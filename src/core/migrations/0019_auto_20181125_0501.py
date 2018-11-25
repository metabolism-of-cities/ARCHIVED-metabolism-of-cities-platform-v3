# Generated by Django 2.1.3 on 2018-11-25 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20181104_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='language',
            field=models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish'), ('CH', 'Chinese'), ('FR', 'French'), ('GE', 'German'), ('NL', 'Dutch'), ('OT', 'Other')], max_length=2),
        ),
    ]