# Generated by Django 4.0.6 on 2022-10-28 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_alter_email_settings_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailsettings',
            name='favorites',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='emailsettings',
            name='good_deals',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='emailsettings',
            name='prop_updates',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='emailsettings',
            name='similars',
            field=models.BooleanField(default=False),
        ),
    ]
