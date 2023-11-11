import json

from ofirio_common.address_util import build_address

from common.management import OfirioCommand
from search.seo.sitemaps import init_socket
from search.seo.constants import SRP_SECTION_TO_PROP_CLASS
from search.constants import PROP_TYPE_FRONTEND_REVERSE_MAPPING


class BaseUrlgenCommand(OfirioCommand):
    '''
    this class contains common methods that are used to communicate with frontend url-generator via socket
    '''
    buf_size = 1024 * 16

    def add_arguments(self, parser):
        parser.add_argument('--no_socket', '--no_socket', action='store_true')

    def handle(self, *args, **options):
        self.no_socket = options['no_socket'] or False
        if self.no_socket:
            self.log('run without socket')
            self._handle(*args, **options)
        else:
            self.socket = init_socket()
            self._handle(*args, **options)
            self.socket.close()

    def gen_search_url(self, state_id, section, place_type, place, prop_type=None, facet=None):
        ''' get search page url '''
        # gen location
        if place_type:
            location = {"state_id": state_id, place_type: place}
        else:
            location = {"state_id": state_id}
        # gen snapshot
        snapshot = {}
        prop_class = SRP_SECTION_TO_PROP_CLASS[section]
        if prop_type:
            snapshot["cleaned_prop_type"] = [PROP_TYPE_FRONTEND_REVERSE_MAPPING[prop_class].get(prop_type)]

        if facet:
            if 'beds' in facet:
                snapshot["beds_exact"] = facet[0]
            elif 'under' in facet:
                snapshot['price_max'] = int(facet[6:])
            else:
                snapshot["amenities"] = facet
        sock_str = [{"generator": "search", "location": location, "snapshot": snapshot, "type": section}]

        if self.no_socket:
            # just return approximate link
            return json.dumps([
                '/' + section + '/' + state_id + (('/' + place) if place else '') +
                (('/' + snapshot["cleaned_prop_type"][0]) if prop_type else '') +
                (('/' + facet) if facet else '')
            ]).lower()

        self.socket.send(bytes(json.dumps(sock_str).encode("utf-8")))
        self.socket.send(b"end")
        return self.socket.recv(1024)

    def to_listing_urlgen(self, chunk):
        ''' 
        converts property info to the list of dicts
        that is acceptable by urlgenerator thas produce property URLs
        '''
        return [{
                "generator": "listing",
                "id": item['prop_id'],
                "address": build_address(
                    item['address_line'], item['address_city'], item['address_state_code'], item['address_zip']
                )}
            for item in chunk]

    def convert_to_urls(self, chunk):
        '''
        accepts list of properties from prop cache and sends them to frontend url-generator via socket.
        returns list of listing urls
        '''
        if self.no_socket:
            # just return list of prop id, not urls
            return ['/p/' + x['prop_id'] for x in chunk]

        to_convert = self.to_listing_urlgen(chunk)

        listings_chunk = None
        for i in range(3):
            try:
                # self.log(f'send {len(to_convert)} properties')
                self.socket.send(bytes(json.dumps(to_convert).encode("utf-8")))
                self.socket.send(b'end')
                listings_data = b''
                while len(data := self.socket.recv(self.buf_size)) == self.buf_size:
                    listings_data += data
                listings_data += data
                listings_chunk = json.loads(listings_data)
                break
            except json.decoder.JSONDecodeError:
                self.log(f'try #{i}: got JSONDecodeError, re-init socket')
                self.socket.close()
                self.socket = init_socket()

        if listings_chunk is None:
            raise Exception('socket error')
        # self.log(f'recv {len(listings_chunk)} properties')
        return listings_chunk
