# Generated by Django 3.1.4 on 2021-01-04 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiodist', '0007_auto_20210104_0458'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='cover',
            field=models.ImageField(blank=True, default='black.jpeg', null=True, upload_to='covers/'),
        ),
    ]
