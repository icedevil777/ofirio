# Generated by Django 3.2.4 on 2021-06-15 11:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogpost',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='blogtag',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogtag',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
