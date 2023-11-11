import hashlib
import random
import re

from ofirio_common.enums import PropEsIndex, PropClass2
from ofirio_common.states_constants import states_from_short
from ofirio_common.address_util import unurlify
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.cache import cache
import pandas as pd
import numpy as np

from common.utils import zip_to_city
from search.seo.constants import FRONTEND_PROP_TYPE_TO_LONG
from search.constants import (
    PROP_TYPE_FRONTEND_REVERSE_MAPPING, PROP_TYPE_FRONTEND_MAPPING,
)
from search.enums import InsightType
from search.models import SpinTextCache, PlaceStat
from search.seo.text_spin_map import SPIN_TEXTS, CONST_TEXTS
from search.seo.overview import get_overview
from search.seo.ab_excluded import EXCLUDED_FROM_AB_TEST
from search.seo.constants import (
    SECTION_TO_STATUS,
    ES_INDEX_TO_SRP_SECTION,
    SRP_SECTION_TO_PROP_CLASS,
    FACET_BEFORE_PROP_TYPE,
    FACET_AFTER_PROP_TYPE,
    FACET_TO_FRONTEND,
    FRONTEND_PROP_TYPE_TO_LONG,
)


def format_facet(x, num):
    if x == 'condo-apt':
        return strong('condo' if num == 1 else 'condos')
    if x == 'house-duplex':
        return strong('single family home' if num == 1 else 'single family homes')
    if x == 'townhouse':
        return strong('townhome' if num == 1 else 'townhomes')

    if num == 1:
        properties = 'property'
        properties_that_are = 'property that is'
        properties_that_have = 'property that has'
        properties_that_dont_have = "property that doesn't have"
    else: 
        properties = 'properties'
        properties_that_are = 'properties that are'
        properties_that_have = 'properties that have'
        properties_that_dont_have = "properties that don't have"

    if 'under' in x:
        return properties_that_are + ' ' + strong(f'Under ${x[-6:-3]}k')
    if x in ('cheap', 'furnished', 'luxury'):
        return strong(x) + ' ' + properties
    if x == 'no-hoa':
        return properties_that_dont_have + ' ' + strong('HOA')
    if x == '55-community':
        return properties_that_are + ' ' + strong('55+')
    if 'beds' in x:
        return properties_that_have + ' ' + strong(f'{x[0]} bedrooms')

    # "with-pool", "waterfront", "with-basement"
    return properties + ' with ' + strong(x.replace('with-', ''))

def strong(x):
    if isinstance(x, (float, int)):
        x = intcomma(x)
    return f'<strong>{x}</strong>'


class SeoGenerator:
    ''' generate h1, title, description, faq, bottom_text for api search '''

    def __init__(self, serializer, number_search_results=None, insights_data=None):

        # extract data from search serializer
        data = serializer.validated_data
        index = data['index']
        srp_type = data['type']
        prop_types = data['cleaned_prop_type'] or []
        state_id = data['state_id'] or ''
        county = data['county'] or ''
        city = data['city'] or ''
        zip_code = data['zip'] or ''
        facets = data['facets'][:3] if data['facets'] else []
        location = serializer.get_location_str()

        # do mappings
        if insights_data and number_search_results is None:
            number_search_results = insights_data['_total']
        section = ES_INDEX_TO_SRP_SECTION[index]
        prop_type = prop_types[0] if len(prop_types) == 1 else None
        prop_class = SRP_SECTION_TO_PROP_CLASS[section]
        frontend_prop_type = FRONTEND_PROP_TYPE_TO_LONG[prop_class][prop_type].title()
        self.near_me = data['near_me']
        if srp_type == 'geo' or self.near_me:
            # it's near me location
            srp_type = None

        # generate common variables for html templates
        if zip_code and not city:
            city = zip_to_city(zip_code) or ''
        state = states_from_short.get(state_id.upper())

        self.facets = facets
        self.single_facet = facets[0] if len(facets) == 1 else None
        self.frontend_prop_type = frontend_prop_type
        self.prop_status = SECTION_TO_STATUS[section]
        self.insights_data = insights_data
        self.location = location
        self.prop_class = prop_class
        self.prop_type = prop_type
        self.internal_prop_type = (
            PROP_TYPE_FRONTEND_MAPPING[prop_types[0]] if prop_types else None
        )
        self.section = section
        self.srp_type = srp_type
        self.data = data
        self.state_id = state_id
        self.city = city

        # this keys will be used to get personal texts
        self.place_type = '/' + index.replace('search-', '')
        self.place = self.place_type + '/' + state_id
        self.place_type += '/' + (srp_type or '')
        if srp_type == 'city':
            self.place += '/' + city
        elif srp_type == 'county':
            self.place += '/' + county
        elif srp_type == 'zip':
            self.place += '/' + zip_code
        if prop_type:
            self.place += '/' + prop_type
            self.place_type += '/' + prop_type
        if self.single_facet:
            self.place += '/' + self.single_facet
            self.place_type += '/' + self.single_facet
        self.place = self.place.lower()

        city = unurlify(city)
        self.base_params = {
            'number_search_results': number_search_results,
            'location': location,
            'state': state,
            'State': state,
            'state_id': state_id.upper(),
            'county': unurlify(county),
            'city': city,
            'City': city,
            'zip': zip_code,
            'zip_code': zip_code,
        }

    def generalize_facet(self, s):
        ''' 2-bedrooms -> x-bedrooms, under-100500 -> under-x, with-pool -> with-pool '''
        if 'bedroom' in s:
            return 'x-bedrooms'
        if 'under' in s:
            return 'under-x'
        return s

    def unurlify_facet(self, s):
        ''' pet-friendly -> Pet Friendly, under-1500 -> Under $1500 '''
        if s in FACET_TO_FRONTEND:
            return FACET_TO_FRONTEND[s]

        # values for a/b text:
        if s == 'condo-apt':
            return 'Condos'
        if s == 'house-duplex':
            return 'Single Family Homes'
        if s == 'townhouse':
            return 'Townhomes'

        return (s
            .replace('0-bedrooms', 'studio')
            .replace('bedrooms', 'bedroom')
            .replace('with-', '')
            .replace('under-', 'under-$')
            .replace('-', ' ')
            .title()
        )

    @property
    def prop_type_with_facets(self):
        prop_type = self.frontend_prop_type
        if not self.facets:
            return prop_type

        facets_before = []
        facets_after = []
        prefix = ''
        suffix = ''
        under_x = ''

        for facet in self.facets:
            term = self.generalize_facet(facet)
            if term == 'under-x':
                under_x = ' ' + self.unurlify_facet(facet)
            elif term in FACET_BEFORE_PROP_TYPE:
                facets_before.append(self.unurlify_facet(facet))
            elif term in FACET_AFTER_PROP_TYPE:
                facets_after.append(self.unurlify_facet(facet))

        prefix = ' '.join(facets_before)
        if prefix:
            prefix += ' '

        if len(facets_after) == 3:
            suffix = '{}, {} and {}'.format(*facets_after)
        else:
            suffix = ' and '.join(facets_after)
        if suffix:
            suffix = ' ' + suffix
        return prefix + prop_type + under_x + suffix

    def clean_whitespace(self, s):
        return (re.sub('\s+', ' ', s)
            .strip()
            .replace('\n', '')
        )

    @property
    def text_key(self) -> str:
        """
        combination of main search parameters which is used to cache
        spin variables avg_price & min_price + for creating random seed
        """
        return '-'.join(map(str, [
            self.section, self.frontend_prop_type, self.location, self.single_facet,
        ])).lower()

    @property
    def random_seed(self) -> int:
        """
        is used for bottom_text to be the same for the same page,
        and to be different for different pages
        """
        return int(hashlib.md5(self.text_key.encode()).hexdigest()[:8], 16)

    @property
    def number_vars(self) -> dict:
        '''
        Cache values of min_price, avg_price & number_search_results vars.
        Number variables should not be changed when data is changed in search results.
        Lookup values in cache, cache if not found
        '''
        key = self.text_key

        entry, created = SpinTextCache.objects.get_or_create(text_key=key)
        if created or entry is None or entry.variables is None:
            if graph := self.insights_data.get(InsightType.ASKING_PRICE):
                min_price = graph['meta']['min']
                avg_price = graph['meta']['average']
            else:
                min_price = avg_price = None
            number_search_results = self.base_params['number_search_results']
            res = {
                'min_price': min_price,
                'avg_price': avg_price,
                'number_search_results': number_search_results,
            }
            entry.variables = res
            entry.save()
        else:
            min_price = entry.variables['min_price']
            avg_price = entry.variables['avg_price']
            number_search_results = entry.variables['number_search_results']
        res = {
            'min_price': '$' + intcomma(min_price or 0),
            'avg_price': '$' + intcomma(avg_price or 0),
            'number_search_results': number_search_results,
        }
        res['__failed_to_get_place_stat'] = False
        try:
            if self.srp_type == 'city' and self.single_facet == 'cheap':
                obj = PlaceStat.objects.get(place=f'{self.state_id}/{self.city}'.lower())
                res.update(obj.data)
                if res['cheap_homes_total'] > 20:
                    res['options_limited_abundant'] = 'widely abundant'
                else:
                    res['options_limited_abundant'] = 'somewhat limited'
                text_100 = "There are {homes_under_100k_total} homes priced under $100K on the market - of those {homes_under_100k_30_days} were added to Ofirio in {city}, {state} in the last 30 days."
                text_200 = "There are {homes_under_200k_total} homes under $200K in {city} - of which {homes_under_200k_30_days} were added in the last 30 days."
                text_300 = "There are {homes_under_300k_total} homes under $300K that are available for homebuyers to consider - of which {homes_under_300k_30_days} were added in the last 30 days."
                if res['homes_under_300k_30_days']:
                    txt = random.choice([text_100, text_200, text_300])
                elif res['homes_under_200k_30_days']:
                    txt = random.choice([text_100, text_200])
                elif res['homes_under_100k_30_days']:
                    txt = text_100
                else:
                    txt = ''
                res['there_are_homes_under'] = txt.format(**{**res, **self.base_params})

                if res['cheap_dom_avg_3']:
                    res['avg_days_on_market'] = res['cheap_dom_avg_3']
                elif res['cheap_dom_avg_6']:
                    res['avg_days_on_market'] = res['cheap_dom_avg_6']
                elif res['cheap_dom_avg_12']:
                    res['avg_days_on_market'] = res['cheap_dom_avg_12']
                else:
                    # I hope it won't happen
                    res['avg_days_on_market'] = 42

                if res['avg_days_on_market'] > 75:
                    res['sale_speed'] = 'slowly'
                elif res['avg_days_on_market'] < 35:
                    res['sale_speed'] = 'quickly'
                else:
                    res['sale_speed'] = 'average speed'

                if not res['sold_prev_month']:
                    # I hope it won't happen
                    res['demand_percent'] = 42
                else:
                    res['demand_percent'] = int(100 * (res['sold_this_month'] - res['sold_prev_month']) / res['sold_prev_month'])
                if res['demand_percent'] > 0:
                    res['demand_rising_declining'] = 'rising'
                else:
                    res['demand_rising_declining'] = 'declining'
                res['demand_percent'] = str(abs(res['demand_percent'])) + '%'
        except PlaceStat.DoesNotExist:
            res['__failed_to_get_place_stat'] = True
        return res

    def select_synonyms(self, text:str) -> str:
        '''find pattern (word1,word2,word3) and replace randomly with one of words'''
        return re.sub(
            '\(.*?\)',
            lambda m: random.choice(
                m.group(0)[1:-1].split(',')  # split synonyms inside ()
            ).strip(),
            text
        )

    def prepare_faq(self, faq:list, params:dict, synonyms:bool) -> list:
        '''format is described in OT-2669'''
        res = []
        for question, answer in faq:
            res.append({
                'question': question,
                'answer': self.prepare_html(answer, params, synonyms),
            })
        return res

    def prepare_html(self, text:str, params:dict, synonyms:bool) -> str:
        '''remove redundant whitespace, apply params, fix markdown'''
        text = self.clean_whitespace(text.format(**params)).replace('> <', '><')
        if synonyms:
            text = self.select_synonyms(text)
        return text

    def get_ab_cities(self):
        '''
        Get and cache csv with list price to close price coefficients.
        Used for A/B testing of bottom_text
        '''
        if not cache.get('seo_bottom_ab'):
            df = (pd
                .read_csv(settings.BASE_DIR / 'data' / 'seo_cities_ab.csv')
                .replace(np.nan, None)
                .groupby(['state', 'city'], as_index=True)
                .apply(lambda x: dict(zip(x.facet, x.coefficient)))
            )
            # OT-3182
            df = df[~df.index.map(lambda idx: idx[0].lower() + '-' + idx[1]).isin(EXCLUDED_FROM_AB_TEST)]
            cache.set('seo_bottom_ab', df.to_dict(), None)
        return cache.get('seo_bottom_ab')

    def ab_new_props_by_afford(self, new_params) -> str:
        if new_params['new_num'] == 1:
            properties = 'property'
            have = 'has'
        else: 
            properties = 'properties'
            have = 'have'
        new_txt = '''
            <p>''' + strong(new_params['new_num']) + ''' new real estate '''+properties+''' in {city}, {State} '''+have+''' been added to Ofirio in the last <strong>7</strong> days.</p>
            <p>Of those new properties:</p>
            <ul>
        '''
        for facet in ('under-100000', 'under-200000', 'under-300000', 'luxury'):
            new_num = new_params.get(f'new_{facet}', 0)
            total_num = new_params.get(f'total_{facet}', 0)

            if new_num == 1:
                properties = 'property'
                were = ' was'
            else: 
                properties = 'properties'
                were = ' were'
            if 'under' in facet:
                txt = properties + ' under ' + strong(f'${facet[-6:-3]}k') + were
            else:
                txt = strong('luxury') + ' ' + properties + were
            if total_num == 1:
                are = 'is'
            else: 
                are = 'are'
            new_txt += f'''
                <li>{strong(new_num)}&nbsp;{txt} added. In total there '''+are+f''' {strong(total_num)} available for sale.</li>
            '''
        return new_txt + '</ul>'

    def ab_biggest_price_change(self, params) -> str:
        if not params:
            return ''

        facet_price_change = intcomma(params['facet_price_change'])
        most_changed_facet = self.unurlify_facet(params['most_changed_facet'])
        facet_price_change_perc = max(1, params['facet_price_change_perc'])
        more_less = params['facet_price_change_more_less']
        return f'''
            <p>The biggest change in price is in the <strong>{most_changed_facet}</strong> segment and it is <strong>{facet_price_change_perc}% (${facet_price_change})</strong> {more_less} than the week prior.</p>
        '''

    def ab_get_facets_txt(self, facets):
        if not facets:
            return ''

        facets_enum = ''.join(f'<li>{strong(num)} new {format_facet(facet, num)}</li>' for num, facet in facets)
        return '''
        <p>This week the following real estate properties became available for sale:</p>
        <ul>
        ''' + facets_enum + '</ul>'

    def find_other_price(self, coef) -> tuple:
        for facet in ('under-200000', 'under-300000'):
            if coef.get(facet) is not None:
                return facet[-6:-3], coef.get(facet)
        # should never happen:
        return None, None

    def bottom_text_ab(self, coef) -> str:
        '''
        quick and dirty a/b test for bottom text generation
        '''
        result = ''

        key = f'bottom-text-ab-test-{self.state_id}-{self.city}'.lower()
        variables = SpinTextCache.objects.get(text_key=key).variables

        h2 = '<h2>Current live statistics for homes in {city}, {state}</h2>'
        new_txt = self.ab_new_props_by_afford(variables.get('new_price_stat'))

        main_coef = coef[None]
        demand = 'high' if main_coef > 0 else ('low' if main_coef < 0 else 'normal')
        close_price_higher_lower = 'higher than' if main_coef > 0 else ('lower than' if main_coef < 0 else 'the same as')
        if main_coef:
            close_price_higher_lower = strong(str(int(round(max(1, 100*abs(main_coef))))) + '%') + ' ' + close_price_higher_lower 
        params = {
            'demand': demand,
            'close_price_higher_lower': close_price_higher_lower,
            'avg_dom': strong(variables['avg_dom']),
        }
        demand_txt = '''
        <p>{city}, {State} has a {demand} demand for real estate. This is determined by the difference between the list price and the closed price, which on average is {close_price_higher_lower} than the list price.
        '''

        try:
            luxury_coef = coef['luxury']
            price, price_coef = self.find_other_price(coef)
            higher_lower = 'higher' if luxury_coef > price_coef else 'lower'
            demand_diff = strong(str(int(round(max(1, 100*abs(luxury_coef - price_coef))))) + '%')
            price_under = strong(f'“Under ${price}k”')
            luxury_txt = f'''
            The demand for <strong>luxury</strong> real estate is {higher_lower} than the demand for {price_under} real estate by {demand_diff}.
            '''
        except:
            luxury_txt = ''

        dom_txt = '''
        Homes in {city}, {State} are on the market for {avg_dom} days, on average among all of our listings.</p>
        '''
        facets_txt = self.ab_get_facets_txt(variables['most_popular_facets'])
        biggest_change_facet_txt = self.ab_biggest_price_change(variables.get('most_changed_facet'))

        if stat := variables.get('list_price_stat'):
            k = stat['this_week'] / stat['prev_week'] - 1
            grown = 'grown' if k > 0 else 'fallen'
            by = max(1, abs(int(round(k * 100))))
            close_price_diff = stat['avg_all'] * (main_coef + 1)
            close_params = {
                'close_price_grown_fallen': grown + ' by ' + strong(str(by) + '%'),
                'close_price_diff': strong(str('$' + intcomma(int(close_price_diff)))),
            }
            close_price_change_txt = '''
            <p>The average closing price for real estate in {city} {State} has {close_price_grown_fallen} from the last week, which amounted to {close_price_diff}.</p>
            '''
        else:
            close_price_change_txt = ''
            close_params = {}

        overview_h2 = '<h2>Monthly Market Overview for houses in {City}, {State}</h2>'
        overview = get_overview({
            'type': 'city',
            'state_id': self.state_id.upper(),
            'city': self.city,
            'index': PropEsIndex.SEARCH_BUY,
        }, self.base_params['number_search_results'])
        if not overview['market_overview']:
            overview_txt = ''
        else:
            overview_txt = ''.join([f'<p>{p}</p>' for p in overview['market_overview']])
        result = (
            h2 + new_txt + demand_txt + luxury_txt + dom_txt + facets_txt +
            biggest_change_facet_txt + close_price_change_txt +
            overview_h2 + overview_txt
        )

        return self.prepare_html(
            result, {**self.base_params, **close_params, **params}, False,
        )

    def generate_bottom_text(self) -> dict:
        ''' generate big block of text on search page '''
        if self.near_me:
            return {
                'bottom_text': None,
                'faq': None,
            }

        text = ''
        try:
            if self.section == 'buy' and self.srp_type == 'city' and not self.facets and not self.internal_prop_type:
                # do not use a/b test when facets exist
                ab = self.get_ab_cities()
                if coef := ab.get((self.state_id.upper(), self.city)):
                    # A/B texts have no FAQ, we should grab it later
                    text = self.bottom_text_ab(coef)
        except SpinTextCache.DoesNotExist:
            pass

        const_content = CONST_TEXTS.get(self.place) or {}
        text = text or const_content.get('text')
        faq = const_content.get('faq') or ''

        spin = False
        # const texts (personalized) have a priority over spin (parametrized random) texts
        if not text:
            text = (SPIN_TEXTS.get(self.place_type) or {}).get('text') or ''
            spin = True

        if spin:
            synonyms = True
            random.seed(self.random_seed)
            params = {
                **self.base_params,
                **self.number_vars,
            }
            if params['__failed_to_get_place_stat']:
                # we failed to get stat for buy/city/cheap page, fallback to buy/city
                text = (SPIN_TEXTS.get(self.place_type.replace('/cheap', '')) or {}).get('text') or ''
        else:
            synonyms = False
            params = {}

        return {
            'bottom_text': self.prepare_html(text, params, synonyms) or None,
            'faq': self.prepare_faq(faq, params={}, synonyms=False) or None,
        }

    def get_tags_schema(self):
        ''' get and cache csv with search params-to-tags mapping '''
        if not cache.get('seo_tags'):
            df = pd.read_csv(settings.BASE_DIR / 'data' / 'seo.csv')
            df.set_index(['section', 'prop_type', 'srp_type'], inplace=True)
            cache.set('seo_tags', df.to_dict(orient='index'), None)
        return cache.get('seo_tags')

    def generate_tags(self) -> dict:
        ''' generate h1, title, description '''
        result = {'title': None, 'description': None, 'h1': None}
        start = self.data['start']
        page = start // 30
        page_suffix = f' - Page {page + 1}' if page else ''
        lower_params = {
            'prop_type': self.prop_type_with_facets.lower(),
            'prop_status': self.prop_status,
        }
        title_params = {
            'prop_type': self.prop_type_with_facets,
            'prop_status': self.prop_status.title(),
        }

        key = (
            self.section,
            self.internal_prop_type or '-',
            self.srp_type or '-',
        )
        tags = self.get_tags_schema()

        if res := tags.get(key):
            result['title'] = self.clean_whitespace(res['title'].format(
                **self.base_params, **title_params
            )) + page_suffix
            result['h1'] = self.clean_whitespace(res['h1'].format(
                **self.base_params, **title_params
            ))
            result['description'] = self.clean_whitespace(res['description'].format(
                **self.base_params, **lower_params
            ))
            if page_suffix:
                if result['description'][-1] == '.':
                    result['description'] = result['description'][:-1]
                result['description'] += page_suffix
            #indexable = res['indexable'] == 'yes'  # not ready yet
        return result
