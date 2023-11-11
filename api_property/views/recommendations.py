from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import get_pg_connection
from api_property.common.errors import NoPropertyError
from api_property.serializers import RecommendationsSerializer
from api_property.common.recommendations import SimilarProps


class Recommendations(APIView):
    serializer_class = RecommendationsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        prop_id = serializer.data['prop_id']
        section = serializer.data.get('section')

        try:
            with get_pg_connection(app_name='api recommendations') as conn:
                with conn.cursor() as cursor:
                    data = SimilarProps(
                        cursor, prop_id, section, user=request.user
                    ).get_recommendations()
        except NoPropertyError:
            message = {'response': f"there is no such property: '{prop_id}'"}
            conn.close()
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        finally:
            conn.close()

        return Response(data, status=status.HTTP_200_OK)
