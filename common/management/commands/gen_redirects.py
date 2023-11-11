import psycopg2
import pandas as pd
from django.conf import settings

from common.utils import get_pg_connection
from common.base_urlgen_command import BaseUrlgenCommand


class Command(BaseUrlgenCommand):
    '''
    print set of rules for nginx 301 redirect,
    suitable for /etc/nginx/redirects/portal_redirects.conf
    '''
    def _handle(self, *args, **options):
        self.conn = get_pg_connection()
        self.gen_redirects()
        self.conn.close()

    def get_properties(self, prop_ids):
        query = '''
            select c.prop_id,
                   c.address ->> 'line' address_line,
                   c.address ->> 'city' address_city,
                   c.address ->> 'state_code' address_state_code,
                   c.address ->> 'zip' address_zip
            from prop_cache c
            where prop_id = any(%(prop_ids)s)
        '''
        with self.conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, {'prop_ids': prop_ids})
            res = cursor.fetchall()
        self.conn.commit()
        return res

    def gen_redirects(self):
        '''
        generates list of feed items (dicts)
        '''
        self.stdout.write('create duplicates1 table...')
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute('''
                drop table if exists duplicates1;

                create table duplicates1 as
                select a.prop_id old_prop_id, a.status old_status, a.update_date old_update_date,
                       b.prop_id new_prop_id, b.status new_status, b.update_date new_update_date
                from prop_cache a, prop_cache b
                where (
                    a.update_date < b.update_date or
                    (a.update_date = b.update_date and a.prop_id < b.prop_id)) and
                    a.prop_class = b.prop_class and
                    a.state_id = b.state_id and
                    a.address->>'address_line_norm' is not null and
                    a.address->>'address_line_norm'= b.address->>'address_line_norm' and
                    (a.address->>'city_url' = b.address->>'city_url' or
                     a.zip = b.zip);

                select old_prop_id, old_status, new_prop_id, new_status from duplicates1
            ''')
            df = pd.DataFrame(cursor.fetchall())

        if len(df) == 0:
            self.stdout.write('no duplicates')
            return

        props = self.get_properties(list(df.old_prop_id.values) + list(df.new_prop_id.values))
        urls = self.convert_to_urls(props)
        id_to_url = {url.split('/')[-1] : url[url.find('/p/'):] for url in urls}

        off_market_idx = (df.old_status != 'off_market') & (df.new_status == 'off_market')
        to_delete = list(df[off_market_idx].new_prop_id.values) + list(df[~off_market_idx].old_prop_id.values)
        for row in df[off_market_idx].itertuples():
            self.stdout.write('    {} {};  # {} -> {}'.format(
                id_to_url[row.new_prop_id],
                id_to_url[row.old_prop_id],
                row.new_status, row.old_status,
            ))
        for row in df[~off_market_idx].itertuples():
            self.stdout.write('    {} {};  # {} -> {}'.format(
                id_to_url[row.old_prop_id],
                id_to_url[row.new_prop_id],
                row.old_status, row.new_status,
            ))
        self.stdout.write(str(to_delete))
