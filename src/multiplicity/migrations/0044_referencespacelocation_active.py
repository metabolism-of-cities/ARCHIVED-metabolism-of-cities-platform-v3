# Generated by Django 2.1.3 on 2019-03-04 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0043_auto_20190209_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='referencespacelocation',
            name='active',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]