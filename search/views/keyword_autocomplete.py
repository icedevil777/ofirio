from django.db import connections
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from search.serializers import KeywordAutocompleteSerializer


class KeywordAutocomplete(CreateAPIView):
    serializer_class = KeywordAutocompleteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        suggestions = []
        with connections['prop_db'].cursor() as cursor:
            sql = """
                SELECT term from
                    (SELECT term, max(count) AS count_max, max(weight) AS weight_max
                     FROM keywords WHERE term LIKE %(prefix)s GROUP BY term) AS keywords_temp
                WHERE count_max > 5 ORDER BY (weight_max, count_max) DESC LIMIT 10;
            """
            cursor.execute(sql, {'prefix': serializer.validated_data['prefix'] + '%'})
            suggestions = [item[0] for item in cursor.fetchall()]

        return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)
