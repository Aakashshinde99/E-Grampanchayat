# Generated by Django 5.1.6 on 2025-04-02 15:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gramapp', '0017_alter_taxpayment_valid_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxpayment',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2026, 4, 2, 15, 10, 20, 790770, tzinfo=datetime.timezone.utc)),
        ),
    ]
