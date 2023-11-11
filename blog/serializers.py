from rest_framework import serializers


class PaginatedListParamsSerializer(serializers.Serializer):
    """
    Validate query params when there may be paginated response
    """
    page = serializers.IntegerField(required=False, default=None, min_value=1)
