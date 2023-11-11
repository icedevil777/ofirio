from rest_framework import serializers

from reports.models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = 'created_at', 'report_type', 'query', 'report_file', 'list_data'


class CreatedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = 'report_file',
