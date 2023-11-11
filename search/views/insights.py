from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common.cache import cache_method_unauth
from search.common import ElasticConstructor, InsightsHandler
from search.seo.generators import SeoGenerator
from search.serializers import InsightsSerializer


class InsightsView(CreateAPIView):
    serializer_class = InsightsSerializer
    permission_classes = AllowAny,

    def get_queryset(self):
        """when elasticsearch is off, AssertionError may occur"""
        pass

    @cache_method_unauth
    def create(self, request, *args, **kwargs):
        """
        Entry point
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        _es_constructor = ElasticConstructor(serializer)
        data = InsightsHandler(_es_constructor).get_insights(
            serializer.validated_data['index'],
            serializer.validated_data['insights'],
        )
        generator = SeoGenerator(serializer, insights_data=data)
        bottom_text = generator.generate_bottom_text()
        data.update(bottom_text)
        return Response(data, status=status.HTTP_200_OK)
