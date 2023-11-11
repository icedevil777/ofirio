from rest_framework.response import Response
from rest_framework.views import APIView

from sale_estimator.serializers import SaleEstimatorSerializer
from sale_estimator.common.model import SaleEstModel
from common.utils import get_pg_connection


class SaleEstimatorView(APIView):
    serializer_class = SaleEstimatorSerializer

    def post(self, request):
        conn = get_pg_connection(app_name="api sale est", db="prop_db_rw")
        serializer = self.serializer_class(data=request.data, conn=conn)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        res = SaleEstModel(conn, data).get_prediction()
        conn.close()
        return Response(res, 200)
