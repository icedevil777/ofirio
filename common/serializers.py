from django.conf import settings
from django.contrib.auth import get_user_model
from drf_recaptcha.fields import ReCaptchaV3Field
from rest_framework import serializers

from account.emails import PasswordSetRequestedEmail

from common.models import ContactUs

User = get_user_model()

class EmptySerializer(serializers.Serializer):
    """
    Allow DRF's browsable API to show CreateAPIView endpoint
    if it doesn't have serializer class
    """
    pass


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = 'full_name', 'email', 'message', 'recaptcha'
    if settings.IS_PRODUCTION:
        recaptcha = ReCaptchaV3Field(action='contact_us_request')
    else:
        recaptcha = ReCaptchaV3Field(action='contact_us_request', required=False)

    def validate(self, attrs):
        if attrs.get("recaptcha"):
            attrs.pop("recaptcha")
        return attrs


class PasswordSetModelSerializer(serializers.ModelSerializer):

    def _update_user(self, user, data):
        if phone := data.get('phone'):
            if not user.phone:
                if not User.objects.filter(phone=phone):
                    user.phone = phone
        if full_name := data.get('full_name'):
            if not user.first_name and not user.last_name:
                splited_name = full_name.strip().split(' ')
                if len(splited_name) == 1:
                    user.first_name = splited_name[0]
                elif len(splited_name) == 2:
                    user.first_name = splited_name[0]
                    user.last_name = splited_name[1]
                elif len(splited_name) > 2:
                    user.first_name = splited_name[0]
                    user.last_name = ' '.join(splited_name[1:])
        user.save()

    def _create_user(self, data):
        user_data = {'email': data.get('email')}
        if phone := data.get('phone'):
            if not User.objects.filter(phone=phone):
                user_data['phone'] = phone
        user = User.objects.create_user(**user_data)
        PasswordSetRequestedEmail.send(user)
        return user
