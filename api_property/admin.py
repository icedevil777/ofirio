import json

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminRadioSelect
from django.utils.html import mark_safe
from ofirio_common.helpers import url_to_cdn

from .models import (
    Building,
    ContactAgent,
    PropCity,
    PropertyNotified,
    PropertyUpdateModel,
    SimilarPropertyNotificationModel,
)
from common.utils import get_pg_connection


class ContactAgentAdmin(admin.ModelAdmin):
    model = ContactAgent
    fields = (
        'order_number', 'created_at', 'full_name',
        'email', 'phone', 'request', 'prop_id', 'prop_address',
    )
    readonly_fields = 'created_at', 'order_number'
    list_display = (
        'order_number', 'created_at', 'full_name', 'email', 'phone', 'request', 'prop_id'
    )

admin.site.register(ContactAgent, ContactAgentAdmin)


class SimilarNotificationAdmin(admin.ModelAdmin):
    model = SimilarPropertyNotificationModel
    fields = 'pk', 'prop_id', 'user', 'prop_class', 'created_at'
    readonly_fields = 'created_at', 'pk'
    list_display = 'user', 'prop_id', 'prop_class', 'created_at'
    list_filter = ('prop_class',)

admin.site.register(SimilarPropertyNotificationModel, SimilarNotificationAdmin)


class PropertyUpdateAdmin(admin.ModelAdmin):
    model = PropertyUpdateModel
    fields = 'pk', 'prop_id', 'user', 'prop_class', 'status', 'price', 'created_at', 'modified_at'
    readonly_fields = 'created_at', 'modified_at', 'pk'
    list_display = 'created_at', 'user', 'prop_id', 'prop_class'
    list_filter = ('prop_class',)

admin.site.register(PropertyUpdateModel, PropertyUpdateAdmin)


class PropertyNotifiedAdmin(admin.ModelAdmin):
    model = PropertyNotified
    fields = 'created_at', 'user', 'prop_class', 'prop_id'
    readonly_fields = ('created_at',)
    list_display = 'user', 'prop_id', 'prop_class', 'created_at'
    list_filter = ('prop_class',)

admin.site.register(PropertyNotified, PropertyNotifiedAdmin)


class PropCityAdmin(admin.ModelAdmin):
    model = PropCity
    readonly_fields = 'created_at', 'modified_at'
    list_display = 'label', 'city', 'state_id', 'county'
    fields = 'label', 'city', 'state_id', 'county', 'created_at', 'modified_at'

admin.site.register(PropCity, PropCityAdmin)


class ImageAdminSelectWidget(AdminRadioSelect):
    """
    Widget to select first photo for a building in Admin
    """
    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                value = None

        if isinstance(value, list):
            for idx, url in enumerate(value):
                html = f'<a href="{url}">link</a> <img src="{url_to_cdn(url)}?width=150"> {url}'
                self.choices.append((idx, mark_safe(html)))

        original = super().render(name, value, attrs=attrs, renderer=renderer)
        return original


class ImageAdminSelectField(forms.fields.JSONField):
    """
    Field to select first photo for a building in Admin
    """
    widget = ImageAdminSelectWidget

    def to_python(self, value):
        return value


class BuildingAdminForm(forms.ModelForm):
    """
    Form for a building in Admin
    """
    photos = ImageAdminSelectField(required=False, label='First photo')

    class Meta:
        model = Building
        fields = 'building_id', 'photos'


class BuildingAdmin(admin.ModelAdmin):
    form = BuildingAdminForm
    model = Building
    fields = 'building_id', 'url', 'photos'
    list_display = 'building_id', 'url'
    readonly_fields = 'building_id', 'url'
    search_fields = 'building_id',

    def url(self, obj):
        url = f'https://{settings.PROJECT_DOMAIN}/b/{obj.building_id}'
        return mark_safe(f'<a href="{url}">{url}</a>')

    def save_model(self, request, obj, form, change):
        """
        Use chosen photo to change photo URLs order in buildings table
        """
        index = int(obj.photos)
        conn = get_pg_connection(db='prop_db_rw')

        with conn.cursor() as cursor:
            cursor.execute('select photos from buildings where building_id=%s', (obj.building_id,))
            photos = cursor.fetchone()[0]

            url = photos.pop(index)
            photos = [url] + photos

            sql = 'update buildings set photos=%s, photos_1_manual=true where building_id=%s'
            cursor.execute(sql, (json.dumps(photos), obj.building_id))
            conn.commit()


admin.site.register(Building, BuildingAdmin)
