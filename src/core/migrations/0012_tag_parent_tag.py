# Generated by Django 2.1.2 on 2018-11-03 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20181030_0101'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='parent_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Tag'),
        ),
    ]
