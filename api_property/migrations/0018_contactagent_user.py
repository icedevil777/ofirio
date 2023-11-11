# Generated by Django 4.0.6 on 2022-11-23 14:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_property', '0017_rename_last_price_propertyupdatemodel_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactagent',
            name='user',
            field=models.ManyToManyField(null=True, related_name='leads', to=settings.AUTH_USER_MODEL),
        ),
    ]