# Generated by Django 2.1.3 on 2018-11-03 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20181103_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='hidden',
            field=models.BooleanField(db_index=True, default=False, null=True),
        ),
    ]
