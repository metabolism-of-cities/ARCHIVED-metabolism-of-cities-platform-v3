# Generated by Django 2.1.3 on 2018-12-13 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='entry_exam',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='category_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
