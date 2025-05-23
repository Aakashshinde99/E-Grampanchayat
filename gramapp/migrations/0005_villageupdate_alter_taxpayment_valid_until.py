# Generated by Django 5.1.6 on 2025-03-16 21:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gramapp', '0004_alter_taxpayment_valid_until'),
    ]

    operations = [
        migrations.CreateModel(
            name='VillageUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='taxpayment',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2026, 3, 16, 21, 11, 17, 120142, tzinfo=datetime.timezone.utc)),
        ),
    ]
