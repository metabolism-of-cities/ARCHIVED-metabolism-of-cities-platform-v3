# Generated by Django 2.1.3 on 2018-11-25 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20181125_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='authors',
            field=models.ManyToManyField(blank=True, to='core.People'),
        ),
        migrations.AlterField(
            model_name='reference',
            name='tags',
            field=models.ManyToManyField(blank=True, limit_choices_to={'hidden': False}, to='core.Tag'),
        ),
    ]