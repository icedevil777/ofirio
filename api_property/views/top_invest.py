from ofirio_common.enums import EsIndex
from ofirio_common.helpers import get_elastic_search
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from elasticsearch.exceptions import NotFoundError as ESNotFoundError

from api_property.common.card import make_prop_card_es


class TopInvestView(APIView):
    def get(self, request, *args, **kwargs):
        elastic = get_elastic_search()
        body = {
            "size": 8,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"is_high_cap_rate": False}},
                        {"term": {"is_rehab": False}},
                        {"term": {"is_55_plus": False}},
                        {"range": {"price": {"gte": 10000}}},
                        {"range": {"cap_rate": {"gte": 0.06}}},
                        {
                            "script": {
                                "script": {
                                    "source": "doc['previews'].size() > 0",
                                    "lang": "painless",
                                }
                            }
                        },
                    ],
                    "should": [],
                    "minimum_should_match": 0,
                }
            },
        }
        try:
            response = elastic.search(body=body, index=EsIndex.SEARCH_INVEST)
        except ESNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if response_ := response.get("hits").get("hits"):
            top_cap_rate_props = [i.get("_source") for i in response_]
        else:
            data = {
                "server message": "At the moment we do not have top cap rate properties"
            }
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)

        return Response(
            [make_prop_card_es("invest", x) for x in top_cap_rate_props],
            status=status.HTTP_200_OK,
        )
