from rest_framework import views, status
from rest_framework.response import Response
import psycopg2.extras
import orjson

from api_property.common.building import (
    get_building,
    get_building_props,
    get_buildings_nearby,
    make_building,
    make_building_cards
)
from common.utils import get_pg_connection

psycopg2.extras.register_default_jsonb(loads=orjson.loads, globally=True)


class BuildingView(views.APIView):

    def get(self, request, *args, **kwargs):
        building_id = request.query_params.get('building_id')

        with get_pg_connection(app_name='api building') as conn:
            building, properties, pois = [], [], []
            if building_id and (building := get_building(conn, building_id)):
                properties = get_building_props(conn, [i['prop_id'] for i in building[7]])
        conn.close()
        if building and properties:
            return Response(make_building(building, properties), status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class BuildingRecommendationsView(views.APIView):

    def get(self, request, *args, **kwargs):
        building_id = request.query_params.get('building_id')

        with get_pg_connection(app_name='api building') as conn:
            similar_buildings = []
            if building_id and (building := get_building(conn, building_id)):
                similar_buildings = get_buildings_nearby(conn, building)
        conn.close()

        if similar_buildings:
            building_cards = make_building_cards(similar_buildings)
            return Response(building_cards, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
