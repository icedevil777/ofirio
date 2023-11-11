from api_property.common.common import getProp
from api_property.common.prop_representation import build_summary, build_public_records
from api_property.tests.base import PropertyBaseTest


class SummaryTest(PropertyBaseTest):

    def test_sumary(self):
        expected_summary = {
            'beds': 1,
            'baths': 1,
            'year_built': 1975,
            'prop_type': 'Condo',
            'garage': 'No',
            'building_size': 686,
            'price_per_sqft': 71.18,
            'monthly_tax': 30.0,
            'monthly_insurance': 0,
            'hoa_fees': 292.0,
            'lot_size': 3154,
            'construction_type': 'Stucco',
            'heating': 'Central,Electric',
            'cooling': 'Central Air',
            'flooring': 'Carpet,Ceramic Tile,Tile',
        }
        prop = getProp('CC666AC9B5D6B9C22B5C')
        summary = build_summary(prop)
        self.assertEqual(summary, expected_summary)

    def test_humanize_summary(self):
        expected_summary = {
            'Beds': 1,
            'Baths': 1,
            'Year built': 1975,
            'Garage & parking': 'No',
            'Property type': 'Condo',
            'Living area, Sq/ft': 686,
            'Price per Sq/ft': '$71.18',
            'Insurance/mo': 0,
            'HOA Fees': '$292',
            'Property Taxes/mo': '$30',
            'Lot size, Sq/ft': 3154,
            'Construction type': 'Stucco',
            'Heating': 'Central,Electric',
            'Cooling': 'Central Air',
            'Flooring': 'Carpet,Ceramic Tile,Tile',
        }
        prop = getProp('CC666AC9B5D6B9C22B5C')
        summary = build_summary(prop, humanize=True)
        self.assertEqual(summary, expected_summary)


    def test_for_dict(self):
        prop = getProp('CC666AC9B5D6B9C22B5C')
        prop_heat_cool = prop['features']['Interior']['Heating and Cooling']
        self.assertEqual(type(prop_heat_cool), dict)

    def test_public_records(self):
        prop = getProp('M5454893686')
        pr = build_public_records(prop)
        expected_pr = {'Property Type': 'condo',
                        'Size': 532,
                        'Stories': 3,
                        'Bathrooms': 4,
                        'Garage': 'Garage',
                        'Construction': 'Wood Frame',
                        'Exterior Construction': 'Frame/Masonry',
                        'Year Built': 2004,
                        'Cooling': 'Central',
                        'Heating': 'Forced Air',
                        'Fireplace': 'Yes',
                        'Date Updated': '02/05/2021'}
        self.assertEqual(pr, expected_pr)
