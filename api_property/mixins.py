from copy import deepcopy

from ofirio_common.helpers import get_elastic_search


class ElasticSearchMixin:

    ES_BODY = {}

    def get_es_body(self, *args, **kwargs):
        return self.ES_BODY

    def get_objects(self, index: str, es_body=None, *args, **kwargs):
        elastic = get_elastic_search()
        body = es_body or self.get_es_body()
        return elastic.search(body=body, index=index)


class LastSearchESRecommendationMixin(ElasticSearchMixin):

    def get_es_body(self, last_search_params=None) -> dict:
        if not last_search_params:
            return super().get_es_body()

        ls_type = last_search_params.get('type')
        ls_field = last_search_params.get('type')
        if ls_type in ('city', 'county'):
            ls_field += '_url'
        elif ls_type == 'state':
            ls_field += '_id'
        ls_value = last_search_params.get(ls_field)

        if ls_field and ls_value:
            body = deepcopy(super().get_es_body())
            body['query']['bool']['must'].append({'match': {
                ls_field: ls_value if ls_type != 'state' else ls_value.upper()
            }})
            if ls_type and ls_type != 'state' and last_search_params.get('state_id'):
                body['query']['bool']['must'].append({'match': {
                    'state_id': last_search_params.get('state_id').upper()
                }})
            return body
        return super().get_es_body()
