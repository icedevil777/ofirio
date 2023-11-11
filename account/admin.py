from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.contrib.auth.admin import UserAdmin

from .models import (
    AccessEvent,
    CustomUser,
    EmailAddress,
    EmailSettings,
    FavoriteProperty,
    GoodDealSettings,
    RestorePasswordCheck,
)


class UserContactAget(TabularInline):
    model = CustomUser.leads.through


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = 'email', 'id', 'full_name', 'verified', 'is_team', 'phone',
    list_filter = 'is_staff', 'is_active', 'is_team'
    readonly_fields = 'id', 'created_at', 'modified_at'
    inlines = (UserContactAget,)
    fieldsets = (
        (None, {'fields': (
            'email', 'password', 'created_at', 'modified_at', 'password_changed_at',
        )}),
        ('Data', {'fields': (
            'first_name', 'last_name', 'phone', 'accepted_terms_of_use',
            'google_user_id', 'fb_user_id',
        )}),
        ('Permissions', {'fields': (
            'is_superuser', 'is_staff', 'is_active', 'verified', 'is_team',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff',
                'is_active', 'is_team',
            )}
         ),
    )
    search_fields = 'email', 'first_name', 'last_name', 'is_active'
    ordering = 'email', 'first_name', 'last_name'

    def full_name(self, obj):
        return obj.get_full_name()


admin.site.register(CustomUser, CustomUserAdmin)


class RestorePasswordCheckAdmin(admin.ModelAdmin):
    model = RestorePasswordCheck
    list_display = 'email', 'restore_code', 'created_time', 'used'

admin.site.register(RestorePasswordCheck, RestorePasswordCheckAdmin)


class FavoritePropertyAdmin(admin.ModelAdmin):
    model = FavoriteProperty
    list_display = 'created_at', 'prop_id', 'user', 'prop_class'
    list_filter = 'prop_class',
    readonly_fields = 'created_at', 'modified_at'
    search_fields = 'prop_id', 'user__email', 'address'

admin.site.register(FavoriteProperty, FavoritePropertyAdmin)


class EmailSettingsAdmin(admin.ModelAdmin):
    model = EmailSettings
    readonly_fields = 'created_at', 'modified_at'
    list_display = 'user', 'good_deals', 'similars', 'prop_updates', 'favorites'
    fields = (
        'user', 'created_at', 'modified_at', 'good_deals', 'similars', 'prop_updates', 'favorites',
        'favorites_match_notification', 'tips_and_guides', 'market_reports_and_updates',
        'tool_updates', 'partner_offers_and_deals', 'properties_you_may_like',
    )

admin.site.register(EmailSettings, EmailSettingsAdmin)


class GoodDealSettingsAdmin(admin.ModelAdmin):
    model = GoodDealSettings
    readonly_fields = 'created_at', 'modified_at'
    list_filter = 'rent_enabled', 'buy_enabled', 'invest_enabled'
    list_display = 'user', 'rent_enabled', 'buy_enabled', 'invest_enabled'
    fields = (
        'user', 'created_at', 'modified_at', 'cities', 'prop_type',
        'rent_min_price', 'rent_max_price', 'buy_min_price', 'buy_max_price',
        'invest_min_price', 'invest_max_price',
        'rent_enabled', 'buy_enabled', 'invest_enabled',
        'beds_min', 'baths_min',
    )

admin.site.register(GoodDealSettings, GoodDealSettingsAdmin)


class EmailAddressAdmin(admin.ModelAdmin):
    model = EmailAddress
    list_display = 'user', 'sent_at', 'code', 'verified'

admin.site.register(EmailAddress, EmailAddressAdmin)


class AccessEventAdmin(admin.ModelAdmin):
    model = AccessEvent
    fields = 'id', 'created_at', 'access_type', 'user', 'ip_address',
    readonly_fields = 'id', 'created_at',
    list_display = 'created_at', 'access_type', 'user', 'ip_address',

admin.site.register(AccessEvent, AccessEventAdmin)
