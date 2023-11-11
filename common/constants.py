class FRONTEND_URLS:
    """
    URLs on frontend. They have no views and so not present in URL conf
    """
    email_confirm_ok = '/msg/email-confirm-ok'
    email_confirm_issue = '/msg/email-confirm-issue'
    email_verification = '/account/verify_email/{code}'
    restore_password = '/restore-password/{restore_code}'
    subscription = '/account/membership'
    msg_payment_fail = '/msg/payment-fail/{msg}'
    msg_payment_success = '/msg/payment-success/{charge}/{price}/{product_id}'


COMPARABLES_TYPE3_TO_UI = {
    'condo-apt': 'Condo & Apts.',
    'house-duplex': 'Single Family',
    'townhouse': 'Townhome',
    'mobile-home': 'Mobile Home',
}
