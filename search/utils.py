import itertools
import logging
import math
import re
from collections import defaultdict

from ofirio_common.enums import EsIndex
from ofirio_common.helpers import get_elastic_search
from rest_framework import exceptions


logger = logging.getLogger(__name__)


def es_grid_centroid_to_geojson(buckets):
    """
    Convert ElasticSearch geohash_grid buckets
    with subaggregation geo_centroid to geojson format
    """
    features = []
    for bucket in buckets:
        point = bucket['centroid_agg']['location']
        feature = {
            'type': 'Feature',
            'properties': {
                'count': bucket['doc_count'],
                'geo_bounds': [bucket['max_lat']['value'], bucket['max_lon']['value'],
                               bucket['min_lat']['value'], bucket['min_lon']['value']],
                'FeatureType': 'Cluster',
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [point['lon'], point['lat']],
            }
        }
        features.append(feature)

    geojson = {'type': 'FeatureCollection', 'features': features}
    return geojson


def es_items_to_nested_geojson(items):
    """
    Convert returned ElasticSearch items to geojson format.
    It is not a valid geojson: we group items with the same geo_point
    into a nested FeatureCollection dict. It is required by client.
    To visualize the data by a 3rd party viewer,
    flatting nested FeatureCollections would be enough
    """
    geo_groups = defaultdict(list)
    for item in items:
        point = item.pop('geo_point')  # field is not needed anymore
        coordinates = (point['lon'], point['lat'])
        geo_groups[coordinates].append(item)

    features = []
    for coordinates, items_group in geo_groups.items():
        group_features = []
        for item in items_group:
            item_feature = {
                'type': 'Feature',
                'properties': item,
                'geometry': {
                    'type': 'Point',
                    'coordinates': coordinates,
                }
            }
            group_features.append(item_feature)

        if len(group_features) == 1:
            features.append(_add_short_line(group_features)[0])
        else:
            collection = {
                'type': 'FeatureCollection',
                'features': _add_short_line(group_features, collection=True),
            }
            features.append(collection)

    geojson = {'type': 'FeatureCollection', 'features': features}
    return geojson


def _add_short_line(feature, collection=False):
    line = feature[0].get('properties', {}).get('address', '').split(', ')[0]
    if collection:
        line = re.sub(r'( #\w+)', '', line)
    feature[0].get('properties', {})['line_short'] = line
    return feature


def estimate_cluster_precision(points):
    """
    Calculate geotile precision based on input polygon points.
    Points are expected in (lon, lat) format.
    """
    lons, lats = zip(*points)
    lat_diff = abs(max(lats) - min(lats))
    lon_diff = abs(max(lons) - min(lons))
    zoom = int(abs(math.log((lat_diff + lon_diff) / 1600, 2)))
    return zoom + 1


def prepare_polygon(polygon):
    """
    Prepare polygon for Elastic:
    - remove repeated points
    - remove points inside a line
    - copy first point to last position
    """
    fixed = []
    last_idx = len(polygon) - 1

    for idx, point in enumerate(polygon):
        uniq = point not in fixed

        if idx in (0, last_idx):
            in_line = False
        else:
            lon, lat = point
            prev_lon, prev_lat = polygon[idx-1]
            next_lon, next_lat = polygon[idx+1]
            in_line = lat == prev_lat == next_lat or lon == prev_lon == next_lon

        if uniq and not in_line:
            fixed.append(point)

    fixed.append(polygon[0])

    return fixed


def group_close_points(points_dict, treshold, diagonal_by=None):
    """
    Group close objects. Only in pairs, but it is enough for now.
    Params:
    - points_dict: dict where a key is a (x, y) tuple representing a point,
      and a value is any object (some content related to the point)
    - treshold: ratio, a float from 0 to 1,
      determines how close the points should be to being grouped
    - diagonal_by: list of points. If present, the base diagonal calculates on it.
    Result is a dict with {center_point: [objects], ...} structure. center_point can be
    one of the input points, or a calculated center of two grouped points,
    if they where close enough. A value (list) may consist of one (not grouped)
    or two (grouped) objects.
    """
    points = list(points_dict.keys())
    groups = _pair_close_points(points, treshold, diagonal_by=diagonal_by)

    result = defaultdict(list)
    for point, group_points in groups.items():
        for group_point in group_points:
            result[point].append(points_dict[group_point])

    return dict(result)


def _pair_close_points(points, treshold, diagonal_by=None):
    """
    Group close points by pairs. If you want to have more than two points in a group,
    use this function as a basis.
    Params:
    - points: collection of (x, y) tuples
    - treshold: ratio, a float from 0 to 1,
      determines how close the points should be to being grouped
    - diagonal_by: list of points. If present, the base diagonal calculates on it
    Result:
    - groups: dict where a key is a center of a group, and a value is a set of points.
      Each set can only has from one to two points. If a point is in a group, it will not
      be present in other groups
    """
    groups = defaultdict(set)
    points_processed = set()
    xs, ys = zip(*(diagonal_by or points))
    diagonal = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
    distance_treshold = treshold * diagonal

    for pa, pb in itertools.combinations(points, 2):
        if pa in points_processed or pb in points_processed:
            continue
        distance = ((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2) ** 0.5
        if distance < distance_treshold:
            center = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
            groups[center].update([pa, pb])
            points_processed.update([pa, pb])

    for point in points:
        if point not in points_processed:
            groups[point].add(point)

    return groups


def request_elastic(body, index=EsIndex.SEARCH_INVEST):
    # logger.warning(body)  # to easily debug the requests
    try:
        elastic = get_elastic_search()
        resp = elastic.search(index=index, body=body)
        return resp
    except Exception as exc:
        logger.exception(exc)
        raise exceptions.ValidationError(f'{exc}')


def round_distance(dist):
    """
    Round distance to it show to the user
    """
    dist = (dist or 0)
    if dist <= 1:
        dist = round(dist, 1)
    else:
        dist = int(round(dist, 0))
    if dist == 0:
        dist = 0.1
    return dist
