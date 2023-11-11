from django.db.models.signals import post_save
from django.dispatch import receiver
from reports.models import Report
import common.tasks as tasks


@receiver(post_save, sender=Report)
def post_report_save(sender, instance, **kwargs):
    tasks.track_report.delay(instance.user.id, instance.user.email, instance.report_type)
