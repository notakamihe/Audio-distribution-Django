# Generated by Django 3.1.4 on 2021-01-04 00:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='date_published',
        ),
        migrations.AddField(
            model_name='song',
            name='release_date',
            field=models.DateField(default=datetime.datetime(2021, 1, 4, 0, 50, 45, 366381)),
        ),
    ]