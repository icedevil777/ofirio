from elasticsearch import NotFoundError
from django.utils import timezone
from ofirio_common.enums import EsIndex
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_property.common.card import make_prop_card_es
from api_property.constants import LAST_SEARCH_AUTOCOMPLETE_HIERARCHY, MINIMUM_PROPERTY_COUNT
from api_property.mixins import ElasticSearchMixin, LastSearchESRecommendationMixin
from api_property.serializers import LastSearchPropClassSerializer, PropClassSerializer


class NewListings(ElasticSearchMixin, APIView):
    serializer_class = PropClassSerializer

    ES_BODY = {
        "size": 8,
        "query": {
            "bool": {
                "filter": {
                    "script": {
                        "script": {
                            "source": "doc['previews'].size() > 0",
                            "lang": "painless",
                        }
                    }
                },
                "should": [],
                "must": [
                    {
                        "range": {
                            "list_date": {
                                "gte": (timezone.now() - timezone.timedelta(days=30)).date(),
                                "lte": timezone.now().date()
                            }
                        }
                    }
                ],
                "minimum_should_match": 0,
            }
        },
        "sort": [{"list_date": {"order": "desc"}}],
    }

    def post(self, request, *args, **kwargs):
        index = EsIndex.SEARCH_RENT if self.request.data.get("prop_class") == "rent" else EsIndex.SEARCH_BUY

        try:
            response = self.get_objects(index, es_body=self.get_es_body())
        except NotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if response_ := response.get("hits", {}).get("hits"):
            new_lists = [i.get("_source") for i in response_]
        else:
            data = {"server message": "At the moment we do not new properties"}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)

        return Response(
            [make_prop_card_es(self.request.data.get("prop_class"), x) for x in new_lists],
            status=status.HTTP_200_OK,
        )


class LastSearchNewListings(LastSearchESRecommendationMixin, NewListings):
    serializer_class = LastSearchPropClassSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            last_search_params = serializer.validated_data.get('last_search', {})
            index = (
                EsIndex.SEARCH_RENT
                if serializer.validated_data.get('prop_class') == "rent"
                else EsIndex.SEARCH_BUY
            )
            if last_search_params.get('type') in ('address', 'building'):
                last_search_params['type'] = 'zip'

            ls_type = last_search_params.get('type')
            response, objects = None, None
            while (not response) and ls_type:
                es_body = self.get_es_body(last_search_params)
                last_search_params['type'] = LAST_SEARCH_AUTOCOMPLETE_HIERARCHY.get(ls_type)
                ls_type = last_search_params.get('type')
                try:
                    response = self.get_objects(index, es_body).get("hits", {}).get("hits")
                except NotFoundError:
                    response = []

                objects = [i.get("_source") for i in response]
                if len(objects) < MINIMUM_PROPERTY_COUNT:
                    response = None

            if objects and len(objects) >= MINIMUM_PROPERTY_COUNT:
                return Response(
                    [make_prop_card_es(serializer.validated_data.get('prop_class'), x) for x in objects],
                    status=status.HTTP_200_OK,
                )
        return super().post(request, *args, **kwargs)
