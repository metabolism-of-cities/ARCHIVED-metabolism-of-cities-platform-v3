# Generated by Django 2.2.2 on 2019-11-24 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0115_auto_20191124_0802'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='eu_contribution',
        ),
        migrations.AddField(
            model_name='project',
            name='material_temp_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
