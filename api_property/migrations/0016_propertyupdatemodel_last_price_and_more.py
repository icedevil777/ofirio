# Generated by Django 4.0.6 on 2022-11-17 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_property', '0015_delete_gooddealsmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyupdatemodel',
            name='last_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='propertyupdatemodel',
            name='last_status',
            field=models.CharField(default='', max_length=32, blank=True),
        ),
    ]