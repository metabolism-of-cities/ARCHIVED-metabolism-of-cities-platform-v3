# Generated by Django 2.1.3 on 2019-02-12 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_auto_20190212_0403'),
    ]

    operations = [
        migrations.AddField(
            model_name='videocollection',
            name='show_in_list',
            field=models.BooleanField(default=True),
        ),
    ]
