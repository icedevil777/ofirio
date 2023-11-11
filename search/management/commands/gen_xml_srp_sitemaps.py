from collections import defaultdict

import psycopg2
from django.conf import settings
from psycopg2.extras import RealDictCursor
from ofirio_common.address_util import build_address, unurlify

from search.seo.sitemaps import gen_srp_sitemap, gen_indexsitemap, gen_html_sitemaps_buildings, gen_html_sitemaps, gen_prop_sitemap
from search.seo.sql import get_seo_table, get_sitemap_links
from common.utils import get_pg_connection
from common.base_urlgen_command import BaseUrlgenCommand

# should rent files be removed from sitemap.xml?
RENT_SHOULD_BE_REMOVED = True
# should rent files be updated daily?
RENT_SHOULD_BE_UPDATED = False


class Command(BaseUrlgenCommand):

    def get_links(self, state_id, res, prop_class, place_field=None, group=False):
        if group:
            links = defaultdict(set)
        else:
            links = set()
        for raw in res:
            place = raw[place_field] if place_field else None
            pt = raw['prop_type']
            facet = raw['facet']
            link = self.gen_search_url(
                state_id, prop_class, place_type=place_field,
                place=place, prop_type=pt, facet=facet
            )
            if group:
                links[place].add(link)
            else:
                links.add(link)
        return links

    def get_state_ids(self):
        # OT-2900: take states with >1k props
        sql_state = f"""
            select distinct state_id
            from {self.seo_table}
            where
                facet = '' and
                prop_type = '' and
                city = '' and
                county = '' and
                zip = '' and
                prop_count > 1000 and
                state_id != 'PR'
        """
        cursor = self.conn.cursor()
        cursor.execute(sql_state)
        res = cursor.fetchall()
        self.state_ids = tuple(raw[0] for raw in res)

    def get_state_buy_links(self):
        links = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'buy', state_id, 'state'):
                links.extend(self.get_links(state_id, res, prop_class='buy'))
        gen_srp_sitemap(links, 'sitemap-buy-state.xml')
        return ['sitemap-buy-state.xml']

    def get_state_invest_links(self):
        links = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'invest', state_id, 'state'):
                links.extend(self.get_links(state_id, res, prop_class='invest'))
        gen_srp_sitemap(links, 'sitemap-invest-state.xml')
        return ['sitemap-invest-state.xml']

    def get_state_rent_links(self):
        if RENT_SHOULD_BE_REMOVED:
            return []
        if RENT_SHOULD_BE_UPDATED:
            links = []
            for state_id in self.state_ids:
                if res := get_sitemap_links(self.cursor, 'rent', state_id, 'state'):
                    links.extend(self.get_links(state_id, res, prop_class='rent'))
            gen_srp_sitemap(links, 'sitemap-rent-state.xml')
        return ['sitemap-rent-state.xml']

    def get_city_buy_links(self):
        sitemaps_names = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'buy', state_id, 'city'):
                links = self.get_links(state_id, res, prop_class='buy', place_field='city', group=True)
                filename = f'sitemap-buy-city-{state_id}.xml'.lower()
                gen_srp_sitemap(sum(map(list, links.values()), []), filename)
                gen_html_sitemaps(state_id, 'buy', links)
                sitemaps_names.append(filename)
        return sitemaps_names

    def get_city_invest_links(self):
        """
        only invest/{state_id}/{city} should be indexable
        """
        sitemaps_names = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'invest', state_id, 'city'):
                links = self.get_links(state_id, res, place_field='city', prop_class='invest', group=True)
                filename = f'sitemap-invest-city-{state_id}.xml'.lower()
                gen_srp_sitemap(sum(map(list, links.values()), []), filename)
                gen_html_sitemaps(state_id, 'invest', links)
                sitemaps_names.append(filename)
        return sitemaps_names

    def get_city_rent_links(self):
        if RENT_SHOULD_BE_REMOVED:
            return []
        sitemaps_names = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'rent', state_id, 'city'):
                links = self.get_links(state_id, res, place_field='city', prop_class='rent', group=True)
                filename = f'sitemap-rent-city-{state_id}.xml'.lower()
                if RENT_SHOULD_BE_UPDATED:
                    gen_srp_sitemap(sum(map(list, links.values()), []), filename)
                    gen_html_sitemaps(state_id, 'rent', links)
                sitemaps_names.append(filename)
        return sitemaps_names

    def get_county_buy_links(self):
        links = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'buy', state_id, 'county'):
                links.extend(self.get_links(state_id, res, place_field='county', prop_class='buy'))
        gen_srp_sitemap(links, 'sitemap-buy-county.xml')
        return ['sitemap-buy-county.xml']

    def get_county_rent_links(self):
        if RENT_SHOULD_BE_REMOVED:
            return []
        if RENT_SHOULD_BE_UPDATED:
            links = []
            for state_id in self.state_ids:
                if res := get_sitemap_links(self.cursor, 'rent', state_id, 'county'):
                    links.extend(self.get_links(state_id, res, place_field='county', prop_class='rent'))
            gen_srp_sitemap(links, 'sitemap-rent-county.xml')
        return ['sitemap-rent-county.xml']

    def get_zip_buy_links(self):
        sitemaps_names = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'buy', state_id, 'zip'):
                links = self.get_links(state_id, res, place_field='zip', prop_class='buy')
                gen_srp_sitemap(links, f'sitemap-buy-zip-{state_id.lower()}.xml')
                sitemaps_names.append(f'sitemap-buy-zip-{state_id.lower()}.xml')
        return sitemaps_names

    def get_zip_rent_links(self):
        if RENT_SHOULD_BE_REMOVED:
            return []
        sitemaps_names = []
        for state_id in self.state_ids:
            if res := get_sitemap_links(self.cursor, 'rent', state_id, 'zip'):
                links = self.get_links(state_id, res, place_field='zip', prop_class='rent')
                if RENT_SHOULD_BE_UPDATED:
                    gen_srp_sitemap(links, f'sitemap-rent-zip-{state_id.lower()}.xml')
                sitemaps_names.append(f'sitemap-rent-zip-{state_id.lower()}.xml')
        return sitemaps_names

    def get_buildings(self):
        '''
        run this if you get 'no such table' error:

                    create table sitemap_buildings as
                    select building_id
                    from buildings
                    where
                        poi_ts is not null and
                        schools is not null
                        and walkscore is not null
                        and photos is not null
                        and photos != '[]'
                    order by active_count desc, sold_count desc
                    limit 2000
        '''
        query = f'''
            select building_id, address, updated_at::text update_date
            from buildings
            join sitemap_buildings using(building_id)
            where state_id = %s
        '''
        sitemaps = []
        for state_id in self.state_ids:
            for_html = defaultdict(list)
            urls = []
            with self.conn.cursor(
                    name='cursor_for_buildings_sitemap',
                    cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, [state_id.lower()])
                while chunk := cursor.fetchmany(1000):
                    for row in chunk:
                        url = settings.PROJECT_SCHEME + settings.PROJECT_DOMAIN + '/b/' + row['building_id']
                        upd = row['update_date'][:10]
                        addr = row['address']
                        city = addr['city']
                        address = build_address(addr['line'], unurlify(addr['city']), addr['state_id'].upper(), addr['zip'])
                        for_html[city].append({
                            'building_id': row['building_id'],
                            'address': address,
                        })
                        urls.append((upd, url))
            if urls:
                filename = f'sitemap-buy-buildings-{state_id.lower()}.xml'
                gen_prop_sitemap(urls, filename, path='srp')
                gen_html_sitemaps_buildings(state_id, 'buildings', for_html)
                sitemaps.append(filename)
            self.conn.commit()
        return sitemaps

    def _handle(self, *args, **options):
        self.conn = get_pg_connection(app_name='gen_xml_srp_sitemaps')
        self.seo_table = get_seo_table()
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.get_state_ids()

        sitemaps = (
            self.get_state_buy_links() +
            self.get_state_rent_links() +
            self.get_city_buy_links() +
            self.get_city_rent_links() +
            self.get_county_buy_links() +
            self.get_county_rent_links() +
            self.get_zip_buy_links() +
            self.get_zip_rent_links() +
            self.get_buildings()
        )
        if settings.INVEST_ENABLED:
            sitemaps += (
                self.get_state_invest_links() +
                self.get_city_invest_links()
            )

        gen_indexsitemap(sitemaps, settings.SITEMAPS_DIR_SRP / 'sitemap.xml')
        self.conn.close()
