# Generated by Django 2.1.3 on 2019-04-25 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_auto_20190425_0755'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='collection',
            new_name='collections',
        ),
    ]
