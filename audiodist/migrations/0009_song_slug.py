# Generated by Django 3.1.4 on 2021-01-04 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0008_song_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, null=True),
        ),
    ]
