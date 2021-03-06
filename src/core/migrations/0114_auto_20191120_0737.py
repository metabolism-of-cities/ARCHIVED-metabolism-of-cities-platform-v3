# Generated by Django 2.2.2 on 2019-11-20 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0113_auto_20191112_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='method',
            name='complete',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='method',
            name='representative_paper',
            field=models.TextField(blank=True, help_text='Which paper is a representative case study using this methodology?', null=True),
        ),
    ]
