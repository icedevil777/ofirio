from psycopg2.extras import RealDictCursor
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import get_pg_connection


class LincesesView(APIView):

    def get(self, request, *args, **kwargs):
        SQL = """SELECT state, brokerage, broker_name
                 FROM parsing_mls_realestatelicenses"""

        cursor = get_pg_connection().cursor(cursor_factory=RealDictCursor)
        cursor.execute(SQL)
        res = cursor.fetchall()
        if not res:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(data=res, status=status.HTTP_200_OK)
