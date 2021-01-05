# Generated by Django 3.1.4 on 2021-01-04 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0009_song_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audiodist.collection')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audiodist.song')),
            ],
        ),
    ]