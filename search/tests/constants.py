from copy import deepcopy


ES_EMPTY_SEARCH_RESPONSE = {
    'took': 1,
    'timed_out': False,
    '_shards': {
        'total': 5,
        'successful': 5,
        'skipped': 0,
        'failed': 0
    },
    'hits': {
        'total': {
            'value': 0,
            'relation': 'eq'
        },
        'max_score': None,
        'hits': [],
    }
}


ES_EMPTY_INSIGHTS_RESPONSE = {**ES_EMPTY_SEARCH_RESPONSE, **{'aggregations': {}}}


ES_FLORIDA_SEARCH_RESPONSE = {
    'took': 5,
    'timed_out': False,
    '_shards': {
        'total': 5,
        'successful': 5,
        'skipped': 0,
        'failed': 0
    },
    'hits': {
        'total': {
            'value': 3,
            'relation': 'eq'
        },
        'max_score': 1.0,
        'hits': [{
            '_index': 'search-20210831120557',
            '_type': '_doc',
            '_id': '751AB568FFD63EFD8A86',
            '_score': 0.0,
            '_source': {
                'prop_id': '751AB568FFD63EFD8A86',
                'status': 'for_sale',
                'badges': '',
                'list_date': '2021-04-24T10:55:09',
                'update_date': '2021-07-24T18:15:18',
                'mls_type': 'broward',
                'prop_type2': 'house-duplex',
                "cleaned_prop_type": "condo-apt",
                'building_size': 1249,
                'photo1': 'https://ofirio-prop-images.s3.amazonaws.com/mls/75/751AB568FFD63EFD8A86-1-small.jpg',
                'state_id': 'FL',
                'city': 'Fort Lauderdale',
                'city_url': 'fort-lauderdale',
                'county_name': 'Broward',
                'county_url': 'broward',
                'zip': '33319',
                'address': '4634 NW 44TH ST, Tamarac, FL, 33319',
                'address_line': '4634 NW 44TH ST',
                'address_line_url': '4634-nw-44th-st',
                'geo_point': {
                    'lat': 26.179449,
                    'lon': -80.214077
                },
                'price': 279400.0,
                'beds': 2.0,
                'baths': 2.0,
                'year_built': 1969.0,
                'predicted_rent': 1848.5,
                'is_high_cap_rate': True,
                'is_high_quality': False,
                'is_55_plus': True,
                'is_cash_only': False,
                'cap_rate': 0.0335,
                'cash_on_cash': 0.0335,
                'total_return': 0.0533,
                'cash_on_cash_mortgage': -0.0363,
                'total_return_mortgage': 0.0723,
                'cash_on_cash_15_20': -0.1498,
                'total_return_15_20': 0.0655,
                'cap_rate_15_20': 0.0255,
                'cash_on_cash_15_30': -0.0783,
                'total_return_15_30': 0.0618,
                'cap_rate_15_30': 0.0218,
                'cash_on_cash_15_40': -0.0401,
                'total_return_15_40': 0.0588,
                'cap_rate_15_40': 0.0288,
                'cash_on_cash_15_50': -0.0163,
                'total_return_15_50': 0.0564,
                'cap_rate_15_50': 0.0264,
                'cash_on_cash_30_20': -0.0363,
                'total_return_30_20': 0.0723,
                'cap_rate_30_20': 0.0223,
                'cash_on_cash_30_30': -0.0091,
                'total_return_30_30': 0.0679,
                'cap_rate_30_30': 0.0279,
                'cash_on_cash_30_40': 0.0055,
                'total_return_30_40': 0.0644,
                'cap_rate_30_40': 0.0244,
                'cash_on_cash_30_50': 0.0146,
                'total_return_30_50': 0.0617,
                'cap_rate_30_50': 0.0217,
                'default_sort': 40056,
                'pet_friendly': True,
                'parking': True,
                'cleaned_amenities': 'pool,laundry',
            }
        }, {
            '_index': 'search-20210831120557',
            '_type': '_doc',
            '_id': '8154C17F502066BBB0AB',
            '_score': 0.0,
            '_source': {
                'prop_id': '8154C17F502066BBB0AB',
                'status': 'for_sale',
                'badges': 'new',
                'list_date': '2021-08-30T15:25:12',
                'update_date': '2021-08-30T15:25:12',
                'mls_type': 'miami',
                'prop_type2': 'house-duplex',
                "cleaned_prop_type": "condo-apt",
                'building_size': 1700,
                'photo1': 'https://ofirio-prop-images.s3.amazonaws.com/mls/81/8154C17F502066BBB0AB-1-small.jpg',
                'state_id': 'FL',
                'city': 'Fort Lauderdale',
                'city_url': 'fort-lauderdale',
                'county_name': 'Broward',
                'county_url': 'broward',
                'zip': '33321',
                'address': '8514 NW 59th Pl, Tamarac, FL, 33321',
                'address_line': '8514 NW 59th Pl',
                'address_line_url': '8514-nw-59th-pl',
                'geo_point': {
                    'lat': 26.179449,
                    'lon': -80.214077
                },
                'price': 295000.0,
                'beds': 2.0,
                'baths': 2.0,
                'year_built': 1971.0,
                'predicted_rent': 1846.5,
                'is_high_cap_rate': False,
                'is_high_quality': True,
                'is_55_plus': True,
                'is_cash_only': False,
                'cap_rate': 0.0449,
                'cash_on_cash': 0.0449,
                'total_return': 0.064,
                'cash_on_cash_mortgage': 0.0147,
                'total_return_mortgage': 0.098,
                'cash_on_cash_15_20': -0.0987,
                'total_return_15_20': 0.0872,
                'cap_rate_15_20': 0.0372,
                'cash_on_cash_15_30': -0.0428,
                'total_return_15_30': 0.0809,
                'cap_rate_15_30': 0.0309,
                'cash_on_cash_15_40': -0.0128,
                'total_return_15_40': 0.0759,
                'cap_rate_15_40': 0.0359,
                'cash_on_cash_15_50': 0.0059,
                'total_return_15_50': 0.0719,
                'cap_rate_15_50': 0.0319,
                'cash_on_cash_30_20': 0.0147,
                'total_return_30_20': 0.098,
                'cap_rate_30_20': 0.038,
                'cash_on_cash_30_30': 0.0265,
                'total_return_30_30': 0.089,
                'cap_rate_30_30': 0.039,
                'cash_on_cash_30_40': 0.0328,
                'total_return_30_40': 0.0827,
                'cap_rate_30_40': 0.0327,
                'cash_on_cash_30_50': 0.0367,
                'total_return_30_50': 0.0778,
                'cap_rate_30_50': 0.0378,
                'default_sort': 91383,
                'pet_friendly': True,
                'parking': True,
                'cleaned_amenities': 'pool,laundry',
            }
        }, {
            '_index': 'search-20210910094747',
            '_type': '_doc',
            '_id': 'M5454893686',
            '_score': 1.0,
            '_source': {
                'prop_id': 'M5454893686',
                'status': 'pending',
                'badges': '',
                'list_date': '2021-04-12T03:14:05',
                'update_date': '2021-04-14T22:34:09',
                'mls_type': '',
                'prop_type2': 'condo-apt',
                 "cleaned_prop_type": "condo-apt",
                'lot_size': -1,
                'building_size': 799,
                'photo1': '',
                'state_id': 'CA',
                'city': 'Spring Valley',
                'city_url': 'spring-valley',
                'county_name': 'San Diego',
                'county_url': 'san-diego',
                'zip': '91978',
                'address': '2916 Alanwood Ct, Spring Valley, CA, 91978',
                'address_line': '2916 Alanwood Ct',
                'address_line_url': '2916-alanwood-ct',
                'geo_point': {
                    'lat': 32.734755,
                    'lon': -116.959734
                },
                'price': 379900.0,
                'beds': 2.0,
                'baths': 2.0,
                'year_built': 2004.0,
                'predicted_rent': 1466.0,
                'is_high_cap_rate': False,
                'is_high_quality': False,
                'is_55_plus': False,
                'is_rehab': False,
                'is_cash_only': False,
                'cap_rate': 0.0086,
                'cash_on_cash': 0.0086,
                'total_return': 0.028,
                'cash_on_cash_mortgage': -0.1474,
                'total_return_mortgage': 0.0253,
                'cash_on_cash_15_20': -0.2609,
                'total_return_15_20': 0.0221,
                'cap_rate_15_20': 0.0321,
                'cash_on_cash_15_30': -0.1559,
                'total_return_15_30': 0.0224,
                'cap_rate_15_30': 0.0324,
                'cash_on_cash_15_40': -0.0996,
                'total_return_15_40': 0.0227,
                'cap_rate_15_40': 0.0327,
                'cash_on_cash_15_50': -0.0646,
                'total_return_15_50': 0.0229,
                'cap_rate_15_50': 0.0329,
                'cash_on_cash_30_20': -0.1474,
                'total_return_30_20': 0.0253,
                'cap_rate_30_20': 0.0353,
                'cash_on_cash_30_30': -0.0866,
                'total_return_30_30': 0.0258,
                'cap_rate_30_30': 0.0358,
                'cash_on_cash_30_40': -0.054,
                'total_return_30_40': 0.0262,
                'cap_rate_30_40': 0.0362,
                'cash_on_cash_30_50': -0.0338,
                'total_return_30_50': 0.0266,
                'cap_rate_30_50': 0.0366,
                'default_sort': 56599.200000000004,
                'pet_friendly': True,
                'parking': True,
                'cleaned_amenities': 'pool,laundry',
            }
        }]
    },
    'aggregations': {
        'min_lon': {'value': -122.60615905746818},
        'max_lat': {'value': 42.495006965473294},
        'max_lon': {'value': -66.00279302336276},
        'min_lat': {'value': 18.37896597571671},
    },
}

ES_FLORIDA_SEARCH_RESPONSE_NO_MAP_QUERY = deepcopy(ES_FLORIDA_SEARCH_RESPONSE)
ES_FLORIDA_SEARCH_RESPONSE_NO_MAP_QUERY['aggregations'] = {}


ES_FLORIDA_SIM_NEARBY_RESPONSE = deepcopy(ES_FLORIDA_SEARCH_RESPONSE)
ES_FLORIDA_SIM_NEARBY_RESPONSE['hits']['hits'][0]['sort'] = [50.31294744290602]
ES_FLORIDA_SIM_NEARBY_RESPONSE['hits']['hits'][1]['sort'] = [50.51633712595714]
ES_FLORIDA_SIM_NEARBY_RESPONSE['hits']['hits'][2]['sort'] = [50.5567133869067]


ES_FLORIDA_ASKING_PRICE_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_percentiles': {'values': {'95.0': 1710906.6320486804, '5.0': 710906.6320486804}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 5,
}
ES_FLORIDA_ASKING_PRICE_MAIN_INSIGHTS_RESPONSE = {
    'took': 11,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'asking_price_median': {'values': {'50.0': 399944.87206598045}},
        'asking_price_average': {'value': 608880.5553893426},
        'asking_price_min': {'value': 100500.555},
        'asking_price_dist': {'buckets': {
            '*-710000.0': {'to': 710000.0, 'doc_count': 9328},
            '710000.0-910000.0': {'from': 710000.0, 'to': 910000.0, 'doc_count': 9792},
            '910000.0-1110000.0': {'from': 910000.0, 'to': 1110000.0, 'doc_count': 2852},
            '1110000.0-1310000.0': {'from': 1110000.0, 'to': 1310000.0, 'doc_count': 916},
            '1310000.0-1510000.0': {'from': 1310000.0, 'to': 1510000.0, 'doc_count': 599},
            '1510000.0-*': {'from': 1510000.0, 'doc_count': 1247},
        }},
    },
}


ES_FLORIDA_PRICE_PER_SQFT_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_per_sqft_percentiles': {'values': {'95.0': 939.6841388094574, '5.0': 739.6841388094574}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 5,
}
ES_FLORIDA_PRICE_PER_SQFT_MAIN_INSIGHTS_RESPONSE = {
    'took': 7,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'price_per_sqft_median': {'values': {'50.0': 265.8394567359089}},
        'price_per_sqft_average': {'value': 375.7958265026884},
        'price_per_sqft_dist': {'buckets': {
            '*-730.0': {'to': 730.0, 'doc_count': 210},
            '730.0-770.0': {'from': 730.0, 'to': 770.0, 'doc_count': 998},
            '770.0-810.0': {'from': 770.0, 'to': 810.0, 'doc_count': 818},
            '810.0-850.0': {'from': 810.0, 'to': 850.0, 'doc_count': 697},
            '850.0-890.0': {'from': 850.0, 'to': 890.0, 'doc_count': 430},
            '890.0-*': {'from': 890.0, 'doc_count': 1330},
        }},
    },
}

ES_FLORIDA_PRICE_PER_SQFT_MAX_1_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_per_sqft_percentiles': {'values': {'95.0': 1.0, '5.0': 0.13649967759847642}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 148, 'relation': 'eq'}},
    'timed_out': False,
    'took': 1,
}
ES_FLORIDA_PRICE_PER_SQFT_MAX_1_MAIN_INSIGHTS_RESPONSE = {
 'took': 836,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 148, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'aggregations': {'price_per_sqft_average': {'value': 0.7010571096482611},
  'price_per_sqft_median': {'values': {'50.0': 0.8251313865184784}},
  'price_per_sqft_dist': {'buckets': {'*-0.13': {'to': 0.13, 'doc_count': 7},
    '0.13-0.3': {'from': 0.13, 'to': 0.3, 'doc_count': 12},
    '0.3-0.47': {'from': 0.3, 'to': 0.47, 'doc_count': 20},
    '0.47-0.64': {'from': 0.47, 'to': 0.64, 'doc_count': 11},
    '0.64-0.81': {'from': 0.64, 'to': 0.81, 'doc_count': 19},
    '0.81-*': {'from': 0.81, 'doc_count': 79}}}}}


ES_FLORIDA_SQFT_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'building_size_percentiles': {'values': {'95.0': 2879.321439594356, '5.0': 879.321439594356}}
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 5,
}
ES_FLORIDA_SQFT_MAIN_INSIGHTS_RESPONSE = {
    'took': 8,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'sqft_median': {'values': {'50.0': 1457.394622935381}},
        'sqft_average': {'value': 1582.8041014570965},
        'sqft_dist': {'buckets': {
            '*-200.0': {'to': 200.0, 'doc_count': 47},
            '800.0-1200.0': {'from': 800.0, 'to': 1200.0, 'doc_count': 2344},
            '1200.0-1600.0': {'from': 1200.0, 'to': 1600.0, 'doc_count': 6019},
            '1600.0-2000.0': {'from': 1600.0, 'to': 2000.0, 'doc_count': 4450},
            '2000.0-2400.0': {'from': 2000.0, 'to': 2400.0, 'doc_count': 2000},
            '2400.0-*': {'from': 2400.0, 'doc_count': 3751},
        }},
    },
}


ES_FLORIDA_EST_RENT_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'predicted_rent_percentiles': {'values': {'95.0': 4488.716666666665, '5.0': 2488.716666666665}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 12,
}
ES_FLORIDA_EST_RENT_MAIN_INSIGHTS_RESPONSE = {
    'took': 11,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'est_rent_median': {'values': {'50.0': 1649.9589422038011}},
        'est_rent_average': {'value': 2005.0117146438101},
        'est_rent_dist': {'buckets': {
            '*-800.0': {'to': 800.0, 'doc_count': 5},
            '800.0-1600.0': {'from': 800.0, 'to': 1600.0, 'doc_count': 4422},
            '1600.0-2400.0': {'from': 1600.0, 'to': 2400.0, 'doc_count': 4261},
            '2400.0-3200.0': {'from': 2400.0, 'to': 3200.0, 'doc_count': 1885},
            '3200.0-4000.0': {'from': 3200.0, 'to': 4000.0, 'doc_count': 582},
            '4000.0-*': {'from': 4000.0, 'doc_count': 1667},
        }},
    },
}


ES_FLORIDA_CAP_RATE_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'cap_rate_percentiles': {'values': {'95.0': 0.04851485443622202, '5.0': 0.00851485443622202}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 11,
}
ES_FLORIDA_CAP_RATE_MAIN_INSIGHTS_RESPONSE = {
    'took': 11,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'cap_rate_median': {'values': {'50.0': 0.020124188034587317}},
        'cap_rate_average': {'value': 0.019611659686750153},
        'cap_rate_dist': {'buckets': {
            '*-0.0.01': {'to': 0.01, 'doc_count': 6634},
            '0.01-0.02': {'from': 0.01, 'to': 0.02, 'doc_count': 5522},
            '0.02-0.03': {'from': 0.02, 'to': 0.03, 'doc_count': 5866},
            '0.03-0.04': {'from': 0.03, 'to': 0.04, 'doc_count': 3783},
            '0.04-0.05': {'from': 0.04, 'to': 0.05, 'doc_count': 1540},
            '0.05-0.06': {'from': 0.05, 'to': 0.06, 'doc_count': 579},
            '0.06-*': {'from': 0.06, 'doc_count': 485},
        }},
    },
}


ES_FLORIDA_YEAR_BUILT_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'year_built_percentiles': {'values': {'95.0': 2021.0, '5.0': 1981.0}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 12,
}
ES_FLORIDA_YEAR_BUILT_MAIN_INSIGHTS_RESPONSE = {
    'took': 13,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'year_built_median': {'values': {'50.0': 1986.0}},
        'year_built_average': {'value': 1984.5508323301092},
        'year_built_dist': {'buckets': {
            '*-1960.0': {'to': 1960.0, 'doc_count': 5},
            '1960.0-1970.0': {'from': 1960.0, 'to': 1970.0, 'doc_count': 1009},
            '1970.0-1980.0': {'from': 1970.0, 'to': 1980.0, 'doc_count': 4422},
            '1980.0-1990.0': {'from': 1980.0, 'to': 1990.0, 'doc_count': 3061},
            '1990.0-2000.0': {'from': 1990.0, 'to': 2000.0, 'doc_count': 1885},
            '2000.0-2010.0': {'from': 2000.0, 'to': 2010.0, 'doc_count': 485},
            '2010.0-*': {'from': 2010.0, 'doc_count': 1667},
        }},
    },
}


ES_FLORIDA_EST_RENT_DISTRIBUTION_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'predicted_rent_percentiles': {'values': {'95.0': 4488.716666666665,
                                                  '5.0': 2488.716666666665}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 12,
}
ES_FLORIDA_EST_RENT_DISTRIBUTION_MAIN_INSIGHTS_RESPONSE = {
    'took': 141,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'est_rent_distribution_median_predicted_rent': {'values': {'50.0': 2045.2942947045917}},
        'est_rent_distribution_dist': {'buckets': {
          '*-2400.0': {'to': 2400.0, 'doc_count': 769},
          '2400.0-3000.0': {'from': 2400.0, 'to': 3000.0, 'doc_count': 13257},
          '3000.0-3600.0': {'from': 3000.0, 'to': 3600.0, 'doc_count': 8024},
          '3600.0-*': {'from': 3600.0, 'doc_count': 2684},
        }},
        'est_rent_distribution_average_cap_rate': {'value': 0.02816475149083337},
        'est_rent_distribution_median_price': {'values': {'50.0': 399922.11000553047}},
        'est_rent_distribution_median_price_per_sqft': {'values': {'50.0': 268.2114777460048}},
        'est_rent_distribution_median_cap_rate': {'values': {'50.0': 0.02959822144124582}},
    },
}


ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_BASE_INSIGHTS_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_percentiles': {'values': {'95.0': 440088.716, '5.0': 24088.7163}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 12,
}
ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_MAIN_INSIGHTS_RESPONSE = {
    'took': 141,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'asking_price_distribution_median_price': {'values': {'50.0': 100560}},
        'asking_price_distribution_dist': {'buckets': {
          '*-24000.0': {'to': 24000.0, 'doc_count': 769},
          '24000.0-162600.0': {'from': 24000.0, 'to': 162600.0, 'doc_count': 13257},
          '162600.0-301200.0': {'from': 162600.0, 'to': 301200.0, 'doc_count': 8024},
          '301200.0-*': {'from': 301200.0, 'doc_count': 2684},
        }},
        'asking_price_distribution_median_price_per_sqft': {
            'values': {'50.0': 1710906.6320486804, '5.0': 710906.6320486804}},
        'asking_price_distribution_cnt_good_deal': {'buckets': [{'key_as_string': 'false'},]},
        'asking_price_distribution_median_days_on_market': {'values': {'50.0': 36}},
    },
}


ES_ASKING_PRICE_NO_PROPS_IN_AREA_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_percentiles': {'values': {'95.0': None, '5.0': None}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 0, 'relation': 'eq'}},
    'timed_out': False,
    'took': 0,
}


ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE = {
    'took': 9,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'median_cap_rate_by_building_type': {
            'doc_count_error_upper_bound': 0,
            'sum_other_doc_count': 0,
            'buckets': [
            {'key': 'house-duplex', 'doc_count': 14081,
             'cap_rate_percentiles': {'values': {'50.0': 0.025058679498385097}}},
            {'key': 'condo-apt', 'doc_count': 10653,
             'cap_rate_percentiles': {'values': {'50.0': 0.012323684143112567}}}],
        },
    },
}


ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_INSIGHTS_RESPONSE = {
    'took': 9,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'count_and_median_rent_by_building_type': {
            'doc_count_error_upper_bound': 0,
            'sum_other_doc_count': 0,
            'buckets': [
            {'key': 'house-duplex', 'doc_count': 14081,
             'predicted_rent_percentiles': {'values': {'50.0': 1629.2710775047258}}},
            {'key': 'condo-apt', 'doc_count': 10653,
             'predicted_rent_percentiles': {'values': {'50.0': 1672.1544211195928}}}],
        },
    },
}


ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE = {
    'took': 9,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        'count_and_price_by_building_type': {
            'doc_count_error_upper_bound': 0,
            'sum_other_doc_count': 0,
            'buckets': [
            {'key': 'house-duplex', 'doc_count': 14081,
             'price_percentiles': {'values': {'50.0': 351935.752}}},
            {'key': 'condo-apt', 'doc_count': 10653,
             'price_percentiles': {'values': {'50.0': 368354.468}}}],
        },
    },
}


ES_FLORIDA_COUNT_BY_BEDS_INSIGHTS_RESPONSE = {
 'took': 2,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 24734, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'aggregations': {
    'count_by_beds': {'buckets': {
        '0.0-1.0': {'from': 0.0, 'to': 1.0, 'doc_count': 421},
        '1.0-2.0': {'from': 1.0, 'to': 2.0, 'doc_count': 2414},
        '2.0-3.0': {'from': 2.0, 'to': 3.0, 'doc_count': 7465},
        '3.0-4.0': {'from': 3.0, 'to': 4.0, 'doc_count': 9253},
        '4.0-5.0': {'from': 4.0, 'to': 5.0, 'doc_count': 4112},
        '5.0-*': {'from': 5.0, 'doc_count': 1069},
    }}
 }
}


ES_FLORIDA_COUNT_BY_BATHS_INSIGHTS_RESPONSE = {
 'took': 2,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 24734, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'aggregations': {
    'count_by_baths': {'buckets': {
        '1.0-1.5': {'from': 1.0, 'to': 1.5, 'doc_count': 3664},
        '1.5-2.0': {'from': 1.5, 'to': 2.0, 'doc_count': 1130},
        '2.0-2.5': {'from': 2.0, 'to': 2.5, 'doc_count': 11457},
        '2.5-3.0': {'from': 2.5, 'to': 3.0, 'doc_count': 2017},
        '3.0-3.5': {'from': 3.0, 'to': 3.5, 'doc_count': 2855},
        '3.5-4.0': {'from': 3.5, 'to': 4.0, 'doc_count': 1729},
        '4.0-*': {'from': 4.0, 'doc_count': 420},
    }}
 }
}

ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_INSIGHTS_RESPONSE = {
 'took': 25,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 24734, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'aggregations': {
    'cap_rate_and_rent_by_beds': {'buckets': {
        '0.0-1.0': {'from': 0.0, 'to': 1.0, 'doc_count': 284,
                  'predicted_rent_percentiles': {'values': {'50.0': 1490.0}},
                  'cap_rate_percentiles': {'values': {'50.0': 0.01360000018030405}}},
        '1.0-2.0': {'from': 1.0, 'to': 2.0, 'doc_count': 4794,
                    'predicted_rent_percentiles': {'values': {'50.0': 1448.5811234817816}},
                    'cap_rate_percentiles': {'values': {'50.0': 0.03098487637457822}}},
        '2.0-3.0': {'from': 2.0, 'to': 3.0, 'doc_count': 12974,
                    'predicted_rent_percentiles': {'values': {'50.0': 1968.7650303507496}},
                    'cap_rate_percentiles': {'values': {'50.0': 0.031109154334811564}}},
        '3.0-4.0': {'from': 3.0, 'to': 4.0, 'doc_count': 4584,
                    'predicted_rent_percentiles': {'values': {'50.0': 2753.431818181818}},
                    'cap_rate_percentiles': {'values': {'50.0': 0.026931447506095513}}},
        '4.0-5.0': {'from': 4.0, 'to': 5.0, 'doc_count': 1378,
                    'predicted_rent_percentiles': {'values': {'50.0': 3797.5}},
                    'cap_rate_percentiles': {'values': {'50.0': 0.02209333305557569}}},
        '5.0-*': {'from': 5.0, 'doc_count': 720,
                  'predicted_rent_percentiles': {'values': {'50.0': 3542.0}},
                  'cap_rate_percentiles': {'values': {'50.0': 0.017133334030707676}}},
    }}
 }
}

ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_INSIGHTS_RESPONSE = {
 'took': 25,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 24734, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'aggregations': {
    'count_and_price_by_beds': {'buckets': {
        '0.0-1.0': {'from': 0.0, 'to': 1.0, 'doc_count': 284,
                  'price_percentiles': {'values': {'50.0': 251935.752}}},
        '1.0-2.0': {'from': 1.0, 'to': 2.0, 'doc_count': 4794,
                    'price_percentiles': {'values': {'50.0': 271935.752}}},
        '2.0-3.0': {'from': 2.0, 'to': 3.0, 'doc_count': 12974,
                    'price_percentiles': {'values': {'50.0': 311935.752}}},
        '3.0-4.0': {'from': 3.0, 'to': 4.0, 'doc_count': 4584,
                    'price_percentiles': {'values': {'50.0': 351935.752}}},
        '4.0-5.0': {'from': 4.0, 'to': 5.0, 'doc_count': 1378,
                    'price_percentiles': {'values': {'50.0': 451935.752}}},
        '5.0-*': {'from': 5.0, 'doc_count': 720,
                  'price_percentiles': {'values': {'50.0': 551935.752}}},
    }}
 }
}


ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_INSIGHTS_RESPONSE = {
 'took': 27,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 24734, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'aggregations': {
    'cap_rate_and_rent_by_baths': {'buckets': {
        '1.0-1.5': {'from': 1.0, 'to': 1.5, 'doc_count': 3188,
         'predicted_rent_percentiles': {'values': {'50.0': 1423.9200000000003}},
         'cap_rate_percentiles': {'values': {'50.0': 0.032679999619722365}}},
        '1.5-2.0': {'from': 1.5, 'to': 2.0, 'doc_count': 880,
         'predicted_rent_percentiles': {'values': {'50.0': 1736.89}},
         'cap_rate_percentiles': {'values': {'50.0': 0.021650000475347042}}},
        '2.0-2.5': {'from': 2.0, 'to': 2.5, 'doc_count': 10602,
         'predicted_rent_percentiles': {'values': {'50.0': 1929.0081324248779}},
         'cap_rate_percentiles': {'values': {'50.0': 0.032077903063295825}}},
        '2.5-3.0': {'from': 2.5, 'to': 3.0, 'doc_count': 2767,
         'predicted_rent_percentiles': {'values': {'50.0': 2756.9482142857137}},
         'cap_rate_percentiles': {'values': {'50.0': 0.026471428307039396}}},
        '3.0-3.5': {'from': 3.0, 'to': 3.5, 'doc_count': 3434,
         'predicted_rent_percentiles': {'values': {'50.0': 2844.446799089069}},
         'cap_rate_percentiles': {'values': {'50.0': 0.026540579449763336}}},
        '3.5-4.0': {'from': 3.5, 'to': 4.0, 'doc_count': 2479,
         'predicted_rent_percentiles': {'values': {'50.0': 2612.375}},
         'cap_rate_percentiles': {'values': {'50.0': 0.02712963010977816}}},
        '4.0-*': {'from': 4.0, 'doc_count': 220,
         'predicted_rent_percentiles': {'values': {'50.0': 3542.0}},
         'cap_rate_percentiles': {'values': {'50.0': 0.017150000669062138}}},
    }}
 }
}


ES_FLORIDA_ALL_BASE_INSIGHTS_INVEST_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_percentiles': {'values': {'95.0': 1710906.6320486804, '5.0': 1110906.6320486804}},
        'predicted_rent_percentiles': {'values': {'95.0': 4488.716666666665, '5.0': 2488.716666666665}},
        'cap_rate_percentiles': {'values': {'95.0': 0.04851485443622202, '5.0': 0.00851485443622202}},
        'building_size_percentiles': {'values': {'95.0': 2879.321439594356, '5.0': 1879.321439594356}},
        'year_built_percentiles': {'values': {'95.0': 2021.0, '5.0': 1981.0}},
        'price_per_sqft_percentiles': {'values': {'95.0': 939.6841388094574, '5.0': 339.6841388094574}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 5,
}
ES_FLORIDA_ALL_MAIN_INSIGHTS_INVEST_RESPONSE = {
    'took': 11,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        **ES_FLORIDA_ASKING_PRICE_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_EST_RENT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_CAP_RATE_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_SQFT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_YEAR_BUILT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_PRICE_PER_SQFT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_BY_BEDS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_BY_BATHS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_EST_RENT_DISTRIBUTION_MAIN_INSIGHTS_RESPONSE['aggregations'],
    },
}


ES_FLORIDA_ALL_BASE_INSIGHTS_BUY_RESPONSE = {
    '_shards': {'failed': 0, 'skipped': 0, 'successful': 5, 'total': 5},
    'aggregations': {
        'price_percentiles': {'values': {'95.0': 1710906.6320486804, '5.0': 1110906.6320486804}},
        'building_size_percentiles': {'values': {'95.0': 2879.321439594356, '5.0': 1879.321439594356}},
        'year_built_percentiles': {'values': {'95.0': 2021.0, '5.0': 1981.0}},
        'price_per_sqft_percentiles': {'values': {'95.0': 939.6841388094574, '5.0': 339.6841388094574}},
    },
    'hits': {'hits': [],
             'max_score': None,
             'total': {'value': 10000, 'relation': 'gte'}},
    'timed_out': False,
    'took': 5,
}
ES_FLORIDA_ALL_MAIN_INSIGHTS_BUY_RESPONSE = {
    'took': 11,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        **ES_FLORIDA_ASKING_PRICE_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_SQFT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_YEAR_BUILT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_PRICE_PER_SQFT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_BY_BEDS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_BY_BATHS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_MAIN_INSIGHTS_RESPONSE['aggregations'],
    },
}


ES_FLORIDA_ALL_BASE_INSIGHTS_RENT_RESPONSE = {'took': 106,
 'timed_out': False,
 '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 10000, 'relation': 'gte'},
          'max_score': None,
          'hits': []},
 'aggregations': {'year_built_percentiles': {'values': {'5.0': 1953.0, '95.0': 2018.0}},
                  'building_size_percentiles': {'values': {'95.0': 2879.321439594356, '5.0': 1879.321439594356}},
                  'price_per_sqft_percentiles': {'values': {'5.0': 0.7000000729959579, '95.0': 2.1157454998236984}},
                  'price_percentiles': {'values': {'5.0': 875.0, '95.0': 3299.9757077625572}}
  },
}
ES_FLORIDA_ALL_MAIN_INSIGHTS_RENT_RESPONSE = {
    'took': 11,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'relation': 'eq', 'value': 24734},
        'max_score': None,
        'hits': []},
    'aggregations': {
        **ES_FLORIDA_ASKING_PRICE_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_YEAR_BUILT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_PRICE_PER_SQFT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_BY_BEDS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_BY_BATHS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_SQFT_MAIN_INSIGHTS_RESPONSE['aggregations'],
        **ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_MAIN_INSIGHTS_RESPONSE['aggregations'],
    },
}


EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST = {
 'query': {'bool': {'filter': [{'term': {'state_id': 'FL'}},
                               {'terms': {'status': ['for_sale', 'under_contract']}}],
                    'minimum_should_match': 0,
                    'must': [],
                    'should': []}},
 'size': 0,
 'track_total_hits': True}


EXPECTED_ES_BODY_QUERY_FLORIDA_BUY = {
 'query': {'bool': {'filter': [{'term': {'state_id': 'FL'}},
                               {'terms': {'status': ['for_sale', 'under_contract']}}],
                    'minimum_should_match': 0,
                    'must': [],
                    'should': []}},
 'size': 0,
 'track_total_hits': True}


EXPECTED_ES_BODY_QUERY_FLORIDA_RENT = {
 'query': {'bool': {'filter': [{'term': {'state_id': 'FL'}},
                               {'terms': {'status': ['for_rent', 'under_contract']}}],
                    'minimum_should_match': 0,
                    'must': [],
                    'should': []}},
 'size': 0,
 'track_total_hits': True}


ES_FLORIDA_ASKING_PRICE_EXPECTED_ES_BODY = {
 'aggs': {'asking_price_average': {'avg': {'field': 'price'}},
          'asking_price_min': {'min': {'field': 'price'}},
          'asking_price_dist': {'range': {'field': 'price',
                                          'keyed': True,
                                          'ranges': [{'to': 700000},
                                                     {'from': 700000, 'to': 900000},
                                                     {'from': 900000, 'to': 1100000},
                                                     {'from': 1100000, 'to': 1300000},
                                                     {'from': 1300000,'to': 1500000},
                                                     {'from': 1500000}]}},
          'asking_price_median': {'percentiles': {'field': 'price',
                                                  'keyed': True,
                                                  'percents': [50]}}},
}


ES_FLORIDA_EST_RENT_EXPECTED_ES_BODY = {
 'aggs': {'est_rent_average': {'avg': {'field': 'predicted_rent'}},
          'est_rent_dist': {'range': {'field': 'predicted_rent',
                                      'keyed': True,
                                      'ranges': [{'to': 2500},
                                                 {'from': 2500, 'to': 2900},
                                                 {'from': 2900, 'to': 3300},
                                                 {'from': 3300, 'to': 3700},
                                                 {'from': 3700, 'to': 4100},
                                                 {'from': 4100}]}},
          'est_rent_median': {'percentiles': {'field': 'predicted_rent',
                                              'keyed': True,
                                              'percents': [50]}}},
}


ES_FLORIDA_EST_RENT_DISTRIBUTION_EXPECTED_ES_BODY = {
 'aggs': {'est_rent_distribution_average_cap_rate': {'avg': {'field': 'cap_rate'}},
          'est_rent_distribution_median_predicted_rent': {'percentiles': {
              'field': 'predicted_rent', 'keyed': True, 'percents': [50]}},
          'est_rent_distribution_median_price': {'percentiles': {
              'field': 'price', 'keyed': True, 'percents': [50]}},
          'est_rent_distribution_median_price_per_sqft': {
              'percentiles': {'field': 'price_per_sqft', 'keyed': True, 'percents': [50]}},
          'est_rent_distribution_median_cap_rate': {
               'percentiles': {'field': 'cap_rate', 'keyed': True, 'percents': [50]}},
          'est_rent_distribution_dist': {'range': {'field': 'predicted_rent',
                                         'keyed': True,
                                         'ranges': [{'to': 2400.0},
                                                    {'from': 2400.0, 'to': 3000.0},
                                                    {'from': 3000.0, 'to': 3600.0},
                                                    {'from': 3600.0}]}}},
}


ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_BUY = {
    'aggs': {
        'asking_price_distribution_median_price': {'percentiles': {
            'field': 'price', 'keyed': True, 'percents': [50]}},
        'asking_price_distribution_median_price_per_sqft': {'percentiles': {
            'field': 'price_per_sqft', 'keyed': True, 'percents': [50]}},
        'asking_price_distribution_dist': {'range': {'field': 'price',
                                                     'keyed': True,
                                                     'ranges': [{'to': 20000.0},
                                                                {'from': 20000.0, 'to': 160000.0},
                                                                {'from': 160000.0, 'to': 300000.0},
                                                                {'from': 300000.0}]}},
        'asking_price_distribution_cnt_good_deal': {'terms': {'field': 'is_good_deal'}}, },
}

ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_RENT = {
    'aggs':
        {'asking_price_distribution_median_days_on_market': {'percentiles': {
            'field': 'days_on_market', 'keyed': True, 'percents': [50]}},
            'asking_price_distribution_median_price': {'percentiles': {
                'field': 'price', 'keyed': True, 'percents': [50]}},
            'asking_price_distribution_dist': {'range': {'field': 'price',
                                                         'keyed': True,
                                                         'ranges': [{'to': 20000.0},
                                                                    {'from': 20000.0, 'to': 160000.0},
                                                                    {'from': 160000.0, 'to': 300000.0},
                                                                    {'from': 300000.0}]}},
            'asking_price_distribution_cnt_good_deal': {'terms': {'field': 'is_good_deal'}}, }}


ES_FLORIDA_CAP_RATE_EXPECTED_ES_BODY = {
 'aggs': {'cap_rate_average': {'avg': {'field': 'cap_rate'}},
          'cap_rate_median': {'percentiles': {'field': 'cap_rate',
                                              'keyed': True,
                                              'percents': [50]}},
          'cap_rate_dist': {'range': {'field': 'cap_rate',
                                      'keyed': True,
                                      'ranges': [{'to': 0.01},
                                                 {'from': 0.01, 'to': 0.016},
                                                 {'from': 0.016, 'to': 0.022},
                                                 {'from': 0.022, 'to': 0.028},
                                                 {'from': 0.028, 'to': 0.034},
                                                 {'from': 0.034, 'to': 0.04},
                                                 {'from': 0.04}]}}},
}


ES_FLORIDA_SQFT_EXPECTED_ES_BODY = {
 'aggs': {'sqft_average': {'avg': {'field': 'building_size'}},
          'sqft_dist': {'range': {'field': 'building_size',
                                  'keyed': True,
                                  'ranges': [{'to': 900},
                                             {'from': 900, 'to': 1300},
                                             {'from': 1300, 'to': 1700},
                                             {'from': 1700, 'to': 2100},
                                             {'from': 2100, 'to': 2500},
                                             {'from': 2500}]}},
          'sqft_median': {'percentiles': {'field': 'building_size',
                                          'keyed': True,
                                          'percents': [50]}}},
}


ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY = {
 'aggs': {'year_built_average': {'avg': {'field': 'year_built'}},
          'year_built_median': {'percentiles': {'field': 'year_built',
                                                'keyed': True,
                                                'percents': [50]}},
          'year_built_dist': {'range': {'field': 'year_built',
                                        'keyed': True,
                                        'ranges': [{'to': 1960},
                                                   {'from': 1960, 'to': 1970},
                                                   {'from': 1970, 'to': 1980},
                                                   {'from': 1980, 'to': 1990},
                                                   {'from': 1990, 'to': 2000},
                                                   {'from': 2000, 'to': 2010},
                                                   {'from': 2010}]}}},
}


ES_FLORIDA_PRICE_PER_SQFT_EXPECTED_ES_BODY = {
 'aggs': {'price_per_sqft_average': {'avg': {'field': 'price_per_sqft'}},
          'price_per_sqft_dist': {'range': {'field': 'price_per_sqft',
                                            'keyed': True,
                                            'ranges': [{'to': 740},
                                                       {'from': 740, 'to': 780},
                                                       {'from': 780, 'to': 820},
                                                       {'from': 820, 'to': 860},
                                                       {'from': 860, 'to': 900},
                                                       {'from': 900}]}},
          'price_per_sqft_median': {'percentiles': {'field': 'price_per_sqft',
                                                    'keyed': True,
                                                    'percents': [50]}}},
}


ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_EXPECTED_ES_BODY = {
 'aggs': {'median_cap_rate_by_building_type': {
              'terms': {'field': 'cleaned_prop_type'},
              'aggs': {'cap_rate_percentiles': {
                           'percentiles': {'field': 'cap_rate', 'keyed': True, 'percents': [50]}
                      }}}},
}


ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_EXPECTED_ES_BODY = {
 'aggs': {'count_and_median_rent_by_building_type': {
              'terms': {'field': 'cleaned_prop_type'},
              'aggs': {'predicted_rent_percentiles': {
                           'percentiles': {'field': 'predicted_rent', 'keyed': True, 'percents': [50]}
                      }}}},
}


ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY = {
 'aggs': {'count_and_price_by_building_type': {
              'terms': {'field': 'cleaned_prop_type'},
              'aggs': {'price_percentiles': {
                           'percentiles': {'field': 'price', 'keyed': True, 'percents': [50]}
                      }}}},
}


ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY = {
 'aggs': {'count_by_beds': {'range': {'field': 'beds',
                                      'keyed': True,
                                      'ranges': [{'from': 0, 'to': 1},
                                                 {'from': 1, 'to': 2},
                                                 {'from': 2, 'to': 3},
                                                 {'from': 3, 'to': 4},
                                                 {'from': 4, 'to': 5},
                                                 {'from': 5}]}}},
}


ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY = {
 'aggs': {'count_by_baths': {'range': {'field': 'baths',
                                       'keyed': True,
                                       'ranges': [{'from': 1.0, 'to': 1.5},
                                                  {'from': 1.5, 'to': 2.0},
                                                  {'from': 2.0, 'to': 2.5},
                                                  {'from': 2.5, 'to': 3.0},
                                                  {'from': 3.0, 'to': 3.5},
                                                  {'from': 3.5, 'to': 4.0},
                                                  {'from': 4.0}]}}},
}


ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_EXPECTED_ES_BODY = {
 'aggs': {
     'cap_rate_and_rent_by_beds': {
         'range': {
             'field': 'beds',
             'keyed': True,
             'ranges': [{'from': 0.0, 'to': 1.0},
                        {'from': 1.0, 'to': 2.0},
                        {'from': 2.0, 'to': 3.0},
                        {'from': 3.0, 'to': 4.0},
                        {'from': 4.0, 'to': 5.0},
                        {'from': 5.0}],
         },
         'aggs': {
             'cap_rate_percentiles': {
                 'percentiles': {'field': 'cap_rate', 'keyed': True, 'percents': [50]}
             },
             'predicted_rent_percentiles': {
                 'percentiles': {'field': 'predicted_rent', 'keyed': True, 'percents': [50]}
             },
 }}},
}


ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY = {
 'aggs': {
     'count_and_price_by_beds': {
         'range': {
             'field': 'beds',
             'keyed': True,
             'ranges': [
                {'from': 0.0, 'to': 1.0},
                {'from': 1.0, 'to': 2.0},
                {'from': 2.0, 'to': 3.0},
                {'from': 3.0, 'to': 4.0},
                {'from': 4.0, 'to': 5.0},
                {'from': 5.0},
            ]
         },
         'aggs': {
             'price_percentiles': {
                 'percentiles': {'field': 'price', 'keyed': True, 'percents': [50]}
             },
 }}},
}


ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_EXPECTED_ES_BODY = {
 'aggs': {
     'cap_rate_and_rent_by_baths': {
         'range': {
             'field': 'baths',
             'keyed': True,
             'ranges': [
                 {'from': 1.0, 'to': 1.5},
                 {'from': 1.5, 'to': 2.0},
                 {'from': 2.0, 'to': 2.5},
                 {'from': 2.5, 'to': 3.0},
                 {'from': 3.0, 'to': 3.5},
                 {'from': 3.5, 'to': 4.0},
                 {'from': 4.0},
            ]
         },
         'aggs': {
             'cap_rate_percentiles': {
                 'percentiles': {'field': 'cap_rate', 'keyed': True, 'percents': [50]}
             },
             'predicted_rent_percentiles': {
                 'percentiles': {'field': 'predicted_rent', 'keyed': True, 'percents': [50]}
             },
 }}},
}


ES_FLORIDA_ASKING_PRICE_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_ASKING_PRICE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_EST_RENT_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_EST_RENT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_EST_RENT_DISTRIBUTION_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_EST_RENT_DISTRIBUTION_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_BUY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_CAP_RATE_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_CAP_RATE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_SQFT_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_SQFT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_PRICE_PER_SQFT_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_PRICE_PER_SQFT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}

ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_EXPECTED_ES_BODY_INVEST = {
 **ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_INVEST}


ES_FLORIDA_ASKING_PRICE_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_ASKING_PRICE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_EST_RENT_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_EST_RENT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_EST_RENT_DISTRIBUTION_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_EST_RENT_DISTRIBUTION_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_BUY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_CAP_RATE_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_CAP_RATE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_SQFT_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_SQFT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_PRICE_PER_SQFT_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_PRICE_PER_SQFT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_CAP_RATE_AND_RENT_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_EXPECTED_ES_BODY_BUY = {
 **ES_FLORIDA_CAP_RATE_AND_RENT_BY_BATHS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_BUY}

ES_FLORIDA_ASKING_PRICE_EXPECTED_ES_BODY_RENT = {
 'aggs': {'asking_price_average': {'avg': {'field': 'price'}},
          'asking_price_min': {'min': {'field': 'price'}},
          'asking_price_dist': {'range': {'field': 'price',
                                          'keyed': True,
                                          'ranges': [{'to': 700000},
                                                     {'from': 700000, 'to': 900000},
                                                     {'from': 900000, 'to': 1100000},
                                                     {'from': 1100000, 'to': 1300000},
                                                     {'from': 1300000,'to': 1500000},
                                                     {'from': 1500000}]}},
          'asking_price_median': {'percentiles': {'field': 'price',
                                                  'keyed': True,
                                                  'percents': [50]}}},
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_YEAR_BUILT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_PRICE_PER_SQFT_EXPECTED_ES_BODY_RENT = {
  'aggs': {'price_per_sqft_average': {'avg': {'field': 'price_per_sqft'}},
          'price_per_sqft_dist': {'range': {'field': 'price_per_sqft',
                                            'keyed': True,
                                            'ranges': [{'to': 740},
                                                       {'from': 740, 'to': 780},
                                                       {'from': 780, 'to': 820},
                                                       {'from': 820, 'to': 860},
                                                       {'from': 860, 'to': 900},
                                                       {'from': 900}]}},
          'price_per_sqft_median': {'percentiles': {'field': 'price_per_sqft',
                                                    'keyed': True,
                                                    'percents': [50]}}},
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_PRICE_PER_SQFT_MAX_1_EXPECTED_ES_BODY_RENT = {
    'size': 0, 'track_total_hits': True,
    'query': {
        'bool': {
            'must': [],
            'filter': [{'term': {'state_id': 'FL'}},
                       {'terms': {'status': ['for_rent', 'under_contract']}},
                       {'range': {'price_per_sqft': {'lte': 1.0}}}],
            'should': [],
            'minimum_should_match': 0
        }
    },
    'aggs': {
        'price_per_sqft_median': {
            'percentiles': {'keyed': True, 'field': 'price_per_sqft', 'percents': [50]}
        },
        'price_per_sqft_average': {
            'avg': {'field': 'price_per_sqft'}
        },
        'price_per_sqft_dist': {
            'range': {
                'field': 'price_per_sqft', 'keyed': True,
                'ranges': [{'to': 0.14},
                           {'from': 0.14, 'to': 0.31},
                           {'from': 0.31, 'to': 0.48},
                           {'from': 0.48, 'to': 0.65},
                           {'from': 0.65, 'to': 0.82},
                           {'from': 0.82}]
            }
        }
    }
}

ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_COUNT_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_COUNT_BY_BATHS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_COUNT_AND_PRICE_BY_BEDS_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_COUNT_AND_PRICE_BY_BUILDING_TYPE_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_SQFT_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_SQFT_EXPECTED_ES_BODY,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}

ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_RENT = {
 **ES_FLORIDA_ASKING_PRICE_DISTRIBUTION_EXPECTED_ES_BODY_RENT,
 **EXPECTED_ES_BODY_QUERY_FLORIDA_RENT}


EXPECTED_ASKING_PRICE_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'asking_price': {
        'meta': {
            'min': 100500,
            'median': 399944,
            'average': 608880,
        },
        'labels': [
            {'min': None, 'max': 710000},
            {'min': 710000, 'max': 910000},
            {'min': 910000, 'max': 1110000},
            {'min': 1110000, 'max': 1310000},
            {'min': 1310000, 'max': 1510000},
            {'min': 1510000, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.37713269184119025, 0.39589229400824777, 0.1153068650440689,
                         0.037034042209104875, 0.0242176760734212, 0.05041643082396701],
            }
        ]
    }
}
EXPECTED_EST_RENT_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'est_rent': {
        'meta': {
            'median': 1649,
            'average': 2005,
        },
        'labels': [
            {'min': None, 'max': 800},
            {'min': 800, 'max': 1600},
            {'min': 1600, 'max': 2400},
            {'min': 2400, 'max': 3200},
            {'min': 3200, 'max': 4000},
            {'min': 4000, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.00020215088542087814, 0.17878224306622462, 0.17227298455567236,
                         0.07621088380367105, 0.023530363062990216, 0.06739710519932077],
            }
        ]
    }
}
EXPECTED_CAP_RATE_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'cap_rate': {
        'meta': {
            'median': 0.020124188034587317,
            'average': 0.019611659686750153,
        },
        'labels': [
            {'min': None, 'max': 0.01},
            {'min': 0.01, 'max': 0.02},
            {'min': 0.02, 'max': 0.03},
            {'min': 0.03, 'max': 0.04},
            {'min': 0.04, 'max': 0.05},
            {'min': 0.05, 'max': 0.06},
            {'min': 0.06, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.2682137947764211, 0.22325543785881782, 0.23716341877577424,
                         0.1529473599094364, 0.062262472709630465, 0.023409072531737688,
                         0.01960863588582518],
            }
        ]
    }
}
EXPECTED_SQFT_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'sqft': {
        'meta': {
            'median': 1457,
            'average': 1582,
        },
        'labels': [
            {'min': None, 'max': 200},
            {'min': 800, 'max': 1200},
            {'min': 1200, 'max': 1600},
            {'min': 1600, 'max': 2000},
            {'min': 2000, 'max': 2400},
            {'min': 2400, 'max': None}
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.0019002183229562546, 0.09476833508530767, 0.2433492358696531,
                         0.17991428802458154, 0.08086035416835126, 0.15165359424274277],
            }
        ]
    }
}
EXPECTED_YEAR_BUILT_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'year_built': {
        'meta': {
            'median': 1986,
            'average': 1984,
        },
        'labels': [
            {'min': None, 'max': 1960},
            {'min': 1960, 'max': 1970},
            {'min': 1970, 'max': 1980},
            {'min': 1980, 'max': 1990},
            {'min': 1990, 'max': 2000},
            {'min': 2000, 'max': 2010},
            {'min': 2010, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.00020215088542087814, 0.04079404867793321, 0.17878224306622462,
                         0.1237567720546616, 0.07621088380367105, 0.01960863588582518,
                         0.06739710519932077],
            }
        ]
    }
}
EXPECTED_PRICE_PER_SQFT_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'price_per_sqft': {
        'meta': {
            'median': 265,
            'average': 375,
        },
        'labels': [
            {'min': None, 'max': 730},
            {'min': 730, 'max': 770},
            {'min': 770, 'max': 810},
            {'min': 810, 'max': 850},
            {'min': 850, 'max': 890},
            {'min': 890, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.008490337187676882, 0.04034931673000728, 0.03307188485485566,
                         0.028179833427670414, 0.01738497614619552, 0.05377213552195358],
            }
        ]
    }
}

EXPECTED_PRICE_PER_SQFT_MAX_1_INSIGHTS_RESPONSE = {
    '_total': 148,
    'bottom_text': None,
    'faq': None,
    'price_per_sqft': {
        'meta': {
            'median': 0.8251313865184784,
            'average': 0.7010571096482611,
        },
        'labels': [
            {'min': None, 'max': 0.13},
            {'min': 0.13, 'max': 0.3},
            {'min': 0.3, 'max': 0.47},
            {'min': 0.47, 'max': 0.64},
            {'min': 0.64, 'max': 0.81},
            {'min': 0.81, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.0472972972972973, 0.08108108108108109, 0.13513513513513514,
                         0.07432432432432433, 0.12837837837837837, 0.5337837837837838],
            }
        ]
    }
}


EXPECTED_MEDIAN_CAP_RATE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'median_cap_rate_by_building_type': {
        'labels': ['Single Family', 'Condo'],
        'datasets': [
            {'name': 'median_cap_rate', 'type': 'plain', 'data': [0.025058679498385097, 0.012323684143112567]},
        ]
    }
}


EXPECTED_COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'count_and_median_rent_by_building_type': {
        'labels': ['Single Family', 'Condo'],
        'datasets': [
            {'name': 'median_predicted_rent', 'type': 'plain', 'data': [1629.2710775047258, 1672.1544211195928]},
            {'name': 'cnt', 'type': 'plain', 'data': [14081, 10653]},
        ]
    }
}


EXPECTED_COUNT_AND_PRICE_BY_BUILDING_TYPE_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'count_and_price_by_building_type': {
        'labels': ['Single Family', 'Condo'],
        'datasets': [
            {'name': 'median_price', 'type': 'plain', 'data': [351935.752, 368354.468]},
            {'name': 'cnt', 'type': 'plain', 'data': [14081, 10653]},
        ]
    }
}


EXPECTED_COUNT_AND_PRICE_BY_BUILDING_TYPE_RENT_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'count_and_price_by_building_type': {
        'labels': ['Houses', 'Apartments'],
        'datasets': [
            {'name': 'median_price', 'type': 'plain', 'data': [351935.752, 368354.468]},
            {'name': 'cnt', 'type': 'plain', 'data': [14081, 10653]},
        ]
    }
}


EXPECTED_COUNT_BY_BEDS_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'count_by_beds': {
        'labels': ['0', '1', '2', '3', '4', '5+'],
        'datasets': [{
            'name': 'cnt_fraction',
            'type': 'plain',
            'data': [0.01702110455243794, 0.09759844748119997, 0.3018112719333711,
                     0.3741004285598771, 0.1662488881701302, 0.04321985930298375],
        }]
    }
}


EXPECTED_COUNT_BY_BATHS_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'count_by_baths': {
        'labels': ['1', '1.5', '2', '2.5', '3', '3.5', '4+'],
        'datasets': [{
            'name': 'cnt_fraction',
            'type': 'plain',
            'data': [0.1481361688364195, 0.04568610010511846, 0.4632085388534002,
                     0.08154766717878224, 0.11542815557532142, 0.06990377617853966,
                     0.016980674375353763],
        }]
    }
}


EXPECTED_CAP_RATE_AND_RENT_BY_BEDS_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'cap_rate_and_rent_by_beds': {
        'labels': ['0', '1', '2', '3', '4', '5+'],
        'datasets': [
            {'name': 'median_predicted_rent', 'type': 'plain',
             'data': [1490.0, 1448.5811234817816, 1968.7650303507496, 2753.431818181818, 3797.5,
                      3542.0]},
            {'name': 'median_cap_rate', 'type': 'plain',
             'data': [0.01360000018030405, 0.03098487637457822, 0.031109154334811564,
                      0.026931447506095513, 0.02209333305557569, 0.017133334030707676]},
        ]
    }
}


EXPECTED_COUNT_AND_PRICE_BY_BEDS_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'count_and_price_by_beds': {
        'labels': ['0', '1', '2', '3', '4', '5+'],
        'datasets': [
            {'name': 'median_price', 'type': 'plain',
             'data': [251935.752, 271935.752, 311935.752,
                      351935.752, 451935.752, 551935.752]},
            {'name': 'cnt', 'type': 'plain',
             'data': [284, 4794, 12974, 4584, 1378, 720]},
        ]
    }
}


EXPECTED_CAP_RATE_AND_RENT_BY_BATHS_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'cap_rate_and_rent_by_baths': {
        'labels': ['1', '1.5', '2', '2.5', '3', '3.5', '4+'],
        'datasets': [
            {'name': 'median_predicted_rent', 'type': 'plain',
             'data': [1423.9200000000003, 1736.89, 1929.0081324248779, 2756.9482142857137,
                      2844.446799089069, 2612.375, 3542.0]},
            {'name': 'median_cap_rate', 'type': 'plain',
             'data': [0.032679999619722365, 0.021650000475347042, 0.032077903063295825,
                      0.026471428307039396, 0.026540579449763336, 0.02712963010977816,
                      0.017150000669062138]},
        ]
    }
}


EXPECTED_EST_RENT_DISTRIBUTION_INSIGHTS_RESPONSE = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'est_rent_distribution': {
        'meta': {
            'median_predicted_rent': 2045,
            'median_price': 399922,
            'median_price_per_sqft': 268,
            'median_cap_rate': 0.02959822144124582,
            'average_cap_rate': 0.02816475149083337,
        },
        'labels': [
            {'min': None, 'max': 2400},
            {'min': 2400, 'max': 3000},
            {'min': 3000, 'max': 3600},
            {'min': 3600, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.031090806177731058, 0.5359828576049163, 0.32441174092342523,
                         0.10851459529392739],
            }
        ]
    }
}

EXPECTED_ASKING_PRICE_DISTRIBUTION_INSIGHTS_RESPONSE_RENT = {
    '_total': 24734,
    'bottom_text': None,
    'faq': None,
    'asking_price_distribution': {
        'meta': {
            'median_price': 100560,
            'cnt_good_deals': 0,
            'cnt': 24734,
            'median_days_on_market': 36,
        },
        'labels': [
            {'min': None, 'max': 24000},
            {'min': 24000, 'max': 162600},
            {'min': 162600, 'max': 301200},
            {'min': 301200, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.031090806177731058, 0.5359828576049163, 0.32441174092342523,
                         0.10851459529392739],
            }
        ]
    }
}


EXPECTED_ASKING_PRICE_DISTRIBUTION_INSIGHTS_RESPONSE_BUY = {
    '_total': 24734,
    'bottom_text': None,
    'asking_price_distribution': {
        'meta': {
            'median_price': 100560,
            'cnt_good_deals': 0,
            'cnt': 24734,
            'median_price_per_sqft': 1710906,
        },
        'labels': [
            {'min': None, 'max': 24000},
            {'min': 24000, 'max': 162600},
            {'min': 162600, 'max': 301200},
            {'min': 301200, 'max': None},
        ],
        'datasets': [
            {
                'name': 'cnt_fraction',
                'type': 'plain',
                'data': [0.031090806177731058, 0.5359828576049163, 0.32441174092342523,
                         0.10851459529392739],
            }
        ]
    }
}


SEARCH_STATE_DATA = {
    'type': 'state',
    'state_id': 'FL',
    'start': 0,
    'map_query': True,
    'zoom': 5,
}


INSIGHTS_STATE_DATA = {
    'type': 'state',
    'state_id': 'FL',
}


ES_LARGE_TOTAL_SEARCH_RESPONSE = deepcopy(ES_FLORIDA_SEARCH_RESPONSE)
ES_LARGE_TOTAL_SEARCH_RESPONSE['hits']['total']['value'] = 1000


ES_GRID_BUCKETS_RESPONSE = deepcopy(ES_FLORIDA_SEARCH_RESPONSE)
ES_GRID_BUCKETS_RESPONSE['aggregations'] = {
    'cluster_agg': {
        'buckets': [
             {'key': '9/141/217',
              'doc_count': 380,
              'centroid_agg': {'location': {'lat': 26.625753568240295,
                'lon': -81.98659116108166},
               'count': 380},
              'min_lon': {'value': -84.3745840061456},
              'max_lat': {'value': 34.59086498245597},
              'max_lon': {'value': -83.52244008332491},
              'min_lat': {'value': 33.75013499055058},
            },
             {'key': '9/138/214',
              'doc_count': 291,
              'centroid_agg': {'location': {'lat': 26.627220922178523,
                'lon': -81.78674398806216},
               'count': 291},
              'min_lon': {'value': -87.18142907135189},
              'max_lat': {'value': 36.56217197421938},
              'max_lon': {'value': -85.78208005987108},
              'min_lat': {'value': 35.17204795964062},
            },
             {'key': '9/142/217',
              'doc_count': 88,
              'centroid_agg': {'location': {'lat': 26.25658559115519,
                'lon': -81.7466801227155},
               'count': 88},
              'min_lon': {'value': -85.00609603710473},
              'max_lat': {'value': 34.33299698866904},
              'max_lon': {'value': -84.3750520516187},
              'min_lat': {'value': 33.75004899222404},
            },
             {'key': '9/141/218',
              'doc_count': 80,
              'centroid_agg': {'location': {'lat': 26.13438494905131,
                'lon': -81.7296706099296},
               'count': 80},
              'min_lon': {'value': -84.3723370693624},
              'max_lat': {'value': 33.74997996725142},
              'max_lon': {'value': -83.77352401614189},
              'min_lat': {'value': 33.328245976008475},
            },
             {'key': '9/140/213',
              'doc_count': 53,
              'centroid_agg': {'location': {'lat': 26.466153269668794,
                'lon': -81.81628367107994},
               'count': 53},
              'min_lon': {'value': -85.03274705260992},
              'max_lat': {'value': 33.749926993623376},
              'max_lon': {'value': -84.37543803825974},
              'min_lat': {'value': 33.34783796221018},
            },
             {'key': '9/142/216',
              'doc_count': 26,
              'centroid_agg': {'location': {'lat': 26.50623955656416,
                'lon': -81.96873600379779},
               'count': 26},
              'min_lon': {'value': -87.53598801791668},
              'max_lat': {'value': 36.562327961437404},
              'max_lon': {'value': -87.18928903341293},
              'min_lat': {'value': 35.43877197895199},
            },
             {'key': '9/139/216',
              'doc_count': 16,
              'centroid_agg': {'location': {'lat': 26.765854666591622,
                'lon': -81.98253229202237},
               'count': 16},
              'min_lon': {'value': -87.44473306462169},
              'max_lat': {'value': 36.64159499108791},
              'max_lon': {'value': -87.20654100179672},
              'min_lat': {'value': 36.5633969893679},
            },
             {'key': '9/139/214',
              'doc_count': 15,
              'centroid_agg': {'location': {'lat': 26.73806838132441,
                'lon': -81.8064040504396},
               'count': 15},
              'min_lon': {'value': -87.17682531103492},
              'max_lat': {'value': 36.62396298721433},
              'max_lon': {'value': -86.42692007124424},
              'min_lat': {'value': 36.56256797723472},
            },
             {'key': '9/138/215',
              'doc_count': 3,
              'centroid_agg': {'location': {'lat': 26.83702197857201,
                'lon': -82.28638638742268},
               'count': 3},
              'min_lon': {'value': -85.76971306465566},
              'max_lat': {'value': 35.694112996570766},
              'max_lon': {'value': -85.76971306465566},
              'min_lat': {'value': 35.694112996570766},
            },
             {'key': '9/141/215',
              'doc_count': 3,
              'centroid_agg': {'location': {'lat': 25.986276646144688,
                'lon': -81.71951802447438},
               'count': 3},
              'min_lon': {'value': -85.03274705260992},
              'max_lat': {'value': 33.749926993623376},
              'max_lon': {'value': -84.37543803825974},
              'min_lat': {'value': 33.34783796221018},
            },
        ]
    }
}

ES_HIGH_CAP_RATE_RESPONSE = {
    '_index': 'search-20211116125501',
    '_type': '_doc',
    '_id': 'whatever high',
    '_version': 1,
    '_seq_no': 0,
    '_primary_term': 1,
    'found': True,
    '_source': {'is_high_cap_rate': True}
}

ES_LOW_CAP_RATE_RESPONSE = {
    '_index': 'search-20211116125501',
    '_type': '_doc',
    '_id': 'whatever low',
    '_version': 1,
    '_seq_no': 0,
    '_primary_term': 1,
    'found': True,
    '_source': {'is_high_cap_rate': False}
}


ES_FEAT_KEYWORD_RESPONSE = {
 'took': 2,
 'timed_out': False,
 '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
 'hits': {'total': {'value': 0, 'relation': 'eq'},
  'max_score': None,
  'hits': []},
 'suggest': {'appliances_suggestion': [{'text': 'featur',
    'offset': 0,
    'length': 6,
    'options': []}],
  'description_suggestion': [{'text': 'featur',
    'offset': 0,
    'length': 6,
    'options': [{'text': 'features',
      '_index': 'temp-test-index-00',
      '_type': '_doc',
      '_id': '3',
      '_score': 5.0}]}],
  'features_suggestion': [{'text': 'featur',
    'offset': 0,
    'length': 6,
    'options': [{'text': 'features',
      '_index': 'temp-test-index-00',
      '_type': '_doc',
      '_id': '0',
      '_score': 10.0}]}]}}


EXPECTED_ES_BODY_FLORIDA_SIM_NEARBY = {
    'size': 10,
    'query': {
        'bool': {
            'must': [],
            'must_not': [{'ids': {'values': ['751AB568FFD63EFD8A86',
                                             '8154C17F502066BBB0AB',
                                             'M5454893686']}}],

            'filter': [{'terms': {'status': ['for_sale', 'under_contract']}},
            {
                'geo_distance': {
                    'distance': '20mi',
                    'geo_point': {'lat': 30.436986470595002, 'lon': -94.30447604041547}
                }
            }],
        }
    },
    'sort': [{
        '_geo_distance': {
            'geo_point': {'lat': 30.436986470595002, 'lon': -94.30447604041547},
            'order': 'asc',
            'unit': 'mi',
            'ignore_unmapped': True
        }
    }]
}


ES_AVENTURA_AUTOCOMPLETE_RESPONSE = {
    'took': 2184,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'value': 1, 'relation': 'eq'},
     'max_score': 16.699083,
     'hits': [{'_index': 'autocomplete-20220930142100',
       '_type': '_doc',
       '_id': 'A_jGjoMBVprEqbQIlrsc',
       '_score': 16.699083,
       '_source': {'label': 'Aventura, FL',
        'searchline': 'aventura, miami-dade, FL, Florida',
        'population': None,
        'city': 'aventura',
        'type_priority': 3,
        'county': 'miami-dade-county',
        'state_id': 'fl',
        'type': 'city',
        'is_test': False,
        'category': 'region',
        'geo_point': {'lat': 25.9601599, 'lon': -80.1330108},
        'is_high_cap_rate': False},
       'sort': [3, -9223372036854775808, 9223372036854775807]}]},
}

ES_AVENTURA_AUTOCOMPLETE_AGGS_RESPONSE = {
    'took': 1752,
    'timed_out': False,
    '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'value': 10000, 'relation': 'gte'},
        'max_score': None,
        'hits': []},
    'aggregations': {'aventura_miami-dade-county_fl_rent-prop': {'doc_count': 962},
        'aventura_miami-dade-county_fl_invest-prop': {'doc_count': 701},
        'aventura_miami-dade-county_fl_buy-prop': {'doc_count': 1293}},
}
