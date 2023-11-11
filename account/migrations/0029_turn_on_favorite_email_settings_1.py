from django.db import migrations


def migrate(apps, schema_editor):
    try:
        User = apps.get_model('account.CustomUser')
        EmailSettings = apps.get_model('account.EmailSettings')
        import datetime
        for user in User.objects.all():
            if user.created_at.timestamp() <= datetime.datetime(year=2022, month=11, day=15).timestamp() and user.favoriteproperty_set.first():
                e_settings = EmailSettings.objects.get(user=user)
                e_settings.favorites = True
                e_settings.favorites_match_notification = True
                e_settings.save()
    except Exception as exc:
        print('Migration account.0029 failed:', exc)
        print('But probably there is nothing to worry about')


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0028_favoriteproperty_status'),
    ]

    operations = [
        migrations.RunPython(migrate)
    ]
