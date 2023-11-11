'''
module has unit tests! see search/tests/test_linking_widget.py to observe examples
of data returned by get_seo_links_for_listing and get_seo_links_from_serializer
'''
from ofirio_common.enums import PropEsIndex, PropClass2
from django.conf import settings

from search.enums import PropType3
from search.constants import PROP_TYPE_FRONTEND_REVERSE_MAPPING, PROP_TYPE_FRONTEND_MAPPING
from search.seo.sql import (
    get_top_buildings,
    get_prop_types,
    get_facets,
    get_nearby_and_popular,
    get_max_prop_count,
    has_invest,
)
from search.seo.constants import (
    ES_INDEX_TO_SRP_SECTION,
    SRP_SECTION_TO_PROP_CLASS,
    FACET_TO_SEO_CAT,
)
from search.seo.enums import SeoCategory
from common.utils import get_dict_cursor


def get_default_facet_cats():
    return {
        SeoCategory.BEDROOMS: [],
        SeoCategory.AMENITIES: [],
        SeoCategory.LIFESTYLE: [],
        SeoCategory.PROP_TYPE: [],
        SeoCategory.AFFORDABILITY: [],
    }


def get_seo_links_for_listing(prop, has_invest_view):
    """
    Return groups of links depending on property class
    (rent for RENT, buy and possibly invest for SALES).
    Links will be displayed on listing page
    """
    prop_class = prop['prop_class']
    if prop_class == PropClass2.RENT:
        seo_links = {PropEsIndex.SEARCH_RENT: {}}
    else:
        seo_links = {PropEsIndex.SEARCH_BUY: {}}
        if has_invest_view:
            seo_links[PropEsIndex.SEARCH_INVEST] = {}
    for seo_section in seo_links:
        if prop_class == PropClass2.RENT:
            prop_types = [prop['data']['cleaned_prop_type'], ]
        else:
            prop_types = []
        seo_links[seo_section].update(get_seo_links(
            seo_section,
            search_prop_types=prop_types,
            state_id=prop['address']['state_code'],
            county='',
            city=prop['address']['city_url'],
            zip_code='',
            srp_type='city',
            api='property',
        ) or {})
    # clean empty sections
    for seo_section in seo_links:
        if not seo_links[seo_section]:
            seo_links[seo_section] = None
    return seo_links


def get_seo_links_from_serializer(search_serializer):
    """
    Return links groupped by categories for SEO link widget.
    Links will be displayed on search page
    """
    data = search_serializer.validated_data
    if data['type'] == 'geo' and not data['near_me']:
        return {}

    index = data['index']
    prop_types = [PROP_TYPE_FRONTEND_MAPPING[t] for t in data['cleaned_prop_type'] or []]
    state_id = data['state_id'] or ''
    county = data['county'] or ''
    city = data['city'] or ''
    zip_code = data['zip'] or ''
    facet = data['facets'][0] if data['facets'] else ''
    user_county = data['user_county']
    srp_type = data['type']
    if data['type'] == 'geo' and data['near_me']:
        srp_type = 'city'

    links = get_seo_links(
        index, prop_types, state_id, county, city, zip_code,
        srp_type=srp_type, search_facet=facet, near_me=data['near_me'],
        user_county=user_county,
    )
    return links


def get_seo_links(search_index, search_prop_types,
                  state_id, county, city, zip_code,
                  srp_type=None, search_facet='',
                  near_me=False, user_county=None, api='search'):

    section = ES_INDEX_TO_SRP_SECTION[search_index]
    prop_type = search_prop_types[0] if search_prop_types else ''
    prop_class = SRP_SECTION_TO_PROP_CLASS[section]
    type_to_label = PROP_TYPE_FRONTEND_REVERSE_MAPPING[prop_class]

    cursor = get_dict_cursor()

    params = {
        'section': section,
        'state_id': state_id.upper(),
        'county': county,
        'city': city,
        'zip_code': zip_code,
        'prop_type': prop_type,
    }

    res = get_default_facet_cats()
    max_prop_count = get_max_prop_count(cursor, params)
    res[SeoCategory.PROP_TYPE] = get_prop_types(
        cursor, params, srp_type, max_prop_count=max_prop_count,
    )

    if section == 'invest':
        # cross-section: insert properties-for-sale links from 'buy' section
        res[SeoCategory.PROP_TYPE] = get_prop_types(
            cursor, {**params, **{'section': 'buy'}}, srp_type
        )
        if res[SeoCategory.PROP_TYPE]:
            res[SeoCategory.PROP_TYPE].append('homes')

    # disabled due to OT-3178
    if 0 and settings.INVEST_ENABLED:
        if section == 'buy' and srp_type not in ('zip', 'county'):
            # cross-section: insert investment properties to buy section
            if has_invest(cursor, params):
                res[SeoCategory.PROP_TYPE].append('invest')

    if section in ('buy', 'rent'):
        if prop_type:
            # add 'homes' if particular prop type is selected
            res[SeoCategory.PROP_TYPE].append('homes')
            # remove the same prop type from linking
            if prop_type in res[SeoCategory.PROP_TYPE]:
                res[SeoCategory.PROP_TYPE].remove(prop_type)

    search_facet = search_facet.replace('bedrooms', 'beds')  # front has bedrooms, db has beds
    facets = get_facets(cursor, params, near_me=near_me, max_prop_count=max_prop_count)
    for _, facet in facets:
        if facet == search_facet:
            # don't add the same page we're on
            continue
        cat = FACET_TO_SEO_CAT[facet]
        if cat in (SeoCategory.AMENITIES, SeoCategory.LIFESTYLE, SeoCategory.AFFORDABILITY):
            # these categories may have prop_type key in addition
            facet = {'value': facet}
        res[cat].append(facet)

    if section == 'rent' and srp_type and srp_type != 'zip' and not prop_type:
        other_cats = {
            PropType3.CONDO_APT: get_default_facet_cats(),
            PropType3.HOUSE_DUPLEX: get_default_facet_cats(),
            PropType3.TOWNHOUSE: get_default_facet_cats(),
        }
        facets = get_facets(cursor, params, all_prop_types=True, near_me=near_me, max_prop_count=max_prop_count)
        for type_, facet in facets:
            cat = FACET_TO_SEO_CAT[facet]
            other_cats[type_][cat].append(facet)

        if srp_type == 'state':
            # create 'Browse apartments by bedrooms' category
            new_beds = override_beds(
                other_cats, type_to_label, (PropType3.CONDO_APT,)
            )
            res.update(new_beds)
            res.pop(SeoCategory.BEDROOMS, None)

            res[SeoCategory.AMENITIES] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.AMENITIES,
                (PropType3.CONDO_APT,),
            )

            res[SeoCategory.AFFORDABILITY] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.AFFORDABILITY,
                (PropType3.CONDO_APT, PropType3.HOUSE_DUPLEX),
            )
        if srp_type == 'city':
            # create 3 categories for bedrooms
            new_beds = override_beds(
                other_cats, type_to_label, PropType3.values
            )
            res.update(new_beds)
            if not near_me:
                res.pop(SeoCategory.BEDROOMS, None)

            res[SeoCategory.AMENITIES] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.AMENITIES,
                (PropType3.CONDO_APT, PropType3.HOUSE_DUPLEX),
            )
            res[SeoCategory.AFFORDABILITY] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.AFFORDABILITY,
                PropType3.values,
            )
            res[SeoCategory.LIFESTYLE] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.LIFESTYLE,
                PropType3.values,
            )
        if srp_type == 'county':
            # create 'Browse apartments by bedrooms' category
            new_beds = override_beds(
                other_cats, type_to_label, (PropType3.CONDO_APT,)
            )
            res.update(new_beds)
            res.pop(SeoCategory.BEDROOMS, None)

            res[SeoCategory.AMENITIES] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.AMENITIES,
                (PropType3.CONDO_APT, PropType3.HOUSE_DUPLEX),
            )
            res[SeoCategory.AFFORDABILITY] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.AFFORDABILITY,
                (PropType3.CONDO_APT,),
            )
            res[SeoCategory.LIFESTYLE] += compose_cats(
                other_cats,
                type_to_label,
                SeoCategory.LIFESTYLE,
                (PropType3.CONDO_APT,),
            )

    # rename internal prop type names to frontend names
    res[SeoCategory.PROP_TYPE] = [
        type_to_label.get(p, p) for p in res[SeoCategory.PROP_TYPE]
    ]

    # insert nearby and popular places, they are already strings
    nearby_and_popular = [
        SeoCategory.POPULAR_CITIES,
        SeoCategory.POPULAR_COUNTIES,
        SeoCategory.NEARBY_ZIPS,
        SeoCategory.NEARBY_COUNTIES,
    ]
    if api == 'search':
        nearby_and_popular.append(SeoCategory.POPULAR_ZIPS)
        nearby_and_popular.append(SeoCategory.NEARBY_CITIES)
    if (section != 'rent' and
            prop_type == PropType3.TOWNHOUSE and
            SeoCategory.POPULAR_ZIPS in nearby_and_popular):
        # sales + townhouse + zips = NOINDEX
        nearby_and_popular.remove(SeoCategory.POPULAR_ZIPS)
    res.update(get_nearby_and_popular(cursor, nearby_and_popular, params))

    # map 1-beds, 2-beds, 3-beds to 1,2,3
    for k, v in res.items():
        if not v:
            res[k] = None
            continue
        if k.startswith(SeoCategory.BEDROOMS):
            res[k] = [x[0] for x in v]

    # if we detected user location on home page, add nearest counties
    # NOTE: we're not currently sure if we need this feature
    #if user_county:
    #    res.update(get_nearby_and_popular(cursor, [SeoCategory.NEARBY_COUNTIES], {**params, **{'city': '', 'county': user_county}}))

    if api == 'search':
        if prop_type and search_facet:
            facet = prop_type + '/' + search_facet
        elif prop_type:
            facet = prop_type
        elif search_facet:
            facet = search_facet
        else:
            facet = ''
        res[SeoCategory.BUILDINGS] = get_top_buildings(
            cursor, srp_type, params, facet
        )
    return res


def override_beds(other_cats, type_to_label, prop_types):
    beds = {}
    for type_ in prop_types:
        if res := other_cats[type_].get(SeoCategory.BEDROOMS):
            beds[SeoCategory.BEDROOMS + '_' + type_to_label[type_]] = res
    return beds


def compose_cats(other_cats, type_to_label, category, prop_types):
    additional_cats = []
    for type_ in prop_types:
        if res := other_cats[type_].get(category):
            additional_cats.extend(add_prop_types(res, type_to_label[type_]))
    return additional_cats


def add_prop_types(labels, prop_type):
    if not labels:
        return labels
    return [{'value': label, 'prop_type': prop_type} for label in labels]
