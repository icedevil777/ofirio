from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ofirio_common.address_util import unurlify

from common.utils import get_pg_connection
from common.states_info import states_info
from search.seo.sql import get_seo_table


class RealEstate(APIView):
    """Api return states info about most popular cities in connected states and photos"""

    def get(self, request, *args, **kwargs):
        section = request.query_params.get("type") or "buy"
        seo_table = get_seo_table()
        SQL = f"""
            SELECT state_id, cat_popular_cities
            FROM {seo_table} seo
            WHERE seo.county = '' AND
                  seo.city = '' AND
                  seo.zip = '' AND
                  seo.prop_type = '' AND
                  seo.facet = '' AND
                  seo.section = %(section)s and
                  seo.state_id != 'PR' and
                  prop_count > 1000
--                we cannot consider Puerto Rico as state in homepage 
                  order by prop_count desc
        """

        with get_pg_connection(app_name="api real_estate") as conn:
            with conn.cursor() as cursor:
                cursor.execute(SQL, {"section": section})
                res = cursor.fetchall()
        conn.close()
        states_photo_dict = {}
        state_cities_dict = {}
        for state_id, cities in res:
            state_name = states_info.get(state_id, {}).get("name")
            photo = states_info.get(state_id, {}).get("photo")
            states_photo_dict[state_name] = photo
            if cities:
                state_cities_dict[state_name] = [unurlify(x) for x in cities.split(",")]

        data = {"states": states_photo_dict, "cities": state_cities_dict}
        return Response(data, status=status.HTTP_200_OK)
