from django.urls import path
from . import views


app_name = 'search'

urlpatterns = [
    path('api/search', views.Search.as_view(), name='search'),
    path('api/search/mortgage', views.Mortgage.as_view(), name='mortgage'),
    path('api/search/autocomplete', views.Autocomplete.as_view(), name='autocomplete'),
    path('api/search/city-autocomplete', views.CityAutocomplete.as_view(), name='city_autocomplete'),
    path('api/search/keyword-autocomplete', views.KeywordAutocomplete.as_view(), name='keyword_autocomplete'),
    path('api/search/address-rect', views.AddressRect.as_view(), name='address_rect'),
    path('api/search/insights', views.InsightsView.as_view(), name='insights'),
    path('api/search/links', views.HtmlSitemap.as_view(), name='links'),
]
