import re
import json

from django.conf import settings
from django.contrib import messages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from bs4 import BeautifulSoup
from ofirio_common.states_constants import states_from_short

from common.cache import cache_for_timeout
from common.utils import get_msg_json, get_pg_connection
from search.seo.sql import get_seo_table
from search.serializers import SitemapSerializer

SECTIONS = ('buy', 'buildings')
if settings.INVEST_ENABLED:
    SECTIONS += ('invest',)


class HtmlSitemap(APIView):
    """
    Return indexable search pages urls for state + city for HTML sitemap.
    Can also return list of all indexable states and cities.
    Urls are retrieved from XML sitemaps.
    To test api locally, run first:
        mkdir -p static_django/sitemaps-srp; python manage.py gen_xml_srp_sitemaps --no_socket
    """
    serializer_class = SitemapSerializer

    @cache_for_timeout(60 * 60 * 12)
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            messages.error(request, 'Error! invalid query')
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        state_id = serializer.data['state_id']
        city = serializer.data['city']
        if not state_id and city:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        seo_table = get_seo_table()
        if not state_id and not city:
            # return all indexable states
            conn = get_pg_connection(app_name='api html sitemap')
            cursor = conn.cursor()
            sql = f"""
                select distinct state_id
                from {seo_table} seo
                where indexable and state_id != 'PR' and city <> ''
            """
            cursor.execute(sql)
            res = cursor.fetchall()
            conn.close()
            return Response(
                sorted(states_from_short.get(x[0]) for x in res),
                status=status.HTTP_200_OK
            )

        if state_id and not city:
            # return all indexable cities for state
            conn = get_pg_connection(app_name='api html sitemap')
            cursor = conn.cursor()
            sql = f"""
                select distinct city_original
                from {seo_table} seo
                where indexable and state_id = %(state_id)s
            """
            cursor.execute(sql, {'state_id': state_id.upper()})
            res = cursor.fetchall()
            conn.close()
            return Response(
                sorted(x[0] for x in res if x[0]),
                status=status.HTTP_200_OK
            )

        link_pattern = re.compile(f'/{state_id}/{city}($|/)')
        links = {}
        state_id = state_id.lower()
        for section in SECTIONS:
            path = settings.BASE_DIR / f'data/html-sitemap/{state_id}/{section}-{city}.txt'
            if path.is_file():
                with open(path, 'r') as f:
                    if section == 'buildings':
                        links[section] = json.load(f)
                    else:
                        links[section] = sorted(x.strip() for x in f.readlines())

        return Response(links, status=status.HTTP_200_OK)
