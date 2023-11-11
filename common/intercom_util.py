import logging
import json

import requests
from django.conf import settings


logger = logging.getLogger('emails')
# TODO: move timeout setting to common place so that klaviyo can use it as well
connect_timeout, read_timeout = 10.0, 60.0
requests_timeout = (connect_timeout, read_timeout)


def send_to_intercom(email, name, body):
    """
    Creates a user in Intercom and creates a conversation starting with the specified message
    """
    if not settings.INTERCOM_ENABLED:
        return

    intercom_addess = 'https://api.intercom.io/'
    headers = {'Authorization': f'Bearer {settings.INTERCOM_TOKEN}',
               'Accept': 'application/json',
               'Content-Type': 'application/json'}
    # find user
    url = intercom_addess + 'contacts/search'
    data = {"query": {"field": "email", "operator": "=", "value": email}}
    r = requests.post(url, json=data, headers=headers, timeout=requests_timeout)
    logger.info('Intercom: POST %s, STATUS %s', url, r.status_code)
    data = json.loads(r.text)
    users = data.get('data', [])
    if len(users):
        user = users[0]
    else:
        # create a user
        url = intercom_addess + 'contacts'
        data = {'role': 'lead', 'name': name, 'email': email}
        r = requests.post(url, json=data, headers=headers, timeout=requests_timeout)
        logger.info('Intercom: POST %s, STATUS %s', url, r.status_code)
        user = json.loads(r.text)
    user_id = user.get('id')

    # create conversation
    url = intercom_addess + 'conversations'
    data = {'from': {'type': 'contact', 'id': user_id}, 'body': body}
    r = requests.post(url, json=data, headers=headers, timeout=requests_timeout)
    logger.info('Intercom: POST %s, STATUS %s', url, r.status_code)
