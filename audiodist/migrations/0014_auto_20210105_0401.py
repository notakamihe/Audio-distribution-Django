# Generated by Django 3.1.4 on 2021-01-05 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0013_auto_20210104_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='kind',
            field=models.CharField(choices=[('Collection', 'Collection'), ('Playlist', 'Playlist'), ('EP', 'EP'), ('Album', 'Album'), ('LP', 'LP'), ('Compilation', 'Compilation'), ('Mixtape', 'Mixtape')], default='Collection', max_length=25),
        ),
    ]