from account.enums import AccessType


class USER_WARNINGS:
    terms_of_use_not_accepted = 'terms_of_use_not_accepted'
    password_change_required = 'password_change_required'


# how many times anonymous user can request each resource
ANON_LIMITS = {
    AccessType.RENT_ANALYZER_SEARCH: 1,
    AccessType.RENT_ESTIMATOR_ANALYTICS: 1,
    AccessType.PROPERTY_REPORT: 0,
    AccessType.RENT_ANALYZER_REPORT: 0,
}
