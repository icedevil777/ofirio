import ast
from abc import ABC

from django.contrib.auth import get_user_model
from ofirio_common.helpers import url_to_cdn
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api_property import enums
from api_property.common.common import (is_suitable_prop_class_returned_from_db,
                                        prop_has_invest_view, is_off_market_status,
                                        get_estimated_mortgage, getProp, can_show_property,
                                        get_status_params_for_favorites, cant_show_price_fields,
                                        getPropAddressStr, format_listing_office)

from api_property.common.errors import NoPropertyError
from api_property.common.rebates import get_rebate_for_view
from api_property.constants import SOLD_STATUSES
from api_property.enums import (
    PropClassSimilarChoices, RecommendationsChoices, PropClass,
)

from api_property.models import SimilarPropertyNotificationModel, \
    PropertyUpdateModel, PropCity
from account.models.favorite_property import FavoriteProperty
from common.fields import MultipleChoiceListField, TextInputListField
from common.utils import get_dict_cursor
from ofirio_common.enums import EsIndex


User = get_user_model()


class PropertyIdSerializer(serializers.Serializer):
    prop_id = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.conn = kwargs.pop('conn', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        prop = getProp(attrs['prop_id'], self.conn)
        if not prop:
            raise NoPropertyError
        attrs['prop'] = prop
        return attrs


class PropertyFinanceSerializer(serializers.Serializer):
    prop_id = serializers.CharField(required=True)
    price = serializers.FloatField(default=None, required=False)
    monthly_rent = serializers.IntegerField(default=None, required=False, min_value=1)
    down_payment = serializers.FloatField(default=1, min_value=0.01, max_value=1)
    financing_years = serializers.IntegerField(default=30, min_value=1, max_value=30)
    interest_rate = serializers.FloatField(default=0.05, min_value=0, max_value=1)
    hoa_fees = serializers.FloatField(default=None, required=False)
    insurance = serializers.FloatField(default=None, required=False)
    property_taxes = serializers.FloatField(default=None, required=False)
    annual_increase_rent = serializers.FloatField(default=0.02, min_value=0, max_value=1)
    annual_increase_prop = serializers.FloatField(default=0.02, min_value=0, max_value=1)
    general_inflation = serializers.FloatField(default=0.015, min_value=0, max_value=1)
    average_length_stay_years = serializers.IntegerField(default=2)
    vacancy_per_year_days = serializers.IntegerField(default=15)
    management_fees_percent = serializers.FloatField(default=0.08, min_value=0, max_value=1)
    maintenance_cost_percent = serializers.FloatField(default=0.025, min_value=0, max_value=1)
    maintenance_cost_amount = serializers.FloatField(default=None, min_value=0)
    overhead_cost_percent = serializers.FloatField(default=0.02, min_value=0, max_value=1)
    overhead_cost_amount = serializers.FloatField(default=None)
    closing_cost_on_purchase_percent = serializers.FloatField(default=0.03,
                                                              min_value=0, max_value=1)
    closing_cost_on_sale_percent = serializers.FloatField(default=0.07, min_value=0, max_value=1)
    release_fees_amount = serializers.FloatField(default=None)



class AnalyticsSerializer(serializers.Serializer):
    prop_id = serializers.CharField(required=True)
    agg_type = serializers.ChoiceField(
        required=False,
        choices=enums.AggTypeChoices.choices,
        default='zip')
    prop_class = serializers.ChoiceField(
        required=True,
        choices=enums.PropClassChoices.choices)
    graph_names = MultipleChoiceListField(choices=enums.GraphsChoices.choices,
                                          allow_empty=False, required=True)


class AffordabilitySerializer(serializers.Serializer):
    prop_id = serializers.CharField(required=True, max_length=20)
    price = serializers.FloatField(default=None, min_value=1)
    down_payment = serializers.FloatField(default=0.2, min_value=0.02, max_value=1)
    interest_rate = serializers.FloatField(default=0.05, min_value=0, max_value=1)
    loan_type = serializers.ChoiceField(default=30, choices=((15, 15), (20, 20), (30, 30)))
    monthly_insurance = serializers.FloatField(default=None, min_value=0)
    prop_tax_est = serializers.FloatField(default=None, min_value=0)
    monthly_hoa = serializers.FloatField(default=None, min_value=0)

    monthly_rent = serializers.HiddenField(default=None)
    annual_increase_rent = serializers.HiddenField(default=0.02)
    annual_increase_prop = serializers.HiddenField(default=0.02)
    general_inflation = serializers.HiddenField(default=0.015)
    average_length_stay_years = serializers.HiddenField(default=2)
    vacancy_per_year_days = serializers.HiddenField(default=15)
    management_fees_percent = serializers.HiddenField(default=0.08)
    maintenance_cost_percent = serializers.HiddenField(default=0.025)
    maintenance_cost_amount = serializers.HiddenField(default=None)
    overhead_cost_percent = serializers.HiddenField(default=0.02)
    overhead_cost_amount = serializers.HiddenField(default=None)
    closing_cost_on_purchase_percent = serializers.HiddenField(default=0.03)
    closing_cost_on_sale_percent = serializers.HiddenField(default=0.07)
    release_fees_amount = serializers.HiddenField(default=None)


class RecentlyViewedSerializer(serializers.Serializer):
    prop_class = serializers.ChoiceField(choices=RecommendationsChoices.choices, required=True)
    prop_ids = TextInputListField(child=serializers.CharField(required=True))


class RecommendationsSerializer(serializers.Serializer):
    prop_id = serializers.CharField(required=True)
    section = serializers.ChoiceField(
        choices=RecommendationsChoices.choices, required=True)


class PropCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = PropCity
        fields = ('city', 'county', 'state_id', 'label')

    def create(self, validated_data):
        """
        Don't create if already exists (do not consider 'label')
        """
        instance = PropCity.objects.filter(
            city=validated_data['city'],
            county=validated_data['county'],
            state_id=validated_data['state_id'],
        ).first()
        if not instance:
            instance = super().create(validated_data)
        return instance


class PropCitiesField(TextInputListField):
    child = PropCitySerializer()

    def to_internal_value(self, data):
        cities = []

        for city in data:
            if isinstance(city, str):  # for tests
                try:
                    city = ast.literal_eval(city)
                except Exception:
                    raise ValidationError('Failed to recognize the city')

            serializer = PropCitySerializer(data=city)
            serializer.is_valid(raise_exception=True)
            prop_city = serializer.create(serializer.validated_data)
            cities.append(prop_city)

        return cities

    def to_representation(self, objects):
        """To replace objects with objects.all()"""
        return super().to_representation(objects.all())


class EmailPreferenceCommonListSerializer(serializers.ListSerializer, ABC):

    @staticmethod
    def prepare_to_show(props, prop_id_pk_dict: dict):
        prop_ids = list(prop_id_pk_dict.keys())
        new_props = []
        for prop in props:
            if prop['prop_id'] in prop_ids:
                if prop['status'] in SOLD_STATUSES:
                    prop['price'] = prop.pop('close_price')
                if (cash_only := prop['cash_only']) is not None:
                    prop['est_mortgage'] = get_estimated_mortgage(cash_only, prop['est_mortgage'])
                    rebate = get_rebate_for_view(prop['zip'], prop['price'],
                                                 is_off_market_status(prop.pop('status')))
                    if isinstance(rebate, float):
                        rebate = int(rebate)
                    if isinstance(prop['est_mortgage'], float):
                        prop['est_mortgage'] = int(prop['est_mortgage'])
                    prop['rebate'] = rebate
                else:
                    prop.pop('est_mortgage')
                if prop['price_diff']:
                    prop['price_diff'] = 'above' if prop['price_diff'] > 0 else 'bellow'
                prop.pop('cash_only')
                prop.pop('zip')
                prop['photo'] = url_to_cdn(prop['photo'] or prop['street_view'])
                prop.pop('street_view')
                prop['pk'] = prop_id_pk_dict[prop['prop_id']]
                new_props.append(prop)
        return sorted(new_props, key=lambda x: prop_ids.index(x["prop_id"]))

    def to_representation(self, instance):
        if props := instance:  # case when we return get
            prop_ids = []
            prop_ids_buy = {}
            prop_ids_rent = {}
            prop_ids_invest = {}
            for prop in props:
                prop_id = prop.prop_id
                pk = prop.pk
                prop_ids.append(prop_id)
                to_update = {prop_id: pk}
                if prop.prop_class == PropClass.BUY:
                    prop_ids_buy.update(to_update)
                elif prop.prop_class == PropClass.RENT:
                    prop_ids_rent.update(to_update)
                elif prop.prop_class == PropClass.INVEST:
                    prop_ids_invest.update(to_update)
            prop_ids = tuple(set(prop_ids))


            sql = f'''
                select
                prop.prop_id,
                data -> 'price' as price,
                data -> 'beds' as beds,
                data -> 'baths' as baths,
                data -> 'building_size' as sqft,
                data -> 'estimated_mortgage' as est_mortgage,
                data -> 'diff_params' -> 'price_diff' as price_diff,
                params -> 'is_cash_only' as cash_only,
                params -> 'listing_office' as listing_office,
                status,
                pp.photos-> 0 photo,
                address -> 'full_address' as full_address,
                zip,
                pp.street_view,
                data -> 'close_price' as close_price
                from  prop_cache prop
                join prop_photos pp on prop.real_prop_id = pp.prop_id
                where prop.prop_id in %(prop_ids)s'''
            with get_dict_cursor() as cursor:
                cursor.execute(sql, {'prop_ids': prop_ids})
                if res := cursor.fetchall():
                    data = [{
                        'buy': self.prepare_to_show(res, prop_ids_buy),
                        'invest': self.prepare_to_show(res, prop_ids_invest),
                        'rent': self.prepare_to_show(res, prop_ids_rent)
                    }]
                    return data
        return [{'buy': [], 'invest': [], 'rent': []}]


class FavoriteListSerializer(serializers.ListSerializer, ABC):

    def to_representation(self, instance):
        if props := instance:
            invest_props = []
            buy_props = []
            rent_props = []
            prop_ids = [prop.prop_id for prop in props]
            props_info = get_status_params_for_favorites(prop_ids)
            for prop in props:
                prop_id = prop.prop_id
                status = props_info[prop_id]['status'] if prop_id in props_info else 'removed'
                state = prop.address.split(', ')[-2] if prop.address else ''
                cant_show_price = prop_id not in props_info \
                                  or cant_show_price_fields(status, state)\
                                  or is_off_market_status(status)

                listing_office = None if prop_id not in props_info else format_listing_office(
                    props_info[prop_id]['params'].get('listing_office'), status,
                )
                item = {
                    'prop_id': prop_id,
                    'pk': prop.pk,
                    'is_available': prop_id in props_info,
                    'status': status,
                    'added_time': prop.added_time,
                    'photo1': url_to_cdn(prop.photo1),
                    'address': prop.address,
                    'price': prop.price if not cant_show_price else None,
                    'beds': prop.beds,
                    'baths': prop.baths,
                    'building_size': prop.building_size,
                    'listing_office': listing_office,
                }

                if prop.prop_class == PropClass.INVEST:
                    if can_show_property(prop.user, prop_id) and not cant_show_price:
                        item['cash_on_cash'] = prop.cash_on_cash
                        item['cap_rate'] = prop.cap_rate
                        item['total_return'] = prop.total_return
                        item['estimated_rent'] = prop.estimated_rent
                    else:
                        item['cash_on_cash'] = None
                        item['cap_rate'] = None
                        item['total_return'] = None
                        item['estimated_rent'] = None
                    invest_props.append(item)
                elif prop.prop_class == PropClass.BUY:
                    if not cant_show_price:
                        item['apr_rate'] = prop.apr_rate
                        item['prop_tax_est'] = prop.prop_taxes
                        item['mortgage_est'] = get_estimated_mortgage(
                            props_info[prop_id]['params'].get('is_cash_only', False),
                            prop.estimated_mortgage)
                    else:
                        item['apr_rate'] = None
                        item['prop_tax_est'] = None
                        item['mortgage_est'] = None
                    buy_props.append(item)
                else:
                    item['parking'] = prop.parking
                    item['pets_friendly'] = prop.pet_friendly
                    item['laundry'] = prop.laundry
                    item['furnished'] = prop.furnished
                    rent_props.append(item)
            qty = len(buy_props + invest_props + rent_props)
            data = [{
                'buy': buy_props,
                'invest':invest_props,
                'rent': rent_props,
                'qty': qty

            }]
            return data
        return [{'buy': [], 'invest': [], 'rent': [], 'qty': 0}]


class CommonPropNotificationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        if 'prop' in validated_data:
            validated_data.pop('prop')
        return super().create(validated_data)

    def validate(self, attrs):
        prop_id = attrs.get('prop_id')
        prop_class = attrs.get('prop_class')
        prop = getProp(prop_id)
        self.prop = attrs['prop'] = prop
        user = attrs.get('user')

        if isinstance(prop, dict):
            if not is_suitable_prop_class_returned_from_db(
                    prop['prop_class'],
                    prop_class, prop_has_invest_view(prop)
            ):
                raise ValidationError(
                    f'not correct prop_class "{prop_class}" for prop with '
                    f'prop_class "{prop["prop_class"]}" or this prop has not invest view'
                )
            elif self.Meta.model.objects.filter(prop_class=prop_class, prop_id=prop_id, user=user).exists():
                raise ValidationError(
                    {'server_messages': [
                        {'message': 'You’ve already subscribed for this property!', 'level': 'error'}
                    ]})
        else:
            raise ValidationError({'message': f'There is no property {prop_id}'})
        return attrs


class SimilarPropertyNotificationSerializer(CommonPropNotificationSerializer):
    class Meta:
        model = SimilarPropertyNotificationModel
        fields = 'prop_id', 'prop_class', 'pk', 'user'
        list_serializer_class = EmailPreferenceCommonListSerializer


class PropUpdatesSerializer(CommonPropNotificationSerializer):
    class Meta:
        model = PropertyUpdateModel
        fields = 'prop_id', 'prop_class', 'pk', 'user', 'price', 'status'
        read_only_fields = 'pk', 'price', 'status'
        list_serializer_class = EmailPreferenceCommonListSerializer

    def validate(self, attrs):
        """
        Set fields obtained from prop_cache
        """
        attrs = super().validate(attrs)
        attrs['price'] = int(self.prop['data']['price'])
        attrs['status'] = self.prop['status']
        return attrs


class FavoriteSerializer(CommonPropNotificationSerializer):
    prop_id = serializers.CharField(required=True)
    prop_class = serializers.ChoiceField(choices=PropClass.choices, required=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FavoriteProperty
        fields = 'prop_id', 'prop_class', 'pk', 'user'
        list_serializer_class = FavoriteListSerializer

    def create(self, validated_data):
        prop = validated_data['prop']
        prop_class = validated_data['prop_class']
        photo1 = prop['photos'][0] if prop['photos'] else prop['street_view']
        favorite_kw = {'prop_id': prop['prop_id'],
                       'user': validated_data['user'],
                       'photo1': photo1,
                       'address': getPropAddressStr(prop),
                       'price': prop['data']['price'] if prop['status'] not in SOLD_STATUSES else prop['data'].get('close_price', 0),
                       'beds': prop['data']['beds'],
                       'baths': prop['data']['baths'],
                       'building_size': prop['data']['building_size'],
                       'prop_class': prop_class,
                       'status': prop['status']}
        if prop_class in (PropClass.BUY, PropClass.INVEST) \
                and not is_off_market_status(prop.get('status')):
            favorite_kw['cash_on_cash'] = prop['data'].get('cash_on_cash')
            favorite_kw['cap_rate'] = prop['data'].get('cap_rate')
            favorite_kw['total_return'] = prop['data'].get('total_return')
            favorite_kw['estimated_rent'] = prop['data']['predicted_rent']
            favorite_kw['apr_rate'] = prop['data']['apr_rate']
            favorite_kw['prop_taxes'] = prop['data']['monthly_tax']
            favorite_kw['estimated_mortgage'] = prop['data']['estimated_mortgage']
        else:
            favorite_kw['parking'] = prop['params']['parking']
            favorite_kw['pet_friendly'] = prop['params']['pet_friendly']
            favorite_kw['laundry'] = prop['params'].get('laundry') or False
            favorite_kw['furnished'] = prop['params']['furnished']
        return super().create(favorite_kw)


class PropClassSerializer(serializers.Serializer):
    prop_class = serializers.ChoiceField(choices=[PropClass.BUY], required=False)


class LastSearchSerializer(serializers.Serializer):
    zip = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    county = serializers.CharField(required=False)
    state_id = serializers.CharField(required=False)
    type = serializers.CharField()

    def validate(self, attrs):
        attrs.update({
            'city_url': attrs.get('city'),
            'county_url': attrs.get('county'),
            'state_code': attrs.get('state_id'),
        })
        return attrs


class LastSearchPropClassSerializer(PropClassSerializer):
    last_search = LastSearchSerializer(required=False)
