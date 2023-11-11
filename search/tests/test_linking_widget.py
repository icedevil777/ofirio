from django.test import override_settings

from common.tests.base import PortalBaseTest
from search.seo.linking_widget import (
    get_seo_links_from_serializer,
    get_seo_links_for_listing,
)
from search.serializers import SearchQuerySerializer
from api_property.common.common import getProp


class SearchLinkingWidgetTest(PortalBaseTest):

    def test_rent_state(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-rent",
            "type": "state",
            "state_id": "fl",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_amenities": [{"value": "furnished", "prop_type": "apartments"}],
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "apartments", "townhomes"],
            "cat_affordability": [
                {"value": "cheap", "prop_type": "apartments"},
                {"value": "cheap", "prop_type": "houses"},
            ],
            "cat_bedrooms_apartments": ["1", "4", "2", "0", "3"],
            "cat_popular_zips": [
                {"state": "FL", "zip": "33160"},
                {"state": "FL", "zip": "33180"},
                {"state": "FL", "zip": "33178"},
                {"state": "FL", "zip": "33166"},
                {"state": "FL", "zip": "33179"},
                {"state": "FL", "zip": "33181"},
                {"state": "FL", "zip": "33161"},
                {"state": "FL", "zip": "33176"},
                {"state": "FL", "zip": "33928"},
                {"state": "FL", "zip": "33172"},
                {"state": "FL", "zip": "33169"},
                {"state": "FL", "zip": "33177"},
                {"state": "FL", "zip": "33162"},
                {"state": "FL", "zip": "33175"},
                {"state": "FL", "zip": "33165"},
                {"state": "FL", "zip": "33174"},
                {"state": "FL", "zip": "33173"},
                {"state": "FL", "zip": "33908"},
                {"state": "FL", "zip": "33170"},
                {"state": "FL", "zip": "33168"},
                {"state": "FL", "zip": "33913"},
            ],
            "cat_popular_cities": [
                {"state": "FL", "city": "sunny-isles-beach"},
                {"state": "FL", "city": "miami"},
                {"state": "FL", "city": "aventura"},
                {"state": "FL", "city": "doral"},
                {"state": "FL", "city": "north-miami-beach"},
                {"state": "FL", "city": "north-miami"},
                {"state": "FL", "city": "fort-myers"},
                {"state": "FL", "city": "estero"},
                {"state": "FL", "city": "golden-beach"},
                {"state": "FL", "city": "biscayne-park"},
                {"state": "FL", "city": "sweetwater"},
                {"state": "FL", "city": "miami-gardens"},
                {"state": "FL", "city": "miami-springs"},
                {"state": "FL", "city": "north-fort-myers"},
                {"state": "FL", "city": "fort-myers-beach"},
            ],
            "cat_popular_counties": [
                {"state": "FL", "county": "miami-dade-county"},
                {"state": "FL", "county": "lee-county"},
            ],
            "cat_nearby_zips": None,
            "cat_nearby_cities": None,
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_invest_city(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-invest",
            "type": "city",
            "state_id": "fl",
            "city": "north-miami",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_bedrooms": None,
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "condos", "homes"],
            "cat_affordability": None,
            "cat_popular_zips": None,
            "cat_popular_cities": None,
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": [{"state": "FL", "city": "sunny-isles-beach"}],
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }

    def test_buy_city_houses(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-buy",
            "type": "city",
            "state_id": "fl",
            "city": "north-miami",
            "cleaned_prop_type": ["houses"],
            "cat_buildings": None,
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_bedrooms": None,
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": ["condos", "homes"],
            "cat_affordability": None,
            "cat_popular_zips": [{"state": "FL", "zip": "33161"}],
            "cat_popular_cities": None,
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": [
                {"state": "FL", "city": "miami"},
                {"state": "FL", "city": "marco-island"},
            ],
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_buy_city(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-buy",
            "type": "city",
            "state_id": "fl",
            "city": "north-miami",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)

        # test without prop count treshold (prop_count=0)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_bedrooms": ["2", "3"],
            "cat_amenities": [{"value": "with-pool"}],
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "condos"],
            "cat_affordability": [
                {"value": "under-200000"},
                {"value": "under-300000"},
                {"value": "cheap"},
                {"value": "no-hoa"},
            ],
            "cat_popular_zips": [{"state": "FL", "zip": "33161"}],
            "cat_popular_cities": None,
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": [
                {"state": "FL", "city": "sunny-isles-beach"},
                {"state": "FL", "city": "miami"},
                {"state": "FL", "city": "marco-island"},
                {"state": "FL", "city": "labelle"},
            ],
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_invest_state(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-invest",
            "type": "state",
            "state_id": "fl",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_bedrooms": None,
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "condos", "townhomes", "homes"],
            "cat_affordability": None,
            "cat_popular_zips": None,
            "cat_popular_cities": [
                {"state": "FL", "city": "north-miami"},
                {"state": "FL", "city": "sunny-isles-beach"},
            ],
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": None,
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_buy_state(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-buy",
            "type": "state",
            "state_id": "fl",
            "facets": ["1-bedrooms"],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_bedrooms": None,
            "cat_amenities": [{"value": "waterfront"}, {"value": "with-pool"}],
            "cat_lifestyle": [{"value": "55-community"}, {"value": "luxury"}],
            "cat_prop_type": ["houses", "condos", "townhomes"],
            "cat_affordability": [{"value": "cheap"}],
            "cat_popular_zips": [
                {"state": "FL", "zip": "33161"},
                {"state": "FL", "zip": "34102"},
                {"state": "FL", "zip": "34145"},
                {"state": "FL", "zip": "32082"},
                {"state": "FL", "zip": "34120"},
                {"state": "FL", "zip": "34103"},
                {"state": "FL", "zip": "34108"},
                {"state": "FL", "zip": "32068"},
                {"state": "FL", "zip": "34117"},
                {"state": "FL", "zip": "32043"},
                {"state": "FL", "zip": "34104"},
                {"state": "FL", "zip": "32084"},
                {"state": "FL", "zip": "34119"},
                {"state": "FL", "zip": "32080"},
                {"state": "FL", "zip": "32034"},
                {"state": "FL", "zip": "33993"},
                {"state": "FL", "zip": "32073"},
                {"state": "FL", "zip": "34112"},
                {"state": "FL", "zip": "32003"},
                {"state": "FL", "zip": "32065"},
                {"state": "FL", "zip": "32708"},
            ],
            "cat_popular_cities": [
                {"state": "FL", "city": "naples"},
                {"state": "FL", "city": "marco-island"},
                {"state": "FL", "city": "st-augustine"},
                {"state": "FL", "city": "tampa"},
                {"state": "FL", "city": "north-miami"},
                {"state": "FL", "city": "miami"},
                {"state": "FL", "city": "ponte-vedra-beach"},
                {"state": "FL", "city": "orange-park"},
                {"state": "FL", "city": "ocala"},
                {"state": "FL", "city": "cape-coral"},
                {"state": "FL", "city": "sarasota"},
                {"state": "FL", "city": "middleburg"},
                {"state": "FL", "city": "gainesville"},
                {"state": "FL", "city": "orlando"},
                {"state": "FL", "city": "green-cove-springs"},
                {"state": "FL", "city": "port-charlotte"},
                {"state": "FL", "city": "st-petersburg"},
                {"state": "FL", "city": "bonita-springs"},
                {"state": "FL", "city": "fernandina-beach"},
                {"state": "FL", "city": "lehigh-acres"},
                {"state": "FL", "city": "fleming-island"},
            ],
            "cat_popular_counties": [
                {"state": "FL", "county": "collier-county"},
                {"state": "FL", "county": "lee-county"},
                {"state": "FL", "county": "st-johns-county"},
                {"state": "FL", "county": "miami-dade-county"},
                {"state": "FL", "county": "clay-county"},
                {"state": "FL", "county": "hillsborough-county"},
                {"state": "FL", "county": "marion-county"},
                {"state": "FL", "county": "orange-county"},
                {"state": "FL", "county": "polk-county"},
                {"state": "FL", "county": "nassau-county"},
                {"state": "FL", "county": "pinellas-county"},
                {"state": "FL", "county": "alachua-county"},
                {"state": "FL", "county": "sarasota-county"},
                {"state": "FL", "county": "charlotte-county"},
                {"state": "FL", "county": "seminole-county"},
                {"state": "FL", "county": "volusia-county"},
                {"state": "FL", "county": "lake-county"},
                {"state": "FL", "county": "levy-county"},
                {"state": "FL", "county": "manatee-county"},
                {"state": "FL", "county": "osceola-county"},
                {"state": "FL", "county": "sumter-county"},
            ],
            "cat_nearby_zips": None,
            "cat_nearby_cities": None,
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_rent_zip(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-rent",
            "type": "zip",
            "state_id": "fl",
            "zip": "33161",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_bedrooms": None,
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "apartments"],
            "cat_affordability": None,
            "cat_popular_zips": None,
            "cat_popular_cities": None,
            "cat_popular_counties": None,
            "cat_nearby_zips": [
                {"state": "FL", "zip": "33168"},
                {"state": "FL", "zip": "33181"},
                {"state": "FL", "zip": "33162"},
                {"state": "FL", "zip": "33180"},
                {"state": "FL", "zip": "33167"},
                {"state": "FL", "zip": "33169"},
                {"state": "FL", "zip": "33160"},
                {"state": "FL", "zip": "33179"},
                {"state": "FL", "zip": "33166"},
                {"state": "FL", "zip": "33172"},
                {"state": "FL", "zip": "33178"},
                {"state": "FL", "zip": "33174"},
                {"state": "FL", "zip": "33165"},
                {"state": "FL", "zip": "33173"},
                {"state": "FL", "zip": "33175"},
                {"state": "FL", "zip": "33176"},
                {"state": "FL", "zip": "33177"},
                {"state": "FL", "zip": "33170"},
            ],
            "cat_nearby_cities": [
                {"state": "FL", "city": "biscayne-park"},
                {"state": "FL", "city": "north-miami"},
                {"state": "FL", "city": "north-miami-beach"},
                {"state": "FL", "city": "sunny-isles-beach"},
                {"state": "FL", "city": "miami-gardens"},
                {"state": "FL", "city": "aventura"},
                {"state": "FL", "city": "miami"},
            ],
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_rent_city(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-rent",
            "type": "city",
            # 'cleaned_prop_type': [],
            "state_id": "fl",
            "city": "aventura",
            "facets": ["luxury"],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_amenities": [
                {"value": "with-pool"},
                {"value": "with-pool", "prop_type": "apartments"},
                {"value": "gated", "prop_type": "apartments"},
                {"value": "gym", "prop_type": "apartments"},
                {"value": "furnished", "prop_type": "apartments"},
                {"value": "balcony", "prop_type": "apartments"},
            ],
            "cat_lifestyle": [
                {"value": "luxury", "prop_type": "apartments"},
            ],
            "cat_prop_type": ["townhomes"],
            "cat_affordability": [{"value": "cheap", "prop_type": "apartments"}],
            "cat_bedrooms_apartments": ["1", "2", "4", "3"],
            "cat_popular_zips": [
                {"state": "FL", "zip": "33160"},
                {"state": "FL", "zip": "33180"},
            ],
            "cat_popular_cities": None,
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": [
                {"state": "FL", "city": "sunny-isles-beach"},
                {"state": "FL", "city": "north-miami-beach"},
                {"state": "FL", "city": "north-miami"},
                {"state": "FL", "city": "biscayne-park"},
                {"state": "FL", "city": "miami-gardens"},
                {"state": "FL", "city": "miami"},
            ],
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_rent_city_unindexable(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-rent",
            "type": "city",
            # 'cleaned_prop_type': [],
            "state_id": "fl",
            "city": "nowhere",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expexted = {
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": None,
            "cat_affordability": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expexted)

    def test_rent_county(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-rent",
            "type": "county",
            "state_id": "fl",
            "county": "lee-county",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expected = {
            "cat_amenities": [
                {"value": "pet-friendly"},
                {"value": "furnished", "prop_type": "apartments"},
            ],
            "cat_lifestyle": [{"value": "luxury", "prop_type": "apartments"}],
            "cat_prop_type": ["townhomes", "houses", "apartments"],
            "cat_affordability": None,
            "cat_popular_zips": [
                {"state": "FL", "zip": "33928"},
                {"state": "FL", "zip": "33908"},
                {"state": "FL", "zip": "33913"},
                {"state": "FL", "zip": "33903"},
                {"state": "FL", "zip": "33912"},
                {"state": "FL", "zip": "33931"},
                {"state": "FL", "zip": "33919"},
            ],
            "cat_popular_cities": [
                {"state": "FL", "city": "fort-myers"},
                {"state": "FL", "city": "estero"},
                {"state": "FL", "city": "fort-myers-beach"},
                {"state": "FL", "city": "north-fort-myers"},
            ],
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": None,
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expected)

    def test_buy_county(self):
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-buy",
            "type": "county",
            "state_id": "fl",
            "county": "lee-county",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expected = {
            "cat_bedrooms": None,
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "condos"],
            "cat_affordability": None,
            "cat_popular_zips": [
                {"state": "FL", "zip": "33993"},
                {"state": "FL", "zip": "34134"},
                {"state": "FL", "zip": "34135"},
                {"state": "FL", "zip": "33928"},
            ],
            "cat_popular_cities": [
                {"state": "FL", "city": "cape-coral"},
                {"state": "FL", "city": "bonita-springs"},
                {"state": "FL", "city": "lehigh-acres"},
                {"state": "FL", "city": "fort-myers"},
                {"state": "FL", "city": "estero"},
            ],
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": None,
            "cat_nearby_counties": [
                {"state": "FL", "county": "charlotte-county"},
                {"state": "FL", "county": "hendry-county"},
                {"state": "FL", "county": "collier-county"},
                {"state": "FL", "county": "sarasota-county"},
                {"state": "FL", "county": "manatee-county"},
                {"state": "FL", "county": "okeechobee-county"},
                {"state": "FL", "county": "palm-beach-county"},
                {"state": "FL", "county": "broward-county"},
                {"state": "FL", "county": "polk-county"},
                {"state": "FL", "county": "hillsborough-county"},
            ],
            "cat_buildings": None,
        }
        self.compare_values(links, expected)

    def test_invest_county(self):
        """this is not indexable cat, hence result is almost empty"""
        data = {
            "start": 0,
            "map_query": False,
            "index": "search-invest",
            "type": "county",
            "state_id": "fl",
            "county": "lee-county",
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception("serializer errors %s" % serializer.errors)
        links = get_seo_links_from_serializer(serializer)
        expected = {
            "cat_bedrooms": None,
            "cat_amenities": None,
            "cat_lifestyle": None,
            "cat_prop_type": ["houses", "condos", "homes"],
            "cat_affordability": None,
            "cat_popular_zips": None,
            "cat_popular_cities": None,
            "cat_popular_counties": None,
            "cat_nearby_zips": None,
            "cat_nearby_cities": None,
            "cat_nearby_counties": None,
            "cat_buildings": None,
        }
        self.compare_values(links, expected)

    def compare_values(self, links, expected):
        """we can't just compare dicts, because keys of `links` are django enums,
        which are not equal to any string constants"""
        for k, v in links.items():
            self.assertEqual(v, expected[k])
        for k, v in expected.items():
            self.assertEqual(v, links[k])

    @override_settings(INVEST_ENABLED=True)
    def test_sales_property(self):
        prop = getProp("CC666AC9B5D6B9C22B5C")
        # test with invest view
        links = get_seo_links_for_listing(prop, True)
        expexted = {
            "search-buy": {
                "cat_bedrooms": ["2", "3"],
                "cat_amenities": [{"value": "with-pool"}],
                "cat_lifestyle": None,
                "cat_prop_type": ["houses", "condos"],
                "cat_affordability": [
                    {"value": "under-200000"},
                    {"value": "under-300000"},
                    {"value": "cheap"},
                    {"value": "no-hoa"},
                ],
                "cat_popular_cities": None,
                "cat_popular_counties": None,
                "cat_nearby_zips": None,
                "cat_nearby_counties": None,
            },
            "search-invest": {
                "cat_bedrooms": None,
                "cat_amenities": None,
                "cat_lifestyle": None,
                "cat_prop_type": ["houses", "condos", "homes"],
                "cat_affordability": None,
                "cat_popular_cities": None,
                "cat_popular_counties": None,
                "cat_nearby_zips": None,
                "cat_nearby_counties": None,
            },
        }

        self.compare_values(links, expexted)
