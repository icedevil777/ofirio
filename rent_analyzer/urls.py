from django.urls import path
from . import views

app_name = 'rent_analyzer'
urlpatterns = [
    path('api/rent_estimator', views.RentAnalyzer.as_view(), name='rent_estimator'), #deprecated
    path('api/rent-analyzer', views.RentAnalyzer.as_view(), name='rent_analyzer'), #new
    path('api/rent_estimator/analytics', views.Analytics.as_view(), name='rent_estimator_analytics'),
]
