import string
import json
from datetime import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ofirio_common.enums import PropClass2
from ofirio_common.helpers import url_to_cdn
from ofirio_common.address_util import get_building_address, build_address, urlify, get_unit
from ofirio_common.states_constants import states_from_short

import common.tasks as tasks
from account.models import FavoriteProperty
from api_property.common.common import (
    get_is_hidden, clean_data_for_api_property,
    cant_show_price_fields,
    prop_has_invest_view, clean_badges, is_off_market_status
)
from api_property.common.rebates import get_rebate_for_view
from api_property.common.errors import NoPropertyError
from api_property.common.prop_representation import get_prop_type_ui, build_summary
from api_property.serializers import PropertyIdSerializer
from search.seo.linking_widget import get_seo_links_for_listing
from search.constants import PROP_TYPE_FRONTEND_REVERSE_MAPPING
from common.cache import cache_method_unauth
from common.utils import get_pg_connection


class FormatDict(dict):
    '''OT-3105: for partial mapping of disclosure vars'''
    def __missing__(self, key):
        return "{" + key + "}"


class Property(APIView):
    serializer_class = PropertyIdSerializer

    @property
    def overview(self):
        overview = {}
        diff_params = self.prop['data'].get('diff_params') or {}

        if (price_diff := diff_params.get('price_diff')) is not None:
            if price_diff > 0:
                overview['price_diff'] = price_diff, 'above'
            elif price_diff < 0:
                if settings.INVEST_ENABLED:
                    overview['price_diff'] = price_diff, 'below'
                else:
                    overview['price_diff'] = abs(price_diff), 'below'
            else:
                overview['price_diff'] = None, 'Same list price as'

        if (dom_diff := diff_params.get('dom_diff')) is not None:
            dom_diff = max(dom_diff, -0.9)
            if dom_diff <= -0.5:
                overview['dom_diff'] = abs(dom_diff), 'faster'
            elif -0.5 < dom_diff < -0.1:
                overview['dom_diff'] = None, 'faster'
            else:
                overview['dom_diff'] = None, 'slower'

        if (rented_qty := diff_params.get('rented_qty')) is not None:
            overview['rented_qty'] = rented_qty

        if (apr_rate := diff_params.get('apr_rate')) is not None:
            word = 'appreciated' if apr_rate >= 0 else 'depreciated'
            overview['apr_rate'] = abs(apr_rate), word

        return {
            'overview': overview if len(overview) > 1 else None,
        }

    @property
    def canonicalized(self):
        """
        True if property should be indexed by google, false otherwise.
        This is temporary solution to boost google indexing.
        To detect canonicalized properties locally, copy data/canonicalized.csv
        from playground server and run
        `python manage.py rebuild_canonicalized` also on playground
        """
        if (self.prop["data"]["description"] and
                self.prop["photos"] and
                self.prop["status"] in ("for_sale", "for_rent", "under_contract")):
            sql = """
                select prop_id from canonicalized_props
                where prop_id = %(prop_id)s
            """
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, {"prop_id": self.prop_id})
                    if res := cursor.fetchone():
                        return True
                except Exception:
                    self.conn.rollback()
        return False

    @property
    def seo(self):
        canonicalized = self.canonicalized
        if canonicalized:
            seo_links = get_seo_links_for_listing(self.prop, self.has_invest_view)
        else:
            seo_links = None
        return {
            'meta': seo_links,
            'canonicalized': canonicalized,
        }

    @property
    def mls_disclosure(self):
        if self.off_market:
            return {}

        json_date_to_text = json.dumps(self.prop['last_checked'], cls=DjangoJSONEncoder)
        disclosure_vars = {
            'current_date_year': datetime.now().year,
            'listings_last_updated': f'$%{json.loads(json_date_to_text)}$%',
            'site_owner_office': 'Ofirio New York LLC',
            'site_owner_email': 'help@ofirio.com',
        }
        mapping = FormatDict(**disclosure_vars)
        formatter = string.Formatter()
        text = formatter.vformat((self.prop['disclosure_text'] or ''), (), mapping)
        return {
            'mls_logo_url': self.prop['logo_url'],
            'mls_last_checked': self.prop['last_checked'],
            'mls_disclosure_text': text,
        }

    @property
    def price_change_params(self):
        current_price = self.prop['data']['price']
        if (not self.off_market and not self.cant_show_price and
                current_price and
                self.prop['last_price_change'] and
                (price_change_amount := self.prop['last_price_change']['price_changed']) != current_price):
            price_change_diff = price_change_amount / (current_price - price_change_amount)
            price_change_date = self.prop['last_price_change']['date']
        else:
            price_change_amount = None
            price_change_diff = None
            price_change_date = None
        return {
            'price_change_diff': price_change_diff,
            'price_change_date': price_change_date,
            'price_change_amount': price_change_amount,
        }

    @property
    def address(self):
        address = self.prop['address']
        unused_fields = (
            'city_url', 'county_url', 'parcel_number', 'address_line_url',
        )
        [address.pop(field, None) for field in unused_fields]
        address['state'] = states_from_short.get(address['state_code'])
        line = address['line']
        type2 = self.prop['data']['prop_type2']
        address['building_address'] = get_building_address(line, type2)
        address['building_id'] = self.prop['building_id']
        address['unit'] = get_unit(line)
        return {'address': address}

    def search_prop_in_buy(self):
        address = self.prop["address"]
        sql = """
            select prop_id, address
            from prop_cache
            where
                state_id = %(state_id)s and
                address->>'address_line_norm' = %(line)s and
                (zip = %(zip)s or address->>'city_url' = %(city_url)s) and
                prop_class = 'sales'
        """
        params = {
            "state_id": address["state_code"],
            "line": address["address_line_norm"],
            "zip": address["zip"],
            "city_url": address["city_url"],
        }
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            if res := cursor.fetchone():
                return {
                    "prop_id": res[0],
                    "address": res[1],
                }

    def redirect_from_rent(self):
        """
        Privide data for frontend so they can return 301 to user.
        Redirect to the same property in BUY if present,
        otherwise redirect to /buy/state/city search page
        """
        if buy_prop := self.search_prop_in_buy():
            redirect_to = "listing"
            addr = buy_prop["address"]
            address_url = urlify(build_address(
                addr["line"], addr["city"], addr["state_code"], addr["zip"],
            ))
            data = {
                "prop_id": buy_prop["prop_id"],
                "address": address_url,
            }
        else:
            address = self.prop['address']
            redirect_to = "search"
            data = {
                "prop_class": "buy",
                "place_type": "city",
                "state_id": address['state_code'].lower(),
                "city": address['city_url'],
            }
        return Response(
            {"redirect_to": redirect_to, "data": data},
            status=status.HTTP_418_IM_A_TEAPOT,
        )

    @cache_method_unauth
    def post(self, request, *args, **kwargs):

        self.conn = get_pg_connection(app_name='api property')
        serializer = self.serializer_class(data=request.data, conn=self.conn)
        try:
            serializer.is_valid(raise_exception=True)
        except NoPropertyError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        prop_id = serializer.data['prop_id']
        prop = serializer.validated_data['prop']
        self.prop_id = prop_id
        self.prop = prop
        prop_class = prop['prop_class']
        if prop_class == PropClass2.RENT:
            # OT-2900
            return self.redirect_from_rent()

        self.off_market = prop['status'] == 'off_market'
        self.cant_show_price = cant_show_price_fields(
            prop['status'], prop['address']['state_code']
        )
        self.has_invest_view = prop_has_invest_view(prop) and not self.cant_show_price

        # NOTE: when we return back invest we should divide it on buy/invest
        # Check favorite
        user = request.user
        favorite = None
        subscribed_for_similars = False
        subscribed_for_prop_updates = False
        if user.is_authenticated:
            favorite_prop = FavoriteProperty.objects.filter(prop_id__exact=prop_id,
                                                            user=user).first()
            if favorite_prop:
                favorite = favorite_prop.pk
            tasks.track_viewed_property.delay(user.email, prop_id)
            subscribed_for_prop_updates = user.props_updates.filter(prop_id=prop_id).exists()
            subscribed_for_similars = user.similar_props.filter(prop_id=prop_id).exists()

        summary = build_summary(
            prop, prop_class=prop_class, off_market=self.off_market,
            cant_show_price=self.cant_show_price
        )

        if prop['status'] in ('closed', 'sold'):
            prop['data']['price'] = prop['data'].get('close_price', 0)

        prop['data']['prop_type3'] = get_prop_type_ui(prop['data']['prop_type3'])
        cleaned_type = prop['data']['cleaned_prop_type']
        prop['data']['prop_type_search_label'] = PROP_TYPE_FRONTEND_REVERSE_MAPPING[prop_class].get(cleaned_type)

        data = {}
        data.update(self.price_change_params)
        data.update(self.mls_disclosure)
        data.update(self.overview)
        data.update(self.seo)
        data.update(self.address)

        if prop_class == PropClass2.SALES:
            prop['data']['rebate'] = get_rebate_for_view(prop['address']['zip'],
                                                         prop['data']['price'],
                                                         is_off_market_status(prop['status']))
        prop_data = clean_data_for_api_property(
            prop['data'], prop_class, cant_show_price=self.cant_show_price, off_market=self.off_market,
            cash_only=prop['params'].get('is_cash_only')
        )
        prop_data['price_diff'] = (data['overview'] or {}).get('price_diff')
        data.update({
            'prop_id': prop_id,
            'status': prop['status'],
            'badges': clean_badges(prop['badges'], prop['list_date']),
            'list_date': prop['list_date'],
            'update_date': prop['update_date'] if not self.off_market else None,
            'is_hidden': get_is_hidden(prop_id, prop['params']),
            'data': prop_data,
            'photos': url_to_cdn(prop['photos'] or ([prop['street_view']] if prop['street_view'] else [])),
            'summary': summary,
            'features': prop['features'],
            'favorite': favorite,
            'subscribed_for_similars': subscribed_for_similars,
            'subscribed_for_prop_updates': subscribed_for_prop_updates,
            'has_invest_view': self.has_invest_view,
            'off_market': self.off_market,
        })

        self.conn.close()
        return Response(data, status=status.HTTP_200_OK)
