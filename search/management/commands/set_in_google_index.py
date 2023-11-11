import json
import time
import httplib2

import pandas as pd
from django.conf import settings
from psycopg2.extras import RealDictCursor
from oauth2client.service_account import ServiceAccountCredentials

from common.management import OfirioCommand
from common.utils import get_pg_connection
from search.seo.sitemaps import init_socket
from search.seo.sql import get_seo_table
from search.seo.constants import SRP_SECTION_TO_PROP_CLASS
from search.constants import PROP_TYPE_FRONTEND_REVERSE_MAPPING


class Command(OfirioCommand):
    """
    This command was used only once to mark some records
    in seo_links table as already indexed by google
    """
    def add_arguments(self, parser):
        parser.add_argument('--no_socket', '--no_socket', action='store_true')

    def get_url_from_socket(self, state_id, section, place_type, place, prop_type=None, facet=None):
        location = {"state_id": state_id, place_type: place}
        snapshot = {}
        prop_class = SRP_SECTION_TO_PROP_CLASS[section]
        if prop_type:
            snapshot["cleaned_prop_type"] = [
                PROP_TYPE_FRONTEND_REVERSE_MAPPING[prop_class].get(prop_type)
            ]

        if facet:
            if 'beds' in facet:
                snapshot["beds_exact"] = facet[0]
            elif 'under' in facet:
                snapshot['price_max'] = int(facet[6:])
            else:
                snapshot["amenities"] = facet
        sock_str = [{"generator": "search",
                     "location": location,
                     "snapshot": snapshot,
                     "type": section}]

        if self.no_socket:
            # just return approximate link
            return bytes(json.dumps(
                ['https://ofirio.com/' +
                 section +
                 '/' +
                 state_id.lower() +
                 (('/' + place) if place else '') +
                 (('/' + facet) if facet else '')]
            ).encode())

        self.socket.send(bytes(json.dumps(sock_str).encode("utf-8")))
        self.socket.send(b"end")
        return self.socket.recv(1024)

    def get_place_type(self, res):
        if res['zip']:
            return 'zip'
        if res['city']:
            return 'city'
        if res['county']:
            return 'county'

    def get_seo_links(self):
        query = f"""
            select id, section, state_id, city, county, zip, prop_type, facet
            from {self.seo_table}
            where not in_google_index
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            while chunk := cursor.fetchmany(1000):
                self.log(self.checked_count, 'checked')
                links = []
                for row in chunk:
                    place_type = self.get_place_type(row)
                    place = row[place_type] if place_type else None
                    pt = row['prop_type']
                    facet = row['facet']
                    state_id = row['state_id']
                    section = row['section']
                    url = self.get_url_from_socket(
                        state_id, section, place_type=place_type,
                        place=place, prop_type=pt, facet=facet
                    )
                    url = json.loads(url)[0].replace('stage.', '')
                    ts = None
                    if self.from_csv:
                        indexed = url in self.indexed_urls
                        if indexed:
                            ts = self.indexed_urls[url]
                    else:
                        indexed, ts = self.in_google_index(url)
                    self.checked_count += 1
                    if indexed:
                        links.append((row['id'], ts))
                        self.log('+', url, ts)
                yield links
        self.conn.commit()

    def in_google_index(self, url):
        endp = 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect'
        #time.sleep(.5)  # google is slow enough
        self.log('.')
        response, content = self.http.request(
            endp, method="POST",
            body=json.dumps({'inspectionUrl': url, 'siteUrl': 'sc-domain:ofirio.com'})
        )
        result = json.loads(content.decode())
        status = result['inspectionResult']['indexStatusResult']['coverageState']
        ts = None
        if status == 'Submitted and indexed':
            ts = result['inspectionResult']['indexStatusResult']['lastCrawlTime']
            return True, ts
        return False, None

    def set_in_index(self, pk, ts):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            update {self.seo_table}
            set
                in_google_index = true, 
                google_index_ts = %(ts)s
            where id = %(id)s
        """, {'id': pk, 'ts': ts})
        self.conn.commit()
        return True

    def handle(self, *args, **options):
        self.no_socket = options['no_socket'] or False
        scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
        json_key = settings.BASE_DIR / 'data' / 'creds' / 'google_index_api_creds.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scopes=scopes)
        self.http = credentials.authorize(httplib2.Http())
        if self.no_socket:
            self.log('run without socket')
            self._handle(*args, **options)
        else:
            self.socket = init_socket()
            self._handle(*args, **options)
            self.socket.close()

    def _handle(self, *args, **options):
        self.conn = get_pg_connection()
        self.seo_table = get_seo_table()
        self.indexed_urls = {}
        self.from_csv = True
        self.checked_count = 0

        path = settings.BASE_DIR / 'data/google-result.txt'
        df = pd.read_csv(path, delimiter=';')

        for idx, url, ts in df.itertuples():
            self.indexed_urls[url] = pd.to_datetime(ts, format="%d-%m-%Y")

        for links in self.get_seo_links():
            for pk, ts in links:
                self.set_in_index(pk, ts)
