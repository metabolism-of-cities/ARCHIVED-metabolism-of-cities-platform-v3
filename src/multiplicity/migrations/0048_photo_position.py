# Generated by Django 2.1.3 on 2019-04-06 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0047_auto_20190320_0544'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='position',
            field=models.PositiveSmallIntegerField(default=99),
        ),
    ]
