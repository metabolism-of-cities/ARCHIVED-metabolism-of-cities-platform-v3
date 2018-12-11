# Generated by Django 2.1.3 on 2018-12-11 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staf', '0011_auto_20181208_0714'),
        ('core', '0021_auto_20181125_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='processes',
            field=models.ManyToManyField(blank=True, limit_choices_to={'slug__isnull': False}, to='staf.Process'),
        ),
    ]