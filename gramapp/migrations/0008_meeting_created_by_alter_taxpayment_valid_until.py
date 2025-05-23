# Generated by Django 5.1.6 on 2025-03-16 21:51

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gramapp', '0007_panchayatmember_alter_taxpayment_valid_until'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='taxpayment',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2026, 3, 16, 21, 51, 40, 861010, tzinfo=datetime.timezone.utc)),
        ),
    ]
