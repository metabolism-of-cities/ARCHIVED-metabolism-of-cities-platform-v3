# Generated by Django 2.1.3 on 2019-02-08 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20190206_0350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='thesistype',
            field=models.CharField(blank=True, choices=[('bachelor', 'Bachelor'), ('masters', 'Master'), ('phd', 'PhD'), ('other', 'Other')], max_length=20, null=True),
        ),
    ]
