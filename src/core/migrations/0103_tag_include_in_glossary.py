# Generated by Django 2.2.2 on 2019-10-24 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0102_auto_20191024_0638'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='include_in_glossary',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
