import json
import logging

from django.core.cache import cache as dj_cache
from rest_framework.response import Response


logger = logging.getLogger('cache')
TIMEOUT = 5 * 60  # 5 minutes


def _construct_key(request):
    """
    Construct key for cache value, sorting input dicts: query and body
    """
    data = {k: request.data[k] for k in sorted(request.data)}
    query = {k: request.query_params[k] for k in sorted(request.query_params)}
    key = f'{request.path}|{query}|{json.dumps(data)}'
    return key


def cache_method(method):
    """
    Cache request based on URL and payload.
    Authorization does not count!
    """
    def wrapper(view, request, *args, **kwargs):
        key = _construct_key(request)

        if cache_res := dj_cache.get(key):
            if 'data' in cache_res and 'status' in cache_res:
                logger.info('Got response from cache: %s', request.path)
                return Response(cache_res['data'], status=cache_res['status'])

        response = method(view, request, *args, **kwargs)
        value = {'data': response.data, 'status': response.status_code}
        dj_cache.set(key, value, TIMEOUT)

        return response

    return wrapper


def cache_method_unauth(method):
    """
    Cache unauthorized request based on URL and payload
    """
    def wrapper(view, request, *args, **kwargs):
        key = _construct_key(request)

        if not request.user.is_authenticated:
            if cache_res := dj_cache.get(key):
                if 'data' in cache_res and 'status' in cache_res:
                    logger.info('Got response from cache: %s', request.path)
                    return Response(cache_res['data'], status=cache_res['status'])

        response = method(view, request, *args, **kwargs)
        if not request.user.is_authenticated:
            value = {'data': response.data, 'status': response.status_code}
            dj_cache.set(key, value, TIMEOUT)

        return response

    return wrapper


def simple_cache_by_static_key(key, timeout=TIMEOUT):
    """
    To cache result of any function or method when there is no incoming arguments.
    Returns decorator which uses provided key when working with cache
    """
    def cache_method(method):

        def wrapper(*args, **kwargs):
            if cache_res := dj_cache.get(key):
                return cache_res

            result = method(*args, **kwargs)
            dj_cache.set(key, result, timeout)
            return result

        return wrapper

    return cache_method


def cache_for_timeout(timeout):
    """
    To cache result of any function or method for specific timeout.
    Returns decorator which uses provided timeout
    """
    def cache_method(method):

        def wrapper(view, request, *args, **kwargs):
            key = _construct_key(request)
            if cache_res := dj_cache.get(key):
                if 'data' in cache_res and 'status' in cache_res:
                    logger.info('Got response from cache: %s', request.path)
                    return Response(cache_res['data'], status=cache_res['status'])

            response = method(view, request, *args, **kwargs)
            value = {'data': response.data, 'status': response.status_code}
            dj_cache.set(key, value, timeout)
            return response

        return wrapper

    return cache_method
