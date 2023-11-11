from django.contrib.auth import get_user_model
from django.db import models

from common.encoders import DjangoNumpyJSONEncoder
from common.models import BaseModel
from reports.enums import ReportType


User = get_user_model()


def _generate_upload_path(instance, filename):
    """Calculate final upload path for report_file"""
    report_type = instance.report_type.replace('_', '-')
    base_name = filename.split('.')[-2].split('-')
    key = base_name[-1]
    year_month = base_name[-2][:6]
    path = f'{report_type}/{year_month}/{key[:2]}/{filename}'
    return path


class Report(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100, choices=ReportType.choices)
    report_file = models.FileField(upload_to=_generate_upload_path)

    # values came from client in report request
    query = models.JSONField()

    # values we calculated or took from another DB
    data = models.JSONField(encoder=DjangoNumpyJSONEncoder)

    # values used on report list screen
    list_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.report_type} of {self.user}'
