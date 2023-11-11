# TODO: seems like we don't need this file here anymore
''' copied from ../playground/processing/common/prop_type_mapping.py '''

prop_type3_mapping = {
    'Condo': 'condo-apt',
    'Condominium': 'condo-apt',
    #'Townhouse': 'condo-apt',
    'Townhouse': 'townhouse',
    'Condominium': 'condo-apt',
    'Apartment': 'condo-apt',
    'Condo/Coop': 'condo-apt',
    'Co-op': 'condo-apt',
    #'Townhouse Condominium': 'condo-apt',
    'Townhouse Condominium': 'townhouse',
    'Condominium Rental': 'condo-apt',
    #'Condo/Townhome': 'condo-apt',
    'Condo/Townhome': 'townhouse',
    #'Townhome': 'condo-apt',
    'Townhome': 'townhouse',
    'Condop': 'condo-apt',
    #'Attached (Townhouse/Rowhouse/Duplex)': 'condo-apt',
    'Attached (Townhouse/Rowhouse/Duplex)': 'townhouse',
    'Villa': 'condo-apt',
    'Mid/Hi-Rise Condominium': 'condo-apt',
    'Condo/TH': 'condo-apt',
    'Condominium (Rental)': 'condo-apt',
    'Condo/Coop/Villa': 'condo-apt',
    'Villa Attached': 'condo-apt',
    #'Condo/Townhse': 'condo-apt',
    'Condo/Townhse': 'townhouse',
    #'Condo/Townhouse': 'condo-apt',
    'Condo/Townhouse': 'townhouse',
    'Condo/Co-Op': 'condo-apt',
    'Co-Op': 'condo-apt',
    'Co-Operative': 'condo-apt',
    #'Condo/Coop/Townhouse': 'condo-apt',
    'Condo/Coop/Townhouse': 'townhouse',
    'Condo - Hotel': 'condo-apt',
    'Condo|Co-op': 'condo-apt',
    'Villa Detached': 'condo-apt',
    #'Townhouse/Villa': 'condo-apt',
    'Townhouse/Villa': 'townhouse',
    'Manor/Village': 'condo-apt',
    'Condotel Lease': 'condo-apt',
    'Coop': 'condo-apt',
    'Single': 'house-duplex',
    'Single Family Attached Lease': 'house-duplex',
    'Single Family Detached': 'house-duplex',
    'Single Family Residence': 'house-duplex',
    'Single Family': 'house-duplex',
    'Single Family Rental': 'house-duplex',
    'House/Building': 'house-duplex',
    'House for Rent': 'house-duplex',
    'Single-Family Homes': 'house-duplex',
    'House (Rental)': 'house-duplex',
    'Single Family Attached': 'house-duplex',
    'Single Family Home': 'house-duplex',
    'Single Family Lease': 'house-duplex',
    'Single Family/Detach': 'house-duplex',
    'Single Family Attached Lease': 'house-duplex',
    'Single-Family Lease': 'house-duplex',
    'Residence/Single Family': 'house-duplex'
}
prop_type3_mapping.update({k.lower(): v for k, v in prop_type3_mapping.items()})


def get_prop_type3(prop_type):
    if not prop_type:
        return None
    pt = prop_type.replace(' ', '')  # XXX: preprocess_rent has another mapping
    return prop_type3_mapping.get(prop_type) or prop_type3_mapping.get(pt)
