# Generated by Django 2.2.7 on 2019-11-26 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0119_project_methodologies_processing_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='cityloops',
            field=models.BooleanField(default=False),
        ),
    ]
