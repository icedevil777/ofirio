# Generated by Django 4.0.6 on 2022-11-02 19:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_property', '0012_propertynotified'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyUpdateModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('prop_id', models.CharField(max_length=21)),
                ('prop_class', models.CharField(choices=[('invest', 'Invest'), ('buy', 'Buy'), ('rent', 'Rent')], max_length=6)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='props_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Property Updates Notification',
            },
        ),
        migrations.CreateModel(
            name='GoodDealsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('prop_id', models.CharField(max_length=21)),
                ('prop_class', models.CharField(choices=[('invest', 'Invest'), ('buy', 'Buy'), ('rent', 'Rent')], max_length=6)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='good_deals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Good Deals Notification',
            },
        ),
    ]
