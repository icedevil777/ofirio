import math

import psycopg2
from django.conf import settings
from ofirio_common.states_constants import states_from_short

from search.seo.sitemaps import gen_prop_sitemap, gen_indexsitemap
from common.base_urlgen_command import BaseUrlgenCommand
from common.utils import get_is_test_condition, get_pg_connection


class Command(BaseUrlgenCommand):
    '''
        creates sitemaps with links to all listings that we have in prop_cache table.
        generates xml files named like this:
            sitemap-ads-fl.xml
            sitemap-ads-fl-1.xml
            sitemap-ads-fl-2.xml
            sitemap-ads-rent-fl.xml
            sitemap-ads-rent-fl-1.xml
    '''
    props_per_page = 30000
    buf_size = 1024 * 16
    chunk_size = 1000
    ads_sitemap_dir = settings.BASE_DIR / 'static_django' / 'sitemaps-ads'

    def _handle(self, *args, **options):
        self.conn = get_pg_connection(app_name='gen_prop_sitemaps')
        sitemaps = []
        for state_id in ['FL']:
            groupped_urls = self.process_state(state_id)
            for group, items in groupped_urls.items():
                filename = f'sitemap-ads-{group}.xml'
                if not items:
                    path = self.ads_sitemap_dir / filename
                    if path.is_file():
                        print('remove obsolete file', path)
                        path.unlink()
                    continue
                gen_prop_sitemap(items, filename)
                sitemaps.append(filename)
        self.conn.close()
        gen_indexsitemap(sitemaps, self.ads_sitemap_dir/'sitemap-ads.xml')

    def get_properties(self, state_id, prop_class):
        ''' get all properties from prop_cache for specified state and prop class '''
        query = f'''
            select p.prop_id,
                   p.status,
                   p.data,
                   p.address ->> 'line' address_line,
                   p.address ->> 'city' address_city,
                   p.address ->> 'state_code' address_state_code,
                   p.address ->> 'zip' address_zip,
                   p.update_date::text update_date
            from prop_cache p
            join canonicalized_props c using(prop_id)
            join prop_photos pp on p.real_prop_id = pp.prop_id
            where p.prop_class = %(prop_class)s
              and p.state_id = %(state_id)s
              and p.status in ('for_sale', 'for_rent', 'under_contract')
              and pp.photos != '[]'
              and p.data ->> 'description' is not null
              and p.data ->> 'description' != ''
              {get_is_test_condition(table_alias='p')}
            order by p.prop_id
        '''
        with self.conn.cursor(
                name='cursor_for_prop_sitemap',
                cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.itersize = self.chunk_size
            cursor.execute(query, {'state_id': state_id, 'prop_class': prop_class})
            while chunk := cursor.fetchmany(self.chunk_size):
                yield chunk
        self.conn.commit()

    def add_pagination(self, urls):
        '''
            split large lists of urls to paginated groups, like
                ca -> ca-1, ca-2, ca-3, ...
                rent-ca -> rent-ca-1, rent-ca-2, rent-ca-3, ...
        '''
        if not any(urls.values()):
            return {}
        paginated = {}
        for prop_class_prefix, prop_class_urls in urls.items():
            page_count = math.ceil(len(prop_class_urls) / self.props_per_page)
            for i in range(page_count):
                suffix = f'-{i+1}'
                paginated[prop_class_prefix + suffix] = prop_class_urls[i * self.props_per_page : (i + 1) * self.props_per_page]
        return paginated

    def process_state(self, state_id):
        '''
        generates dict with paginated lists of property urls for single state, example:
            {'ca': [...],   'rent-ca': [...],
             'ca-1': [...], 'rent-ca-1': [...],
             'ca-2': [...], 'rent-ca-2': [...]}
        '''
        urls = {}
        urls[state_id.lower()] = self.process_state_with_prop_class(state_id, 'sales')
        # OT-2900 rent section is currently disable
        # urls['rent-' + state_id.lower()] = self.process_state_with_prop_class(state_id, 'rent')
        paginated = self.add_pagination(urls)
        return paginated

    def process_state_with_prop_class(self, state_id, prop_class):
        ''' returns list of property urls for given state and prop_class '''
        print('=======', state_id, prop_class, '========')
        i = 0
        listings = []
        last_mods = []
        prop_ids = []
        for chunk in self.get_properties(state_id, prop_class):
            #print(f'chunk #{i}')
            listings_chunk = self.convert_to_urls(chunk)
            listings.extend(listings_chunk)
            last_mod = [item['update_date'][:10] for item in chunk]
            last_mods.extend(last_mod)
            prop_id = [item['prop_id'] for item in chunk]
            prop_ids.extend(prop_id)
            i += 1
        if len(listings):
            print(f'{state_id}: converted {len(listings)} properties')

        urls = []
        for prop_id, last_mod, url in zip(prop_ids, last_mods, listings):
            urls.append((last_mod, url))
        return urls
