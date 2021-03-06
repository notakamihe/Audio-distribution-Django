# Generated by Django 3.1.4 on 2021-01-04 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0011_auto_20210104_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='artist',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='audiodist.artist'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='collection',
            name='kind',
            field=models.CharField(choices=[('collection', 'Collection'), ('playlist', 'Playlist'), ('ep', 'EP'), ('album', 'Album'), ('lp', 'LP'), ('compilation', 'Compilation'), ('mixtape', 'Mixtape')], default='Collection', max_length=25),
        ),
    ]
