# Generated by Django 5.1.6 on 2025-03-23 14:40

import datetime
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gramapp', '0011_remove_userprofile_profile_picture_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='taxpayment',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2026, 3, 23, 14, 40, 52, 495834, tzinfo=datetime.timezone.utc)),
        ),
    ]
