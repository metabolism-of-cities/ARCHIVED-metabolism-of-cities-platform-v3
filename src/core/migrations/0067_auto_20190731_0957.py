# Generated by Django 2.2.2 on 2019-07-31 09:57

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_auto_20190731_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
