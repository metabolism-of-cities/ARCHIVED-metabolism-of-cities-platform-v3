# Generated by Django 2.1.2 on 2018-11-03 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_tag_parent_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='gps',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
