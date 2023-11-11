from django.urls import path

from . import views


app_name = 'common'

urlpatterns = [
    path('api/contact_us', views.ContactUsView.as_view(), name='contact_us'),
    path('api/realestatelicenses', views.LincesesView.as_view(), name='Licenses'),
]
