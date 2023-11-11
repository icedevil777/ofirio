import base64
import pathlib
import uuid
from datetime import datetime

import numpy as np
import psycopg2
import pandas as pd
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from bs4 import BeautifulSoup
from celery import shared_task
from django.db import connections
from django.conf import settings
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.cache import cache
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.html import strip_tags as django_strip_tags
from ofirio_common.helpers import send_internal_telegram
from psycopg2.extras import RealDictCursor
from rest_framework.throttling import BaseThrottle
from sqlalchemy import create_engine


def get_is_test_condition(table_alias='prop_cache'):
    ''' Returns SQL condition to filter out test properties on production '''

    if settings.IS_PRODUCTION:
        return f' and {table_alias}.is_test = false '
    return ''


def get_is_test_es_filter():
    ''' Returns elastic search filter to filter out test properties on production '''

    if settings.IS_PRODUCTION:
        return [{'term': {'is_test': False}}]
    return []


def zip_to_city(zip_code):
    ''' should lookup city in django cache '''
    if not cache.get('zip_to_city'):
        df = get_us_zips(index='zip', usecols=['zip', 'city'])
        cache.set('zip_to_city', df.to_dict(orient='index'), None)
    return cache.get('zip_to_city').get(zip_code, {}).get('city')


def get_us_zips(index=None, usecols=None):
    path = settings.BASE_DIR / 'data/uszips-cached.csv'
    zip_frame = pd.read_csv(path, converters={'zip': str}, usecols=usecols)
    if index:
        zip_frame.set_index(index, inplace=True)
    return zip_frame


def generate_random_hex_str():
    """Generate random 32-length hex string"""
    return uuid.uuid4().hex


def get_absolute_url(relative_url=''):
    return settings.PROJECT_SCHEME + settings.PROJECT_DOMAIN + relative_url


def datetime_from_unixtime(unixtime):
    """Convert Unix time to timezone-aware datetime object"""
    return timezone.make_aware(datetime.utcfromtimestamp(unixtime))


def _remove_tag(html, tag):
    """Remove first occurence of the tag from the html"""
    tag_open = f'<{tag}>'
    tag_close = f'</{tag}>'
    index_open = html.find(tag_open)
    index_close = html.find(tag_close)
    return html[:index_open] + html[index_close + len(tag_close):]


def strip_tags(html):
    """Convert html to plain text"""
    html = _remove_tag(html, 'style')
    plain = django_strip_tags(html)
    # TODO:
    # - remove any tags that have style="display:none"
    # - replace any number of '\n' > 1 with '\n\n'
    # - replace any number of ' ' > 1 with '  '
    return plain


def read_text_file(path_str, as_safe=False):
    """
    Return content of the provided path's file.
    If path is relative, it is looked starting from settings.BASE_DIR.
    If you need to use file content as part of HTML later,
    you'll find useful 'as_safe' argument, which is False by default
    for the sake of security.
    """
    path = pathlib.Path(path_str)
    if path.absolute() == path:  # is absolute
        fullpath = path
    else:
        fullpath = settings.BASE_DIR / path

    with open(fullpath) as text_file:
        content = text_file.read()

    if as_safe:
        content = mark_safe(content)

    return content


def read_binary_file(path_str):
    """
    Return content of the provided path's file.
    If path is relative, it is looked starting from settings.BASE_DIR
    """
    path = pathlib.Path(path_str)
    if path.absolute() == path:  # is absolute
        fullpath = path
    else:
        fullpath = settings.BASE_DIR / path

    with open(fullpath, 'rb') as bin_file:
        content = bin_file.read()

    return content


def get_ip_address(request):
    ident = BaseThrottle().get_ident(request)
    if ident:
        ip_address = ident.split(',')[0]
        return ip_address


def get_msg_json(request):
    """Form error messages for client"""
    server_messages = []
    for message in messages.get_messages(request):
        server_messages.append({'level': message.level_tag,
                                'message': message.message})
    return server_messages


def extract_first_error(serializer):
    """
    Extract first text error from the provided serializer
    """
    error = ''
    if errors := serializer.errors:

        if isinstance(errors, list):
            error = errors[0]

        elif isinstance(errors, dict):
            error = list(errors.values())[0]
            if error and isinstance(error, list):
                error = error[0]

    error = str(error or '')
    if error.startswith('['):
        error = error.replace("', '", '", "').split('", "')[0][2:]
    if error.endswith(']'):
        error = error[:-2]

    return error


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def notify_telegram(title, data):
    """Format data and title and send internally by Telegram"""
    message = ''
    for key in sorted(data):
        message += f'<b>{key}</b>: {data[key]}\n'
    send_internal_telegram(title, message)


def leave_letters_nums(string, also=''):
    """
    Leave only letters and numbers in provided string,
    or leave a char if it's in 'also'
    """
    result = ''
    for char in string:
        if char.isalpha() or char.isdigit() or char in also:
            result += char
    return result


def get_dict_cursor(db_name='prop_db'):
    if settings.DATABASES[db_name]['ENGINE'] != 'common.custom_sqlite3_backend':
        return get_pg_connection().cursor(cursor_factory=RealDictCursor)
    else:
        # this is unit test
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        con = connections[db_name]
        con.connection.row_factory = dict_factory
        cursor = con.cursor()
    return cursor


def get_soup(html):
    return BeautifulSoup(html, 'html.parser')


def to_num(val, to_int=False, round_to=None):
    """
    Convert a stringable object to integer or float number
    """
    if val is None:
        return

    val_float = float(val)
    val_int = int(val)

    result = val_float
    if to_int or (val_float == val_int):
        result = val_int

    if round_to is not None:
        result = val // round_to * round_to

    return result


def _decompose_secret(secret):
    """
    Decompose secret key to key and IV
    """
    if len(secret) != 32:
        raise ValueError('Secret must be exactly 32 chars')
    key = secret[:16].encode('utf-8')
    iv = secret[16:].encode('utf-8')
    return key, iv


def encrypt(string, secret):
    """
    Encrypt the string with the provided secret.
    Can be decrypted in JS as described here: https://bit.ly/3fcT17J
    """
    key, iv = _decompose_secret(secret)
    data = pad(string.encode(), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    bts = base64.b64encode(cipher.encrypt(data))
    return bts.decode('utf-8', 'ignore')


def decrypt(string, secret):
    """
    Decrypt the string using the provided secret.
    Can be encrypted in JS as described here: https://bit.ly/3fcT17J
    """
    key, iv = _decompose_secret(secret)
    enc = base64.b64decode(string)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    unpadded = unpad(cipher.decrypt(enc), 16)
    return unpadded.decode('utf-8', 'ignore')


def calculate_distance(lat1, lon1, lat2, lon2):
    radlat1 = np.pi * lat1 / 180
    radlat2 = np.pi * lat2 / 180
    theta = lon1 - lon2
    radtheta = np.pi * theta / 180
    dist = (np.sin(radlat1) * np.sin(radlat2) +
            np.cos(radlat1) * np.cos(radlat2) * np.cos(radtheta))

    dist = min(dist, 1)
    dist = np.arccos(dist)
    dist = dist * 180 / np.pi
    dist = dist * 60 * 1.1515
    return dist


def get_pg_connection(alchemy=False, app_name=settings.PROJECT_DOMAIN, db='prop_db'):
    """
    By default returns connection for psycopg2
    """
    user = settings.DATABASES[db]['USER']
    password = settings.DATABASES[db]['PASSWORD']
    dbname = settings.DATABASES[db]['NAME']
    host = settings.DATABASES[db]['HOST']
    port = settings.DATABASES[db]['PORT']

    if alchemy:
        return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")

    return psycopg2.connect(
        f"user={user} password={password} dbname={dbname} host={host} port={port} "
        f"application_name='{app_name}'"
    )


def split_to_chunks(sequence, chunk_size):
    """
    Split the sequence to chunks of the provided size
    """
    chunks_num = len(sequence) / chunk_size
    if chunks_num != int(chunks_num):
        chunks_num = chunks_num + 1
    chunks_num = int(chunks_num)

    chunks = []
    for chunk_idx in range(chunks_num):
        chunk = sequence[chunk_idx * chunk_size:(chunk_idx + 1) * chunk_size]
        chunks.append(chunk)

    return chunks


def humanize_price(price):
    """
    Convert number or string to a string suitable for humans, with a dollar sign.
    If an error occured, return original object
    """
    try:
        human_price = f'${intcomma(round(float(price)))}'
    except (TypeError, ValueError):
        human_price = price
    return human_price
