# Generated by Django 2.2.2 on 2019-10-24 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0104_auto_20191024_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='method',
            name='internal_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
