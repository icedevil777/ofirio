"""
location.raw has the following structure, example:

{'address_components':
   [{'long_name': '2035', 'short_name': '2035', 'types': ['street_number']},
    {'long_name': 'Northeast 151st Street', 'short_name': 'NE 151st St', 'types': ['route']},
    {'long_name': 'North Miami Beach', 'short_name': 'North Miami Beach', 'types': ['locality', 'political']},
    {'long_name': 'Miami-Dade County', 'short_name': 'Miami-Dade County', 'types': ['administrative_area_level_2', 'political']},
    {'long_name': 'Florida', 'short_name': 'FL', 'types': ['administrative_area_level_1', 'political']},
    {'long_name': 'United States', 'short_name': 'US', 'types': ['country', 'political']},
    {'long_name': '33162', 'short_name': '33162', 'types': ['postal_code']}
    ],
'formatted_address': '2035 NE 151st St, North Miami Beach, FL 33162, USA',
'geometry': {'location': {'lat': 25.9152271, 'lng': -80.15931789999999},
            'location_type': 'ROOFTOP',
            'viewport': {'northeast': {'lat': 25.9165760802915, 'lng': -80.15796891970848},
                         'southwest': {'lat': 25.9138781197085, 'lng': -80.1606668802915}}},
            'place_id': 'ChIJ1zqcg5at2YgRSvjGg5veBeE',
            'plus_code': {'compound_code': 'WR8R+37 North Miami Beach, FL, USA', 'global_code': '76QXWR8R+37'},
            'types': ['street_address']}
"""
from django.db import connections
from django.contrib import messages
from ofirio_common.geocode import geocode, get_rect_from_google_location
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import common.tasks as tasks
from common.utils import get_msg_json
from search.serializers import AddressRectSerializer


class AddressRect(APIView):
    """
    Take text query, return rectangle coordinates of the place on map,
    using Google geocoder
    """
    serializer_class = AddressRectSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            messages.error(request, 'Error! Empty query')
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_authenticated:
            tasks.track_search_address.delay(request.user.email, serializer.data)

        query = serializer.data['query']
        cursor = connections['prop_db_rw'].cursor()
        location = geocode(cursor, address=query)

        if not location:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # get State
        # state_name = state_id = zip_code = city = ''
        # for line in location['address_components']:

            # if line['types'] == ['administrative_area_level_1', 'political']:
                # state_name = line['long_name']
                # state_id = line['short_name']

            # if line['types'] == ['postal_code']:
                # zip_code = line['short_name']

            # if line['types'] == ['locality', 'political']:
                # city = line['short_name']

        rect = get_rect_from_google_location(location)
        data = {'geo_rect': ','.join(map(str, rect))}
        return Response(data, status=status.HTTP_200_OK)
