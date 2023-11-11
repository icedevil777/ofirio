import json
import httplib2

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

    def add_arguments(self, parser):
        parser.add_argument('--no_socket', '--no_socket', action='store_true')
        parser.add_argument('--dry_run', '--dry_run', action='store_true')

    def get_url_from_socket(self, state_id, section, place_type, place, prop_type=None, facet=None):
        location = {"state_id": state_id, place_type: place}
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
            return bytes(json.dumps(['/' + section + '/' + state_id.lower() +
                                     (('/' + place) if place else '') +
                                     (('/' + facet) if facet else '')]).encode())

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
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"""
            select id, section, state_id, city, county, zip, prop_type, facet
            from {self.seo_table}
            where indexable and not in_google_index
            order by prop_count desc
            limit 1000
        """)
        links = []
        for row in cursor.fetchall():
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
            links.append((row['id'], url))
        return links

    def send_to_google(self, idx, pk, link):
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        body = {'url': json.loads(link)[0], 'type': "URL_UPDATED"}
        if self.dry_run:
            self.log(f'[{idx}] sent', body)
            return True

        response, content = self.http.request(endpoint, method="POST", body=json.dumps(body))
        self.log(f'[{idx}] sent', body)
        self.log(f'[{idx}] got', content)
        result = json.loads(content.decode())
        # For debug purpose only
        if "error" in result:
            self.log(
                "Error({} - {}): {}".format(
                    result["error"]["code"],
                    result["error"]["status"],
                    result["error"]["message"]
                )
            )
            return False

        self.log("urlNotificationMetadata.url: {}".format(result["urlNotificationMetadata"]["url"]))
        self.log("urlNotificationMetadata.latestUpdate.url: {}".format(
            result["urlNotificationMetadata"]["latestUpdate"]["url"]))
        self.log("urlNotificationMetadata.latestUpdate.type: {}".format(
            result["urlNotificationMetadata"]["latestUpdate"]["type"]))
        self.log("urlNotificationMetadata.latestUpdate.notifyTime: {}".format(
            result["urlNotificationMetadata"]["latestUpdate"]["notifyTime"]))
        cursor = self.conn.cursor()
        cursor.execute(f"""
            update {self.seo_table}
            set
                in_google_index = true, 
                google_index_ts = current_timestamp at time zone 'utc'
            where id = %(id)s
        """, {'id': pk})
        self.conn.commit()
        return True

    def handle(self, *args, **options):
        self.no_socket = options['no_socket'] or False
        self.dry_run = options['dry_run'] or False
        scopes = ["https://www.googleapis.com/auth/indexing"]
        json_key = settings.BASE_DIR / 'data' / 'creds' / 'google_index_api_creds.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scopes=scopes)
        self.http = credentials.authorize(httplib2.Http())
        if self.dry_run:
            self.log('NOT really sending to google')
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
        links = self.get_seo_links()
        for idx, (pk, link) in enumerate(links):
            resp = self.send_to_google(idx, pk, link)
            if not resp:
                # looks like we hit a limit
                break
