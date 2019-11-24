# Generated by Django 2.2.2 on 2019-11-24 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0114_auto_20191120_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='methodologies_tags',
            field=models.ManyToManyField(limit_choices_to={'parent_tag__id': 318}, to='core.Tag'),
        ),
    ]
