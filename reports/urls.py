from django.urls import path

from reports.views import PropertyReportCreateView, RentAnalyzerReportCreateView, ReportList


app_name = 'reports'
urlpatterns = [
    path('api/report/property', PropertyReportCreateView.as_view(), name='property_report'),
    path(
        'api/report/rent_analyzer', RentAnalyzerReportCreateView.as_view(),
        name='rent_analyzer_report',
    ),
    path('api/report/reports', ReportList.as_view(), name='report_list'),
]
