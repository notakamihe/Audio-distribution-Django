# Generated by Django 3.1.4 on 2021-01-04 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0005_artist_pfp'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='name',
            field=models.CharField(default='Artist', max_length=60),
        ),
    ]
