from search.constants import PropType3


# cleaned_prop_type mapped to klaviyo categories in Buy/Invest feeds
KLAVIYO_PROP_TYPE_SALES = {
    PropType3.CONDO_APT: 'Condo',
    PropType3.HOUSE_DUPLEX: 'Single Family',
    PropType3.TOWNHOUSE: 'Townhome',
}

# cleaned_prop_type mapped to klaviyo categories in RENT feeds
KLAVIYO_PROP_TYPE_RENT = {
    PropType3.CONDO_APT: 'Apartments',
    PropType3.HOUSE_DUPLEX: 'Houses',
    PropType3.TOWNHOUSE: 'Townhome',
}
