from ofirio_common.geocode import geocode, parse_address_from_geocode
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from api_property.common.common import get_fields_prop_cache, getPropAddressStr
from sale_estimator.common.common import (
    get_beds_from_prop,
    get_baths_from_prop,
    get_baths_from_choices,
    get_beds_from_choices,
)
from sale_estimator.enums import PropertyType3, Beds, Baths


class SaleEstimatorSerializer(serializers.Serializer):

    prop_id = serializers.CharField(
        required=False, default=None, allow_null=True, max_length=255
    )
    query = serializers.CharField(
        required=False, default=None, allow_null=True, max_length=255
    )
    beds = serializers.ChoiceField(
        required=False, allow_null=True, choices=Beds.choices
    )
    baths = serializers.ChoiceField(
        required=False, allow_null=True, choices=Baths.choices
    )
    prop_type3 = serializers.ChoiceField(
        required=False, allow_null=True, choices=PropertyType3.choices
    )
    building_size = serializers.IntegerField(
        required=False, default=None, allow_null=True
    )

    def __init__(self, *args, **kwargs):
        self.conn = kwargs.pop('conn', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        query = attrs.get("query")
        prop_id = attrs.get("prop_id")

        if not query and not prop_id:
            raise serializers.ValidationError("Query or Prop Id required")
        if prop_id:
            prop = get_fields_prop_cache(
                prop_id=prop_id,
                fields=("data", "address", "params"),
                conn=self.conn
            )
            if not prop and not query:
                raise NotFound
            elif prop:
                attrs["beds"] = (
                    get_beds_from_choices(attrs.get("beds"))
                    if attrs.get("beds") is not None
                    else get_beds_from_prop(prop["data"]["beds"])
                )
                attrs["baths"] = (
                    get_baths_from_choices(attrs.get("baths"))
                    if attrs.get("baths") is not None
                    else get_baths_from_prop(prop["data"]["baths"])
                )
                attrs["prop_type3"] = (
                    attrs.get("prop_type3") or prop["data"]["prop_type3"]
                )
                attrs["building_size"] = (
                    attrs.get("building_size") or prop["data"]["building_size"]
                )
                attrs["address"] = {
                    "address_line": prop["address"]["line"],
                    "state_id": prop["address"]["state_code"],
                    "county": prop["address"]["county"],
                    "city": prop["address"]["city"],
                    "zip": prop["address"]["zip"],
                    "lat": prop["address"]["lat"],
                    "lon": prop["address"]["lon"],
                    "place_type": "street_address",
                    "formatted_address": getPropAddressStr(prop),
                }
                attrs["is_rehab"] = prop["params"].get("is_rehab")
                return attrs
        elif query:
            if any(attrs.get(x) is None for x in ["beds", "baths", "prop_type3"]):
                raise serializers.ValidationError(
                    "prop_type3, baths, beds are required if prop_id is empty"
                )
            with self.conn.cursor() as cursor:
                location = geocode(cursor, address=query)
            if not location:
                raise NotFound(f"There is no such location {query}")
            address = parse_address_from_geocode(location)
            if address["place_type"] != "street_address":
                raise serializers.ValidationError(
                    f"You should indicate street adress not {query}"
                )
            attrs["address"] = address
            attrs["building_size"] = attrs.get("building_size")
            attrs["beds"] = get_beds_from_choices(attrs["beds"])
            attrs["baths"] = get_baths_from_choices(attrs["baths"])
        return attrs
