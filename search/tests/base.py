from common.tests.base import PortalBaseTest
from search import utils


class SearchBaseTest(PortalBaseTest):
    maxDiff = None

    def find_prop_in_map_response(self, prop_id, response):
        """
        Find a prop with specified id in search response's 'map' content
        """
        map_item = None

        for feature in response.data['map']['features']:
            if feature['type'] == 'Feature':
                if feature['properties']['prop_id'] == prop_id:
                    map_item = nested_feature['properties']

            elif feature['type'] == 'FeatureCollection':
                for nested_feature in feature['features']:
                    if nested_feature['properties']['prop_id'] == prop_id:
                        map_item = nested_feature['properties']

        return map_item
