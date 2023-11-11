from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from account.tokens import OfirioRefreshToken
from account.authentication import FacebookJwtBackend, GoogleJwtBackend
from account.emails import PasswordSetRequestedEmail
from account.common import phone_regex
from account.models import EmailSettings, FavoriteProperty, GoodDealSettings, RestorePasswordCheck
from account.utils import get_access_status, validate_password
from api_property.serializers import PropCitiesField, PropCitySerializer
from common.serializers import PasswordSetModelSerializer
from common.fields import TextInputListField
from search.enums import PropType3


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class SocialJwtLoginSerializer(serializers.Serializer):
    backend = None

    token = serializers.CharField(required=True)
    user = serializers.HiddenField(default=None)

    def validate(self, raw_data):
        """
        Validate token from social provider and fill a user
        """
        data = super().validate(raw_data)
        backend = self.backend()
        request = self.context['request']
        data['user'] = backend.authenticate(request, token=data['token'])
        return data


class GoogleJwtLoginSerializer(SocialJwtLoginSerializer):
    backend = GoogleJwtBackend


class FacebookJwtLoginSerializer(SocialJwtLoginSerializer):
    backend = FacebookJwtBackend


class JwtLoginSerializer(TokenObtainPairSerializer):
    token_class = OfirioRefreshToken


class JwtRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(style={'input_type': 'hidden'})
    token_class = OfirioRefreshToken


class ChangeProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True, allow_blank=True)
    phone = serializers.CharField(validators=[phone_regex], max_length=16,
                                  allow_blank=True, required=False, default='')


class ChangePasswordSerializer(serializers.Serializer):
    password_old = serializers.CharField(required=True)
    password_new = serializers.CharField(required=True, trim_whitespace=False,
                                         min_length=6, max_length=20)

    def validate(self, raw_data):
        email = getattr(self.context['request'].user, 'email', None)
        raw_password = raw_data.get('password_new')
        password = validate_password(raw_password, 'password_new', email)
        return {**raw_data, **{'password_new': password}}


class AccountSerializer(serializers.ModelSerializer):
    favorites_qty = serializers.SerializerMethodField()
    access_status = serializers.SerializerMethodField()
    is_admin = serializers.BooleanField(source='is_staff')

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name', 'phone',
                  'is_admin', 'is_team', 'verified', 'access_status', 'warnings',
                  # custom fields:
                  'favorites_qty', 'access_status')

    def get_favorites_qty(self, obj):
        return FavoriteProperty.objects.filter(user=obj).count()

    def get_access_status(self, obj):
        return get_access_status(obj)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(required=True, trim_whitespace=False,
                                     min_length=6, max_length=20)
    first_name = serializers.CharField(required=False, default='')
    last_name = serializers.CharField(required=False, default='')
    phone = serializers.CharField(validators=[phone_regex], max_length=16, default='')

    class Meta:
        model = User
        fields = 'id', 'email', 'password', 'first_name', 'last_name', 'phone'
        read_only_fields = 'id',

    def validate(self, raw_data):
        email = str(raw_data.get('email', '')).strip()
        raw_password = raw_data.get('password')
        password = validate_password(raw_password, email=email)
        return {**raw_data, **{'email': email, 'password': password}}


class RestorePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class RestorePasswordCheckSerializer(serializers.Serializer):
    restore_code = serializers.CharField(required=True, max_length=32, min_length=32)


class RestorePasswordChangeSerializer(serializers.Serializer):
    restore_code = serializers.CharField(required=True, max_length=32, min_length=32)
    password_new = serializers.CharField(required=True, trim_whitespace=False,
                                         min_length=6, max_length=20)

    def validate(self, raw_data):
        restore_code = raw_data.get('restore_code').strip()
        restore_check = RestorePasswordCheck.objects.find_active(restore_code)
        raw_password = raw_data.get('password_new')
        email = getattr(restore_check, 'email', None)
        password = validate_password(raw_password, 'password_new', email)
        return {**raw_data, **{'password_new': password}}


class EmailSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailSettings
        fields = ('similars', 'good_deals', 'prop_updates',
                  'favorites', 'favorites_match_notification',
                  'tips_and_guides', 'market_reports_and_updates',
                  'tool_updates', 'partner_offers_and_deals', 'properties_you_may_like')

    def validate(self, attrs):
        validated_attrs = {}
        for key, value in attrs.items():  # ModelSerializer adds not indicated fields in tests,
            if key in self.initial_data:  # although it is only in tests, with this method
                validated_attrs[key] = value  # our code will be safer
        return validated_attrs


class GoodDealSettingsSerializer(PasswordSetModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    email = serializers.EmailField(
        validators=(EmailValidator(),), max_length=254,
        required=False, allow_blank=True, write_only=True)
    phone = serializers.CharField(
        max_length=16, validators=[phone_regex], allow_blank=True, required=False, write_only=True)
    cities = PropCitiesField(required=False, default=list)
    add_city = serializers.BooleanField(required=False, default=False, write_only=True)
    prop_type = serializers.ChoiceField(choices=PropType3.choices, required=False, allow_null=True)

    rent_min_price = serializers.IntegerField(
        default=200, required=False, min_value=200, max_value=20_000)
    rent_max_price = serializers.IntegerField(
        default=20_000, required=False, min_value=200, max_value=20_000)
    buy_min_price = serializers.IntegerField(
        default=10_000, required=False, min_value=10_000, max_value=10_000_000)
    buy_max_price = serializers.IntegerField(
        default=10_000_000, required=False, min_value=10_000, max_value=10_000_000)
    invest_min_price = serializers.IntegerField(
        default=10_000, required=False, min_value=10_000, max_value=10_000_000)
    invest_max_price = serializers.IntegerField(
        default=10_000_000, required=False, min_value=10_000, max_value=10_000_000)

    rent_enabled = serializers.BooleanField(default=False, required=False)
    buy_enabled = serializers.BooleanField(default=False, required=False)
    invest_enabled = serializers.BooleanField(default=False, required=False)

    beds_min = serializers.IntegerField(
        default=None, required=False, max_value=5, allow_null=True)
    baths_min = serializers.IntegerField(
        default=None, required=False, max_value=4, allow_null=True)

    class Meta:
        model = GoodDealSettings
        fields = (
            'email', 'phone', 'user', 'cities', 'add_city', 'prop_type',
            'rent_min_price', 'rent_max_price',
            'buy_min_price', 'buy_max_price',
            'invest_min_price', 'invest_max_price',
            'rent_enabled', 'buy_enabled', 'invest_enabled',
            'beds_min', 'baths_min',
        )

    def _update_user(self, user, data):
        super()._update_user(user, data)

        # set 'good deals' in user's email settings to true
        if any([data.get('rent_enabled'), data.get('buy_enabled'), data.get('invest_enabled')]):
            ems = user.emailsettings_set.first()
            ems.good_deals = True
            ems.save()

    def validate(self, attrs):
        if any([attrs['rent_enabled'], attrs['buy_enabled'], attrs['invest_enabled']]):
            if not attrs['cities']:
                raise ValidationError('Cities are required because notifications are enabled')

        # change only received fields
        validated_attrs = {'user': attrs['user']}
        for key, value in attrs.items():
            if key in self.initial_data:
                validated_attrs[key] = value

        return validated_attrs

    def save(self, **kwargs):
        """
        If email is unknown to us, create new user.
        If new info about existing user came, update it.
        """
        data = self.validated_data
        user = data['user']

        if not data['user'].pk:
            if email := data.get('email'):
                user = User.objects.filter(email=email).first() or self._create_user(data)
                self.instance = GoodDealSettings.objects.get(user=user)
            else:
                raise ValidationError('Email is required')

        self._update_user(user, data)
        data['user'] = user
        data.pop('email', None)  # user already obtained/created, no need in email
        data.pop('phone', None)  # phone already written to the user, no need in phone

        if data.get('add_city'):  # if add_city is True, add passed cities to existing ones
            existing_cities = list(self.instance.cities.all())
            kwargs['cities'] = kwargs.pop('cities', []) + data['cities'] + existing_cities

        instance = super().save(**kwargs)
        return instance
