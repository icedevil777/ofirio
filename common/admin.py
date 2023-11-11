from django.contrib import admin

from .models import ContactUs


class ContactUsAdmin(admin.ModelAdmin):
    model = ContactUs
    fields = ('id', 'created_at', 'full_name', 'email', 'message')
    readonly_fields = ('id', 'created_at')
    list_display = ('created_at', 'full_name', 'email', 'message')

admin.site.register(ContactUs, ContactUsAdmin)
