"""
Functions to convert Prop from database object to representation.
Maybe this would be moved somewhere later
"""
import re

from common.utils import humanize_price


# Mapping of the keys of property's Summary
SUMMARY_HUMAN_KEYS = {
    'beds': 'Beds',
    'baths': 'Baths',
    'year_built': 'Year built',
    'garage': 'Garage & parking',
    'prop_type': 'Property type',
    'building_size': 'Living area, Sq/ft',
    'price_per_sqft': 'Price per Sq/ft',
    'monthly_insurance': 'Insurance/mo',
    'hoa_fees': 'HOA Fees',
    'monthly_tax': 'Property Taxes/mo',
    'lot_size': 'Lot size, Sq/ft',
    'construction_type': 'Construction type',
    'heating': 'Heating',
    'cooling': 'Cooling',
    'flooring': 'Flooring',
}

PUBLIC_RECORDS_UI_NAMES = {
    'prop_type': 'Property Type',
    'sqft': 'Size',
    'rooms': 'Rooms',
    'units': 'Units',
    'stories': 'Stories',
    'beds': 'Bedrooms',
    'baths': 'Bathrooms',
    'baths_full': 'Baths Full',
    'baths_half': 'Baths Half',
    'view': 'View',
    'style': 'Style',
    'pool': 'Pool',
    'garage': 'Garage',
    'garage_spaces': 'Garage Spaces',
    'construction': 'Construction',
    'Exterior Construction': 'Exterior Construction',
    'year_built': 'Year Built',
    'year_renovated': 'Year Renovated',
    'zoning': 'Zoning',
    'cooling': 'Cooling',
    'heating': 'Heating',
    'roofing': 'Roofing',
    'fireplace': 'Fireplace',
    'lot_size': 'Lot size',
    'date_updated': 'Date Updated',
}
SUMMARY_PRICE_KEYS = (
    'monthly_tax', 'monthly_insurance',
    'hoa_fees',
)


def build_public_records(prop):
    data = prop.get('public_records')
    if not data:
        return {}
    if isinstance(data, dict) and data.get('Property Type', ''):
        data["Property Type"] = data.get("Property Type", '').replace('_', ' ')

    if isinstance(data, list):
        if len(data):
            data = data[0]
        else:
            return {}

    # TODO: it's an adapter for new public records structure.
    # remove build_public_records function after full DB update
    first_letter = list(data.keys())[0][0]
    if first_letter != first_letter.lower():
        # if the key starts with an uppercase letter, structure is already remapped
        return data

    to_remove = (
        'cl_id',
        'baths_1qtr',
        'baths_3qtr',
        'distinct_baths',
    )
    for key in to_remove:
        data.pop(key, None)

    # merge exterior1 and exterior2 if present
    if ext1 := data.get('exterior1'):
        data['Exterior Construction'] = ext1
        if ext2 := data.get('exterior2'):
            data['Exterior Construction'] += ', ' + ext2

    # sort and rename fields
    res = {}
    for key, ui_name in PUBLIC_RECORDS_UI_NAMES.items():
        value = data.get(key)
        # filter empty values
        if value is not None and value != '':
            if isinstance(value, list):
                value = ', '.join(value)
            res[ui_name] = value
    return res


# obsolete but left as example
def get_pool_info(features):
    # currently returns only Yes or No
    exterior = features.get('Exterior', {}).get('Pool and Spa', {})
    if any(key in exterior for key in ('Pool Features',
                                       'Pool Private',
                                       'Pool Size')):
        return 'Yes'

    community = (features.get('Community', {})
                         .get('Amenities and Community Features', ''))
    # based on underlying structure, community may be dict or string here
    if re.search(r'\bPool\b', str(community), re.IGNORECASE):
        return 'Yes'

    return 'No'


def get_garage_info(garage, features):

    #replace bool values
    if garage==False: garage = 0
    if garage==True: garage = 1

    if isinstance(garage, int) and garage != 0:
        return garage
    elif isinstance(garage, str) and garage.lower() == 'yes':
        return 'Yes'
    parking = (features.get('Exterior', {})
                       .get('Garage and Parking', {}))
    parking = parking.get('Parking Features', '') if isinstance(parking, dict) else ''
    r = r'(\d)'
    # if we have parking features, there must be some garage
    garage_info = 'Yes' if parking else 'No'
    search = re.search(r, parking, re.IGNORECASE)
    if search:
        return int(search.group(1))
    return garage_info


def get_flooring(interior):
    f = interior.get('Interior Features', {})
    if isinstance(f, dict):
        return f.get('Flooring', '-')
    return '-'


def get_construction(features):
    f = features.get('Building and Construction', {})
    if isinstance(f, dict):
        return f.get('Construction Materials', '-')
    else:
        return None


def get_heating(heating_cooling):
    if isinstance(heating_cooling, dict):
        return heating_cooling.get('Heating Features') or heating_cooling.get('Heating') or '-'
    else:
        return None


def get_cooling(heating_cooling):
    if isinstance(heating_cooling, dict):
        return heating_cooling.get('Cooling Features') or heating_cooling.get('Cooling') or '-'
    else:
        return None


def get_prop_type_ui(prop_type3, prop_class='sales'):
    UI_TYPE3 = {
        'condo-apt': 'Condo' if prop_class=='sales' else 'Apartment',
        'house-duplex': 'Single Family',
        'townhouse': 'Townhome',
        'mobile-home': 'Mobile Home'
    }
    return UI_TYPE3.get(prop_type3, '-')


def build_summary(prop, prop_class='sales', off_market=False, cant_show_price=False, humanize=False):
    data = prop['data']
    features = prop['features']
    garage = data['garage']
    garage_info = get_garage_info(garage, features)

    interior = features.get('Interior', {})
    heating_cooling = interior.get('Heating and Cooling', {})
    heating = get_heating(heating_cooling)
    cooling = get_cooling(heating_cooling)
    prop_type = get_prop_type_ui(data['prop_type3'], prop_class=prop_class)

    summary = {
        'beds':                 data.get('beds'),
        'baths':                data.get('baths'),
        'year_built':           data.get('year_built') or '-',
        'garage':               garage_info,
        'building_size':        data.get('building_size') or '-',
        'prop_type':            prop_type,
        'heating':              heating,
        'cooling':              cooling,
    }
    if prop_class == 'rent':
        summary['pets'] = 'Allowed' if prop['params'].get('pet_friendly') else 'Not Allowed'
        if laundry := features.get('Features', {}).get('Laundry Features', {}).get('Laundry'):
            summary['laundry'] = laundry
        else:
            summary['laundry'] = 'In unit' if 'laundry' in data.get('cleaned_amenities', '') else '-'
    if prop_class == 'sales':
        flooring = get_flooring(interior)
        construction = get_construction(features)
        summary['flooring'] = flooring
        summary['monthly_tax'] = data.get('monthly_tax')
        summary['monthly_insurance'] = data.get('monthly_insurance')
        summary['hoa_fees'] = data.get('hoa_fees')
        summary['construction_type'] = construction
        if not off_market:
            summary['lot_size'] = data.get('lot_size')
            summary['price_per_sqft'] = data.get('price_per_sqft') if not cant_show_price else None
    if humanize:
        summary = _humanize_summary(summary)
    return summary


def _humanize_summary(summary):
    for price_key in SUMMARY_PRICE_KEYS:
        if price := summary.get(price_key):
            summary[price_key] = humanize_price(price)
    summary['price_per_sqft'] = f'${round(summary.get("price_per_sqft", ""), 2)}'
    summary['status'] = humanize_status(summary.get('status'))
    human_summary = {human_key: summary[key] for key, human_key in SUMMARY_HUMAN_KEYS.items()}
    return human_summary


def humanize_status(status):
    """Humanize property status"""
    status = (status or '').replace('_', ' ')
    splitted = [s.capitalize() for s in status.split(' ')]
    return ' '.join(splitted)
