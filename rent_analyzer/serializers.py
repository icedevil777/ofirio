from rest_framework import serializers

from api_property.enums import AggTypeChoices, GraphsChoices
from common.fields import MultipleChoiceListField
from rent_analyzer.enums import (
    SearchType, Distance, Beds, Baths, PropertyType, LookBack, PropertyType3,
)


class RentAnalyzerSearchSerializer(serializers.Serializer):

    type = serializers.ChoiceField(required=True, choices=SearchType.choices)
    query = serializers.CharField(required=False, default=None, allow_null=True, max_length=255)
    distance = serializers.ChoiceField(required=True, choices=Distance.choices)
    beds = serializers.ChoiceField(required=True, choices=Beds.choices)
    baths = serializers.ChoiceField(required=True, choices=Baths.choices)
    prop_type3 = serializers.ChoiceField(required=False, default='', choices=PropertyType3.choices)
    look_back = serializers.ChoiceField(required=True, choices=LookBack.choices, initial='12')
    building_size = serializers.IntegerField(required=False, default=None, allow_null=True)
    prop_id = serializers.CharField(required=False, default=None, allow_null=True, max_length=255)

    def validate(self, data):
        query = data.get('query')
        prop_id = data.get('prop_id')

        if not query and not prop_id:
            raise serializers.ValidationError('Query or Prop Id required')

        return data


class AnalyticsSerializer(serializers.Serializer):
    county = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    state = serializers.CharField(required=True, max_length=2)
    zip = serializers.CharField(required=False, max_length=5,allow_null=True, allow_blank=True)
    city = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    agg_type = serializers.ChoiceField(choices=AggTypeChoices.choices,
                                       required=True)
    graph_names = MultipleChoiceListField(choices=GraphsChoices.choices,
                                          allow_empty=False, required=True)
    prop_type2 = serializers.ChoiceField(required=False, choices=PropertyType3.choices,
                                         default=PropertyType3.ANY, allow_null=True)
