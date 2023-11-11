from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import get_pg_connection
from api_property.common.card import make_cards, PROP_CARD_BY_ID_AND_PROP_CLASS_SQL, \
    get_prop_class_from_section
from api_property.serializers import RecentlyViewedSerializer


class RecentlyViewed(APIView):
    serializer_class = RecentlyViewedSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        prop_ids = serializer.data["prop_ids"]
        section = serializer.data["prop_class"]
        if not prop_ids:
            return Response(status=status.HTTP_404_NOT_FOUND)

        with get_pg_connection(app_name='api recently viewed') as conn:
            with conn.cursor() as cursor:
                cursor.execute(PROP_CARD_BY_ID_AND_PROP_CLASS_SQL,
                               {"prop_ids": prop_ids,
                                "prop_class": get_prop_class_from_section(section)})
                res = cursor.fetchall()
        conn.close()
        if not res:
            return Response(status=status.HTTP_404_NOT_FOUND)
        props = make_cards(section, res)

        return Response(
            sorted(props, key=lambda x: prop_ids.index(x["prop_id"])),
            status=status.HTTP_200_OK,
        )
