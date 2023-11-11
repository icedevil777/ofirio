import logging
import re
import time
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.db import connections
from django.utils import timezone
from django.utils.module_loading import import_string

from blog.tests import constants


_wp_client = None
logger = logging.getLogger(__name__)


class BaseWordPressClient:
    """
    Base for WordPress clients. Has logic common between all the clients
    """
    api_url = None
    api_host = None

    def _request_post(self, post_id=None, slug=None, authed=False):
        raise NotImplementedError

    def _request_posts(self, page=None, per_page=9, categories=None, author=None):
        raise NotImplementedError

    def _request_user(self, user_id=None, slug=None, authed=False):
        raise NotImplementedError

    def _request_category(self, category_id=None, slug=None):
        raise NotImplementedError

    def _request_categories(self, page=None, per_page=9):
        raise NotImplementedError

    def _request_media(self, media_id):
        raise NotImplementedError

    def _request_paginated_objects(self, type_=None, _fields=None, per_page=None, page=None):
        raise NotImplementedError

    def get_all_slugs(self, nonempty=False):
        all_posts = self.get_all_paginated_objects('posts')
        all_users = self.get_all_paginated_objects('users')
        all_categories = self.get_all_paginated_objects('categories')

        posts, users, categories = all_posts, all_users, all_categories

        if nonempty:
            # filter posts
            posts = all_posts

            # filter users
            users = []
            for user in all_users:
                raw, headers = self._request_posts(page=1, author=user['id'], per_page=1)
                if int(headers.get('x-wp-total', 0)):
                    users.append(user)

            # filter categories
            categories = [cat for cat in all_categories if cat['count'] > 0]

        return {
            'posts': [post['slug'] for post in posts],
            'users': [user['slug'] for user in users],
            'categories': [category['slug'] for category in categories],
        }

    def get_all_paginated_objects(self, type_, fields=None):
        """
        Return ALL the objects of provided type
        """
        args = {'type_': type_, 'per_page': 100, 'page': 1}
        if fields:
            args['_fields'] = fields
        objects, headers = self._request_paginated_objects(**args)

        pages = int(headers['x-wp-totalpages'])
        if pages >= 2:
            for page in range(2, pages):
                args['page'] = page
                raw, headers = self._request_paginated_objects(**args)
                objects.extend(raw)

        return objects

    def get_user(self, user_id=None, slug=None, authed=False):
        raw, headers = self._request_user(user_id=user_id, slug=slug, authed=authed)
        if raw:
            yoast = raw.get('yoast_head_json', {})
            user = {
                'id': raw.get('id'),
                'full_name': raw.get('full_name'),
                'slug': raw.get('slug'),
                'description': raw.get('description'),
                'avatar': raw.get('avatar_urls', {}).get('96'),
                'meta': {
                    'title': yoast.get('title'),
                    'description': yoast.get('description'),
                },
            }
            return user

    def get_category(self, category_id=None, slug=None):
        raw, headers = self._request_category(category_id=category_id, slug=slug)
        if raw:
            category = self._prepare_category(raw)
            return category

    def get_categories(self, page=None, per_page=9, orderby=None, order=None):
        raw, headers = self._request_categories(
            page=page or 1, per_page=per_page, orderby=orderby, order=order,
        )
        if raw:
            result = {
                'total': headers['x-wp-total'],
                'pages': headers['x-wp-totalpages'],
                'results': [self._prepare_category(c) for c in raw],
            }
            return result

    def _prepare_category(self, raw):
        yoast = raw.get('yoast_head_json', {})
        category = {
            'id': raw['id'],
            'name': raw['name'],
            'slug': raw['slug'],
            'description': raw['description'],
            'count': raw['count'],
            'meta': {
                'title': yoast.get('title'),
                'description': yoast.get('description'),
            },
        }
        return category

    def get_media(self, media_id):
        raw, headers = self._request_media(media_id)
        if raw:
            sizes = raw['media_details']['sizes']
            media = {
                'id': media_id,
                'alt_text': raw['alt_text'],
                'sizes': {
                    'xs': sizes.get('thumbnail', {}).get('source_url'),
                    'sm': sizes.get('medium', {}).get('source_url'),
                    'md': sizes.get('medium_large', {}).get('source_url'),
                    'lg': sizes.get('large', {}).get('source_url'),
                    'xl': sizes.get('1536x1536', {}).get('source_url'),
                    '2xl': sizes.get('2048x2048', {}).get('source_url'),
                    'full': sizes.get('full', {}).get('source_url'),
                },
            }
            return media

    def get_post(self, post_id=None, slug=None, authed=False):
        raw, headers = self._request_post(post_id=post_id, slug=slug, authed=authed)
        if raw:
            return self._prepare_post(raw, headers, authed=authed)

    def _prepare_post(self, raw, headers, author=None, authed=False):
        """
        Convert raw WP post json to our vision
        """
        image = self.get_media(raw['featured_media']) or {}
        content = raw['content']['rendered']
        yoast = raw.get('yoast_head_json', {})
        schema = yoast.pop('schema', {})  # yes, pop
        twitter_reading_time = yoast.get('twitter_misc', {}).get('Est. reading time', '1 minute')

        # copy schema but remove breadcrumbs
        for idx, item in enumerate(schema.get('@graph', [])):
            if item.get('@type') == 'BreadcrumbList':
                schema['@graph'].pop(idx)
                break

        post = {
            'id': raw['id'],
            'title': raw['title']['rendered'],
            'slug': raw['slug'],
            'content': content,
            'description': raw.get('excerpt', {}).get('rendered'),
            'categories': [self.get_category(c) for c in raw['categories']],
            'author': author or self.get_user(raw['author'], authed=authed),
            'date': raw['date_gmt'],
            'modified': raw['modified_gmt'],
            'status': raw['status'],
            'image': image,
            'thumbnail': image.get('sizes', {}).get('sm'),
            'reading_time': f'{twitter_reading_time} read',
            'meta': yoast,
            'schema': schema,
        }
        return post

    def get_posts(self, page=None, categories=None, author=None, full_author=None):
        raw, headers = self._request_posts(page=page or 1, categories=categories, author=author)
        if raw:
            results = []
            for post in raw:
                result = self._prepare_post(post, headers, author=full_author)
                results.append(result)

            posts = {
                'total': int(headers['x-wp-total']),
                'pages': int(headers['x-wp-totalpages']),
                'results': results,
            }
            return posts


class RequestsWordPressClient(BaseWordPressClient):
    """
    WordPress client that uses Requests lib
    (and a bit of SQL querying...)
    """
    api_url = f'{settings.WP_INTERNAL_URL}/wp-json/wp/v2/'
    authed_api_url = f'https://{settings.WP_API_HOST}/wp-json/wp/v2/'
    api_host = settings.WP_API_HOST

    def _get_wp_auth(self):
        """
        Return objects to perform authenticated requests to WP:
        - 'requests' session
        - headers dict
        """
        base_url = f'https://{settings.WP_API_HOST}'
        retries = 0

        while retries < 50:
            retries += 1

            try:
                session = requests.session()

                login_data = {
                    'log': settings.WP_AUTH_USERNAME,
                    'pwd': settings.WP_AUTH_PASSWORD,
                    'wp-submit': 'Log In',
                    'redirect_to': f'https://{settings.WP_API_HOST}/wp-admin/',
                }
                resp = session.post(f'{base_url}/wp-login.php', data=login_data)
                resp = session.get(f'{base_url}/wp-admin/post-new.php')

                nonce = re.findall('var wpApiSettings = .*\;', resp.text)
                nonce = re.sub('^.*\"nonce\"\:\"', '', nonce[0])
                headers = {'X-WP-Nonce': re.sub('\".*$', '', nonce)}
                return session, headers

            except Exception as exc:
                logger.error('Retrying, error in RequestsWordPressClient._get_wp_auth(): %s', exc)
                time.sleep(retries)

        raise RuntimeError('Cant authenticate in WordPress')

    def _extract_special_wp_headers(self, response):
        """
        WP respond some of the info in headers
        """
        special = {}
        for header in response.headers:
            header = header.lower()
            if header.startswith('x-wp-'):
                special[header] = response.headers[header]
        return special

    def _get(self, url, authed=False):
        if authed:
            url = f'{self.authed_api_url}{url}'
            req, req_headers = self._get_wp_auth()
        else:
            url = f'{self.api_url}{url}'
            req, req_headers = requests, {'host': self.api_host}

        resp = req.get(url, headers=req_headers, timeout=420)
        if resp.status_code == 200:
            headers = self._extract_special_wp_headers(resp)
            return resp.json(), headers

        return None, {}

    def _request_post(self, post_id=None, slug=None, authed=False):
        if post_id:
            post, headers = self._get(f'posts/{post_id}', authed=authed)
            if post and post.get('status') not in ('publish', 'draft'):
                return None, {}
            return post, headers

        elif slug:
            resp, headers = self._get(f'posts?slug={slug}')
            return resp[0] if resp else None, headers

        raise ValueError('post_id or slug is required')

    def _request_posts(self, page=None, per_page=9, categories=None, author=None):
        url = f'posts?per_page={per_page}'
        if page:
            url += f'&page={page}'
        if categories:
            url += f'&categories={categories}'
        if author:
            url += f'&author={author}'
        return self._get(url)

    def _request_categories(self, page=None, per_page=9, orderby=None, order=None):
        url = f'categories?per_page={per_page}'
        if page:
            url += f'&page={page}'
        if orderby:
            url += f'&orderby={orderby}'
        if order:
            url += f'&order={order}'
        return self._get(url)

    def _read_user_full_name(self, user_id):
        """
        WP API doesn't respond first_name and last_name.
        Here we simply read it from the WP database
        """
        sql = '''select meta_value from wp_usermeta
                 where user_id=%(user_id)s
                 and meta_key in ("first_name", "last_name")'''
        with connections['wpdb'].cursor() as cursor:
            cursor.execute(sql, {'user_id': user_id})
            result = cursor.fetchall()

        return f'{result[0][0]} {result[1][0]}'

    def _request_user(self, user_id=None, slug=None, authed=False):
        if not user_id and not slug:
            raise ValueError('user_id or slug is required')

        if user_id:
            resp, headers = self._get(f'users/{user_id}', authed=authed)
        elif slug:
            resp, headers = self._get(f'users?slug={slug}', authed=authed)
            resp = resp[0] if resp else None

        if resp:
            resp['full_name'] = self._read_user_full_name(resp['id'])
            return resp, headers

        return None, headers

    def _request_category(self, category_id=None, slug=None):
        if category_id:
            return self._get(f'categories/{category_id}')
        elif slug:
            resp, headers = self._get(f'categories?slug={slug}')
            return resp[0] if resp else None, headers
        raise ValueError('category_id or slug is required')

    def _request_media(self, media_id):
        return self._get(f'media/{media_id}', authed=True)

    def _request_paginated_objects(self, type_=None, _fields=None, per_page=None, page=None):
        """
        Get any paginable WP objects, with the only fields specified in _fields
        """
        args = {'per_page': per_page, 'page': page}
        if _fields:
            args['_fields'] = _fields
        query = urlencode(args)
        return self._get(f'{type_}/?{query}')


class DummyWordPressClient(BaseWordPressClient):
    """
    Does not perform real requests,
    suitable for testing
    """
    api_url = 'https://rsprjblog.ofirio.com/wp-json/wp/v2/'

    def _request_post(self, post_id=None, slug=None, authed=False):
        if post_id == 1 or slug == 'hello-world':
            return constants.WP_POST_1, {}
        if post_id == 3 or slug == 'houses':
            return constants.WP_POST_3, {}
        return None, {}

    def _request_posts(self, page=None, per_page=9, categories=None, author=None):
        if categories == 3:  # exists, but empty
            return [], {'x-wp-total': 0, 'x-wp-totalpages': 0}
        return (
            [constants.WP_POST_1, constants.WP_POST_1],
            {'x-wp-total': '3', 'x-wp-totalpages': '2'},
        )

    def _request_user(self, user_id=None, slug=None, authed=False):
        if user_id == 1 or slug == 'ofirio_author':
            res = constants.WP_USER_1
            res['full_name'] = 'Ofirio Author'
            return res, {}
        return None, {}

    def _request_category(self, category_id=None, slug=None):
        if category_id == 1 or slug == 'uncategorized':
            return constants.WP_CATEGORY_1, {}
        if category_id == 3 or slug == 'cat3':
            return constants.WP_CATEGORY_3, {}
        return None, {}

    def _request_categories(self, page=None, per_page=9, orderby=None, order=None):
        return (
            [constants.WP_CATEGORY_1, constants.WP_CATEGORY_3],
            {'x-wp-total': '3', 'x-wp-totalpages': '2'},
        )

    def _request_media(self, media_id):
        if media_id == 7:
            return constants.WP_MEDIA_7, {}
        return None, {}

    def _request_paginated_objects(self, type_=None, _fields=None, per_page=None, page=None):
        if type_ == 'posts':
            return (
                [constants.WP_POST_1, constants.WP_POST_3],
                {'x-wp-total': '3', 'x-wp-totalpages': '2'},
            )
        if type_ == 'users':
            return (
                [constants.WP_USER_1],
                {'x-wp-total': '1', 'x-wp-totalpages': '1'},
            )
        if type_ == 'categories':
            return (
                [constants.WP_CATEGORY_1, constants.WP_CATEGORY_3],
                {'x-wp-total': '3', 'x-wp-totalpages': '2'},
            )


def get_wp_client():
    """
    Return WordPress client instance based on WP_CLIENT_CLASS setting
    """
    global _wp_client
    if _wp_client is None:
        try:
            klass = import_string(settings.WP_CLIENT_CLASS)
        except (AttributeError, ImportError):
            klass = RequestsWordPressClient
        _wp_client = klass()
    return _wp_client
