# Generated by Django 4.0.6 on 2022-11-24 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0027_track_new_good_deal_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='favoriteproperty',
            name='status',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]
