# Generated by Django 2.1.3 on 2018-11-25 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0013_referencespace_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
