import datetime
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_recaptcha.fields import ReCaptchaV3Field
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from account.models import EmailSettings
from api_property.common.common import (
    is_suitable_prop_class_returned_from_db,
    prop_has_invest_view,
    is_off_market_status,
    getProp, check_right_sighs_to_sheets,
)
from api_property.common.rebates import get_rebate_for_view
from api_property.common.errors import NoPropertyError
from api_property.constants import SOLD_STATUSES
from api_property.enums import PropClass
from api_property.models import ContactAgent
from common.serializers import PasswordSetModelSerializer
from common.utils import get_absolute_url


User = get_user_model()


class CommonContactAgentSerializer(PasswordSetModelSerializer):
    url = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ContactAgent
        fields = (
            "full_name",
            "email",
            "phone",
            "recaptcha",
            "url",
            "prop_class",
            "user",
        )

    recaptcha = ReCaptchaV3Field(action="contact_agent_request")
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def normalize_url(self, url):
        return re.sub(r'(&gclid).*', '', url)[:255]

    def construct_url(self, attrs):
        if url := attrs.get('url'):
            return self.normalize_url(get_absolute_url(url))

    def validate(self, attrs):
        if attrs.get("recaptcha"):
            attrs.pop("recaptcha")
        elif settings.IS_PRODUCTION:
            raise ValidationError('recaptcha')

        attrs = check_right_sighs_to_sheets(attrs)
        prop = getProp(attrs["prop_id"])
        if not prop or not is_suitable_prop_class_returned_from_db(
                prop["prop_class"], attrs["prop_class"], prop_has_invest_view(prop)):
            raise NoPropertyError

        attrs["prop_address"] = prop["address"]["full_address"]
        attrs["price"] = prop["data"]["close_price"] if prop['status'] in SOLD_STATUSES else prop["data"]["price"]
        attrs["prop"] = prop
        attrs["url"] = self.construct_url(attrs)
        return attrs

    def create(self, validated_data):
        if "recaptcha" in validated_data:
            validated_data.pop("recaptcha")
        if "prop" in validated_data:
            validated_data.pop("prop")
        if "tour_type" in validated_data:
            validated_data.pop("tour_type")
        if "schedule_tour_date" in validated_data:
            validated_data.pop("schedule_tour_date")
        if "schedule_tour_time" in validated_data:
            validated_data.pop("schedule_tour_time")
        if "rebate" in validated_data:
            validated_data.pop("rebate")
        if "enable_alerts" in validated_data:
            validated_data.pop("enable_alerts")
        if "popup_type" in validated_data:
            validated_data.pop("popup_type")
        if "best_time_to_call" in validated_data:
            validated_data.pop("best_time_to_call")
        user = validated_data.get('user')
        _validated_data = validated_data.copy()
        _validated_data.pop('user')
        instance = super().create(_validated_data)
        if user.is_authenticated:
            user.leads.add(instance)
        return instance

    def save(self, **kwargs):
        """
        If email is unknown to us, create new user.
        If new info about existing user came, update it.
        """
        data = self.validated_data
        user = data['user']

        if data.get('enable_alerts'):
            if not user.pk:
                if email := data.get('email'):
                    user = User.objects.filter(email=email).first() or self._create_user(data)
                else:
                    raise ValidationError('email should_be specified')
            if not user.similar_props.first():
                e_setting_obj = EmailSettings.objects.get(user=user)
                e_setting_obj.similars = True
                e_setting_obj.save()
            if not user.similar_props.filter(prop_id=data['prop_id'],
                                             prop_class=data['prop_class']):
                user.similar_props.create(prop_id=data['prop_id'], prop_class=data['prop_class'],)
            self._update_user(user, data)

        data['user'] = user
        instance = super().save(**kwargs)
        return instance


class ScheduleTourSerializer(CommonContactAgentSerializer):
    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            "enable_alerts",
            "prop_id",
            "prop_address",
            "request",
            "schedule_tour_date",
            "schedule_tour_time",
            "tour_type",
        )

    prop_address = serializers.HiddenField(default=None)
    enable_alerts = serializers.BooleanField(required=False)

    prop_class = serializers.ChoiceField(
        choices=[("buy", "Buy"), ("invest", "Invest")], default="buy"
    )
    request = serializers.CharField(max_length=4096, required=False, allow_blank=True)
    schedule_tour_date = serializers.DateField(required=True)
    schedule_tour_time = serializers.TimeField(
        required=True,
        format="%I:%M%p",
        input_formats=["%I:%M%p", "%I:%M %p"],
        allow_null=True,
    )
    tour_type = serializers.ChoiceField(
        required=True,
        choices=[
            ("in_person", "In Person"),
            ("video_chat", "Video Chat"),
        ],
    )

    def validate(self, attrs):
        attrs["schedule_tour_time"] = attrs["schedule_tour_time"] or "Any Time"
        if attrs["schedule_tour_date"] < datetime.date.today() - datetime.timedelta(days=1):
            raise ValidationError("schedule_tour_date should be >= current date")
        return super().validate(attrs)


class CheckAvailabilitySerializer(CommonContactAgentSerializer):
    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            "enable_alerts",
            "prop_id",
            "prop_address",
            "request",
            "move_in_date",
        )

    prop_address = serializers.HiddenField(default=None)
    enable_alerts = serializers.BooleanField(required=False)
    request = serializers.CharField(max_length=4096, required=False, allow_blank=True)
    move_in_date = serializers.DateField(required=True)
    prop_class = serializers.ChoiceField(choices=[("rent", "Rent")], default="rent")

    def validate(self, attrs):
        if attrs["move_in_date"] < datetime.date.today() - datetime.timedelta(days=1):
            raise ValidationError("move in date should be >= current date")
        return super().validate(attrs)


class RebateSerializer(CommonContactAgentSerializer):
    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            "enable_alerts",
            "prop_id",
            "prop_address",
            "best_time_to_call",
        )

    prop_address = serializers.HiddenField(default=None)
    enable_alerts = serializers.BooleanField(required=False)
    prop_class = serializers.ChoiceField(
        choices=[("buy", "Buy"), ("invest", "Invest")], default="buy"
    )
    best_time_to_call = serializers.ChoiceField(
        required=True,
        choices=[
            ("any_time", "Any Time"),
            ("morning", "Morning"),
            ("noon", "Noon"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
        ],
        allow_blank=True,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        prop = attrs["prop"]
        zip_code = prop["address"]["zip"]
        price = prop["data"]["price"]
        is_off_market = is_off_market_status(prop["status"])
        attrs["rebate"] = get_rebate_for_view(zip_code, price, is_off_market)
        return attrs


class OnlyParamsRebateSerializer(CommonContactAgentSerializer):
    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            "best_time_to_call",
            "prop_id",
        )

    prop_class = serializers.ChoiceField(
        choices=[("buy", "Buy"), ("invest", "Invest")], default="buy"
    )
    best_time_to_call = serializers.ChoiceField(
        required=True,
        choices=[
            ("any_time", "Any Time"),
            ("morning", "Morning"),
            ("noon", "Noon"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
        ],
        allow_blank=True,
    )


class AskQuestionSerializer(CommonContactAgentSerializer):
    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            "enable_alerts",
            "prop_id",
            "prop_address",
            "request",
        )

    prop_address = serializers.HiddenField(default=None)
    enable_alerts = serializers.BooleanField(required=False)
    prop_class = serializers.ChoiceField(choices=PropClass.choices)
    request = serializers.CharField(max_length=4096, required=False, allow_blank=True)


class ContactSaleLPSerializer(CommonContactAgentSerializer):
    """
    Contact agent from sales landing page
    """
    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            "request",
        )

    request = serializers.CharField(max_length=4096, required=False, allow_blank=True)
    prop_class = serializers.ChoiceField(
        choices=[("buy", "Buy")], default="buy",
    )

    def validate(self, attrs):
        attrs['url'] = self.construct_url(attrs)
        return attrs


class GetHelpSerializer(CommonContactAgentSerializer):

    class Meta(CommonContactAgentSerializer.Meta):
        fields = CommonContactAgentSerializer.Meta.fields + (
            'request',
        )

    request = serializers.CharField(max_length=4096, required=False, allow_blank=True)
    prop_class = serializers.ChoiceField(choices=PropClass.choices)

    def validate(self, attrs):
        attrs['url'] = self.construct_url(attrs)
        return attrs
