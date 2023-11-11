from django.urls import path
from sale_estimator import views

app_name = 'sale_estimator'
urlpatterns = [
    path('api/sale_estimator', views.SaleEstimatorView.as_view(), name='sale_estimator'),
]
