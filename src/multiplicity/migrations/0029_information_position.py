# Generated by Django 2.1.3 on 2018-12-15 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0028_information_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='information',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
