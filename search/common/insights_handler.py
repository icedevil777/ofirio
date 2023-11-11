import math
from collections import defaultdict

from ofirio_common.enums import PropEsIndex
from rest_framework.exceptions import NotFound

from common.utils import to_num
from search.constants import INT_MEDIAN_AVG_RANGE_INSIGHTS, PERCENTILE_95_BASED_INSIGHTS
from search.enums import InsightType, PropType3, PropType3Rent
from search.utils import request_elastic


class InsightsHandler:

    def __init__(self, _es_constructor):
        self._es_constructor = _es_constructor

    def get_insights(self, index, insights=None):
        if not insights:
            insights = []

        if InsightType.ASKING_PRICE not in insights:
            requested_insights_ = insights + [InsightType.ASKING_PRICE]
            # we should use request asking price all time but if it's not indicated in input
            # we should not show it in output
        else:
            requested_insights_ = insights.copy()

        if index == PropEsIndex.SEARCH_INVEST:
            # needed for widget info
            requested_insights_.append(InsightType.CAP_RATE)

        # 1. Request Elasticsearch for base values
        base_vals = {}
        if base_vals_body := self.construct_es_base_vals_body(requested_insights_):
            base_vals = self.get_es_base_vals(requested_insights_, base_vals_body, index)
            #requested_insights_, base_vals = self.validate_perc_insights(requested_insights_, base_vals)

        # 2. Request Elasticsearch for main values based on base values
        main_body = self.get_main_es_body(requested_insights_, base_vals, index)
        main_es_resp = request_elastic(main_body, index=index)

        # 3. Convert data for a client
        return self.get_response_data(insights, main_es_resp, index)

    def validate_perc_insights(self, insights, base_vals):
        """for some fields(for ex year_built case it can be none) base_vals var
            could contain none so this func drop insights from requested_insights
            and we just don't return these insights at all"""
        for insight in insights:
            if insight in PERCENTILE_95_BASED_INSIGHTS:
                field = PERCENTILE_95_BASED_INSIGHTS[insight]
                perc95_field = f'{field}_percentile_95'
                perc5_field = f'{field}_percentile_5'
                if None in (base_vals.get(perc5_field), base_vals.get(perc95_field)):
                    insights.remove(insight)
                    base_vals.pop(perc5_field)
                    base_vals.pop(perc95_field)
        return insights, base_vals

    def construct_es_base_vals_body(self, requested_insights):
        """
        Construct ES query body for base values
        """
        body = {
            'size': 0,
            'query': self._es_constructor.get_es_query(),
            'aggs': {},
        }
        for insight in requested_insights:
            if insight in PERCENTILE_95_BASED_INSIGHTS:
                field = PERCENTILE_95_BASED_INSIGHTS[insight]
                body['aggs'][f'{field}_percentiles'] = self.construct_percentiles_agg(field, 5, 95)
        return body if body['aggs'] else {}

    def get_es_base_vals(self, requested_insights, es_body, index):
        """
        Request Elastic with provided body,
        and extract base values from the response
        """
        vals = {}
        resp = request_elastic(es_body, index=index)
        if resp['hits']['total']['value'] == 0:
            raise NotFound

        aggs = resp['aggregations']
        for insight in requested_insights:
            if insight in PERCENTILE_95_BASED_INSIGHTS:
                field = PERCENTILE_95_BASED_INSIGHTS[insight]
                percentiles = aggs[f'{field}_percentiles']['values']
                vals[f'{field}_percentile_95'] = percentiles['95.0']
                vals[f'{field}_percentile_5'] = percentiles['5.0']
        return dict(vals)

    def construct_median_avg_range_agg(self, insight, base_vals, step_count, round_to=None,
                                       negative_col=False, start=None, step=None):
        field = PERCENTILE_95_BASED_INSIGHTS[insight]
        if start is None:
            start = base_vals[f'{field}_percentile_5']

        percentile = base_vals[f'{field}_percentile_95']
        aggs = {
            f'{insight}_median': self.construct_percentiles_agg(field, 50),
            f'{insight}_average': self.construct_agg(field, 'avg'),
            f'{insight}_dist': self.construct_range_agg(
                field, percentile, step_count, round_to=round_to, negative_col=negative_col,
                start=start, step=step,
            ),
        }
        if insight == InsightType.ASKING_PRICE:
            # OT-2444: it's required to additionally find min price
            aggs[f'{insight}_min'] = self.construct_agg(field, 'min')
        return aggs

    def construct_percentiles_agg(self, field, *percents):
        """
        Construct a 'percentiles' aggregation for the provided field in ES body
        """
        if not percents:
            raise ValueError('percents not specified')
        composite_field = self._get_composite_field(field)
        return {
            'percentiles': {
                'keyed': True, 'field': composite_field, 'percents': list(percents),
            },
        }

    def construct_agg(self, field, agg):
        """
        Construct aggregation for the provided field.
        agg may be 'min', 'max', 'avg', etc...
        """
        composite_field = self._get_composite_field(field)
        return {agg: {'field': composite_field}}

    def construct_range_agg(self, field, percentile, step_count, round_to=None,
                            negative_col=False, start=None, step=None, before_start=True):
        """
        Construct a 'range' aggregation for the provided field.
        """
        band = percentile - (start or 0)
        magnitude = calc_magnitude(band)

        # calculate step
        if step is None:
            step = band / (step_count + 1)
            if (round_to or 0) >= 1 or magnitude >= 1:
                step = int(step) or 1
        if round_to is not None:
            step = step // round_to * round_to
        step = round(step, 1 - magnitude)

        # calculate start
        start = step if start is None else start
        if (round_to or 0) >= 1 or magnitude >= 1:
            start = int(start)
        if round_to is not None:
            start = start // round_to * round_to
        start = round(start, 1 - magnitude)

        # range for first bucket
        agg_ranges = []
        if before_start:
            if negative_col:
                agg_ranges.append({'to': 0})
            else:
                agg_ranges.append({'to': start})

        # ranges for middle buckets
        for i in range(0, step_count):
            step_from = round(start + step * i, 1 - magnitude)
            step_to = round(step_from + step, 1 - magnitude)
            agg_ranges.append({'from': step_from, 'to': step_to})

        agg_ranges.append({'from': step_to})  # range for final bucket
        composite_field = self._get_composite_field(field)
        return {'range': {'field': composite_field, 'keyed': True, 'ranges': agg_ranges}}

    def construct_terms_agg(self, field):
        """
        Construct a 'terms' aggregation for the provided field
        """
        composite_field = self._get_composite_field(field)
        return {'terms': {'field': composite_field}}

    def get_main_es_body(self, requested_insights, base_vals, index):
        body = {
            'size': 0,
            'track_total_hits': True,
            'query': self._es_constructor.get_es_query(),
            'aggs': {},
        }

        for insight in requested_insights:

            aggs = {}

            if insight == InsightType.ASKING_PRICE:
                aggs = self.construct_median_avg_range_agg(insight, base_vals, 4)

            if insight == InsightType.EST_RENT:
                aggs = self.construct_median_avg_range_agg(insight, base_vals, 4, round_to=10)

            if insight == InsightType.CAP_RATE:
                aggs = self.construct_median_avg_range_agg(insight, base_vals, 5, start=0.01)
            if insight == InsightType.SQFT:
                aggs = self.construct_median_avg_range_agg(insight, base_vals, 4, round_to=10)

            if insight == InsightType.YEAR_BUILT:
                aggs = self.construct_median_avg_range_agg(insight, base_vals, 5, round_to=10,
                                                           start=1960, step=10)
            if insight == InsightType.PRICE_PER_SQFT:
                aggs = self.construct_median_avg_range_agg(insight, base_vals, 4)

            if insight == InsightType.MEDIAN_CAP_RATE_BY_BUILDING_TYPE:
                aggs = {insight: self.construct_terms_agg('cleaned_prop_type')}
                inside_aggs = aggs[insight].setdefault('aggs', {})
                field = 'cap_rate'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)

            if insight == InsightType.COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE:
                aggs = {insight: self.construct_terms_agg('cleaned_prop_type')}
                inside_aggs = aggs[insight].setdefault('aggs', {})
                field = 'predicted_rent'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)

            if insight == InsightType.COUNT_AND_PRICE_BY_BUILDING_TYPE:
                aggs = {insight: self.construct_terms_agg('cleaned_prop_type')}
                inside_aggs = aggs[insight].setdefault('aggs', {})
                field = 'price'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)

            if insight == InsightType.COUNT_BY_BEDS:
                aggs = {insight: self.construct_range_agg('beds', 5, 5, round_to=1, start=0,
                                                          before_start=False)}

            if insight == InsightType.COUNT_BY_BATHS:
                aggs = {insight: self.construct_range_agg('baths', 5, 6, round_to=0.5, start=1.0,
                                                          before_start=False)}

            if insight == InsightType.CAP_RATE_AND_RENT_BY_BEDS:
                aggs = {insight: self.construct_range_agg('beds', 5, 5, round_to=1, start=0,
                                                          before_start=False)}
                inside_aggs = aggs[insight].setdefault('aggs', {})
                field = 'cap_rate'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)
                field = 'predicted_rent'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)

            if insight == InsightType.CAP_RATE_AND_RENT_BY_BATHS:
                aggs = {insight: self.construct_range_agg('baths', 5, 6, round_to=0.5, start=1.0,
                                                          before_start=False)}
                inside_aggs = aggs[insight].setdefault('aggs', {})
                field = 'cap_rate'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)
                field = 'predicted_rent'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)

            if insight == InsightType.COUNT_AND_PRICE_BY_BEDS:
                aggs = {insight: self.construct_range_agg('beds', 5, 5, round_to=1, start=0,
                                                          before_start=False)}
                inside_aggs = aggs[insight].setdefault('aggs', {})
                field = 'price'
                inside_aggs[f'{field}_percentiles'] = self.construct_percentiles_agg(field, 50)

            if index == PropEsIndex.SEARCH_INVEST:
                for field in ('price', 'price_per_sqft'):
                    aggs[f'median_{field}'] = self.construct_percentiles_agg(field, 50)
                    aggs['median_cap_rate'] = self.construct_median_avg_range_agg('cap_rate', base_vals, 5, start=0.01)[
                        'cap_rate_median']
            if index in (PropEsIndex.SEARCH_BUY, PropEsIndex.SEARCH_RENT):
                if index == PropEsIndex.SEARCH_BUY:
                    fields = ('price', 'price_per_sqft')
                elif index == PropEsIndex.SEARCH_RENT:
                    fields = ('price', 'days_on_market')
                for field in fields:
                    aggs[f'median_{field}'] = self.construct_percentiles_agg(field, 50)
                aggs[f'cnt_good_deal'] = self.construct_terms_agg('is_good_deal')

            body['aggs'].update(aggs)

        return body

    def construct_median_avg_range_graph(self, aggs, total, insight, to_int=True):
        agg = aggs[f'{insight}_dist']
        graph = self.construct_range_graph(agg, total, to_int=to_int)
        meta = graph.setdefault('meta', {})
        median = aggs[f'{insight}_median']['values']['50.0']
        average = aggs[f'{insight}_average']['value']
        meta['median'] = to_num(median, to_int=to_int or median > 50)  # temporary
        meta['average'] = to_num(average, to_int=to_int or average > 50)  # TODO: make each Insight a class with methods

        if insight == InsightType.ASKING_PRICE:
            # OT-2444: it's required to additionally find min price
            minimum = aggs[f'{insight}_min']['value']
            meta['min'] = to_num(minimum, to_int=to_int or minimum > 50)

        return graph

    def get_response_data(self, requested_insights, es_resp, index):
        data = {}
        graph = None
        aggs = es_resp['aggregations']
        total = es_resp['hits']['total']['value']
        if total == 0:
            raise NotFound

        for insight in requested_insights:

            if insight in INT_MEDIAN_AVG_RANGE_INSIGHTS:
                graph = self.construct_median_avg_range_graph(aggs, total, insight)

            if insight == InsightType.PRICE_PER_SQFT:
                graph = self.construct_median_avg_range_graph(aggs, total, insight, to_int=False)

            if insight == InsightType.COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE:
                graph = self.construct_terms_with_medians_graph(aggs[insight], cnt=True)
                graph['labels'] = self._convert_enum_vals(graph['labels'], PropType3)

            if insight == InsightType.COUNT_AND_PRICE_BY_BUILDING_TYPE:
                graph = self.construct_terms_with_medians_graph(aggs[insight], cnt=True)
                enum = PropType3Rent if index == PropEsIndex.SEARCH_RENT else PropType3
                graph['labels'] = self._convert_enum_vals(graph['labels'], enum)

            if insight == InsightType.CAP_RATE:
                graph = self.construct_median_avg_range_graph(aggs, total, insight, to_int=False)

            if insight == InsightType.MEDIAN_CAP_RATE_BY_BUILDING_TYPE:
                graph = self.construct_terms_with_medians_graph(aggs[insight])
                graph['labels'] = self._convert_enum_vals(graph['labels'], PropType3)

            if insight == InsightType.COUNT_BY_BEDS:
                graph = self.construct_range_graph(aggs[insight], total, left_val=True)

            if insight == InsightType.COUNT_BY_BATHS:
                graph = self.construct_range_graph(aggs[insight], total, to_int=False,
                                                   left_val=True)

            if insight == InsightType.CAP_RATE_AND_RENT_BY_BEDS:
                graph = self.construct_range_with_medians_graph(aggs[insight], total,
                                                                left_val=True)

            if insight == InsightType.CAP_RATE_AND_RENT_BY_BATHS:
                graph = self.construct_range_with_medians_graph(aggs[insight], total, to_int=False,
                                                                left_val=True)

            if insight == InsightType.COUNT_AND_PRICE_BY_BEDS:
                graph = self.construct_range_with_medians_graph(aggs[insight], total, to_int=True,
                                                                cnt=True, left_val=True)

            data[insight] = graph

        # save total count for seo texts substitution
        data['widget_info'] = get_widget_info(index, aggs)
        data['_total'] = total
        return data

    def _convert_enum_vals(self, vals, enum):
        enum_dict = dict(enum.choices)
        converted_vals = []
        for val in vals:
            if enum_val := enum_dict.get(val):
                converted_vals.append(enum_val)
        return converted_vals

    def _extract_label_from_range_bucket(self, bucket, to_int=True, left_val=False):
        """
        If left_val==True, each label constructs as a left value of a bucket range
        """
        from_val = to_num(bucket.get('from'), to_int=to_int)
        to_val = to_num(bucket.get('to'), to_int=to_int)

        if left_val:
            if from_val is None:
                label = f'<{to_val}'
            elif to_val is None:
                label = f'{from_val}+'
            else:
                label = str(from_val)
        else:
            if from_val is None and not to_val:
                label = None
            else:
                label = {'min': from_val, 'max': to_val}
        return label

    def _get_composite_field(self, field):
        """
        If it is a composite field, return its converted name.
        Otherwise return original name
        """
        if field in ('cash_on_cash', 'total_return', 'cap_rate'):
            return self._es_constructor.get_composite_fields()[field]
        return field

    def construct_range_graph(self, agg, total, to_int=True, left_val=False):
        """
        General method to construct an insight which consists of range buckets.
        If left_val==True, each label constructs as a left value of a bucket range
        """
        labels, data = self._range_agg_to_cnt_fraction_graph(agg, total, to_int, left_val)
        datasets = [{'name': 'cnt_fraction', 'type': 'plain', 'data': data}]
        return {
            'labels': labels,
            'datasets': datasets
        } if datasets else None

    def construct_range_with_medians_graph(self, agg, total, to_int=True, cnt=False,
                                           cnt_fraction=False, left_val=False):
        """
        Construct a resulting insight which consists of 'range' buckets with
        any number of median subcalculations in them
        """
        labels = []
        cnt_data = []
        medians_data = defaultdict(list)

        for bucket in agg['buckets'].values():
            if label := self._extract_label_from_range_bucket(bucket, to_int, left_val):
                labels.append(label)

            if cnt:
                cnt_data.append(bucket.get('doc_count'))
            elif cnt_fraction:
                cnt_data.append(bucket.get('doc_count') / total)

            for agg_key in bucket:
                if agg_key.endswith('_percentiles'):
                    field = agg_key[:-len('_percentiles')]
                    medians_data[field].append(bucket[agg_key]['values']['50.0'])

        datasets = [{'name': f'median_{field}', 'type': 'plain', 'data': data}
                    for field, data in medians_data.items()]
        if cnt_data:
            name = 'cnt' if cnt else 'cnt_fraction'
            datasets.append({'name': name, 'type': 'plain', 'data': cnt_data})

        return {'labels': labels, 'datasets': datasets} if datasets else None

    def construct_terms_with_medians_graph(self, agg, cnt=False):
        """
        Construct a resulting insight which consists of 'terms' buckets with
        any number of median subcalculations in them
        """
        labels = []
        cnt_data = []
        medians_data = defaultdict(list)

        for bucket in agg['buckets']:
            labels.append(bucket['key'])
            if cnt:
                cnt_data.append(bucket['doc_count'])
            for agg_key in bucket:
                if agg_key.endswith('_percentiles'):
                    field = agg_key[:-len('_percentiles')]
                    medians_data[field].append(bucket[agg_key]['values']['50.0'])

        datasets = [{'name': f'median_{field}', 'type': 'plain', 'data': data}
                    for field, data in medians_data.items()]
        if cnt_data:
            datasets.append({'name': 'cnt', 'type': 'plain', 'data': cnt_data})

        return {'labels': labels, 'datasets': datasets} if datasets else None

    # def construct_est_rent_distribution_graph(self, aggs, total):
    #     """
    #     Construct a graph for 'est_rent_distribution' insight
    #     """
    #     insight = InsightType.EST_RENT_DISTRIBUTION.value
    #
    #     field = 'cap_rate'
    #     meta = {f'average_{field}': aggs[f'{insight}_average_{field}']['value']}
    #     meta[f'median_{field}'] = aggs[f'{insight}_median_{field}']['values']['50.0']
    #
    #     for field in ('predicted_rent', 'price', 'price_per_sqft'):
    #         meta[f'median_{field}'] = aggs[f'{insight}_median_{field}']['values']['50.0']
    #         if meta[f'median_{field}']:
    #             meta[f'median_{field}'] =int(meta[f'median_{field}'])
    #     labels, cnt_data = self._range_agg_to_cnt_fraction_graph(aggs[f'{insight}_dist'], total)
    #     datasets = [{'name': 'cnt_fraction', 'type': 'plain', 'data': cnt_data}]
    #     return {'meta': meta, 'labels': labels, 'datasets': datasets} if datasets else None
    #
    # def construct_asking_price_distribution_graph(self, aggs, total, index):
    #     """
    #     Construct a graph for 'asking_price_distribution' insight
    #     """
    #     insight = InsightType.ASKING_PRICE_DISTRIBUTION.value
    #
    #     meta = {'cnt': total}
    #     if index == PropEsIndex.SEARCH_RENT:
    #         fields = ('price', 'days_on_market')
    #     elif index in  PropEsIndex.SEARCH_BUY:
    #         fields = ('price', 'price_per_sqft')
    #     for field in fields:
    #         meta[f'median_{field}'] = int(aggs[f'{insight}_median_{field}']['values']['50.0'])
    #         if meta[f'median_{field}']:
    #             meta[f'median_{field}'] = int(meta[f'median_{field}'])
    #     buckets = aggs['asking_price_distribution_cnt_good_deal']['buckets']
    #     for bucket in buckets:
    #         if bucket['key_as_string'] == 'true':
    #             meta['cnt_good_deals'] = bucket['doc_count']
    #     if not meta.get('cnt_good_deals'):
    #         meta['cnt_good_deals'] = 0
    #     labels, cnt_data = self._range_agg_to_cnt_fraction_graph(aggs[f'{insight}_dist'], total)
    #     datasets = [{'name': 'cnt_fraction', 'type': 'plain', 'data': cnt_data}]
    #     return {'meta': meta, 'labels': labels, 'datasets': datasets} if datasets else None

    def _range_agg_to_cnt_fraction_graph(self, agg, total, to_int=True, left_val=False):
        labels = []
        data = []
        for bucket in agg['buckets'].values():
            if label := self._extract_label_from_range_bucket(bucket, to_int, left_val):
                labels.append(label)
                data.append(bucket.get('doc_count') / total)
        return labels, data


def calc_magnitude(value):
    """Calculate order of magnitude"""
    if value == 0:
        return 0
    return int(math.floor(math.log10(abs(value))))


def get_widget_info(index, aggs):
    meta = {}
    if index == PropEsIndex.SEARCH_RENT:
        fields = ('price', 'days_on_market')
    elif index == PropEsIndex.SEARCH_BUY:
        fields = ('price', 'price_per_sqft')
    elif index == PropEsIndex.SEARCH_INVEST:
        fields = ('price_per_sqft', 'price', 'cap_rate')
    for field in fields:
        val = aggs[f'median_{field}']['values']['50.0']
        if val:
            if field not in ('cap_rate',):
                meta[field] = int(val)
            else:
                meta[field] = round(val, 4)
        else:
            meta[field] = None

    if index in (PropEsIndex.SEARCH_RENT, PropEsIndex.SEARCH_BUY):
        buckets = aggs['cnt_good_deal']['buckets']
        for bucket in buckets:
            if bucket['key_as_string'] == 'true':
                meta['good_deals'] = bucket['doc_count']
        if not meta.get('good_deals'):
            meta['good_deals'] = 0
    return meta
