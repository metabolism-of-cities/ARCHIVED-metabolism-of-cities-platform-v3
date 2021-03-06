# Generated by Django 2.2.2 on 2019-10-23 14:41

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_auto_20191022_1602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='casestudy',
            options={'verbose_name_plural': 'case studies'},
        ),
        migrations.RemoveField(
            model_name='tag',
            name='gps',
        ),
        migrations.AlterField(
            model_name='tag',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='hidden',
            field=models.BooleanField(db_index=True, default=False, help_text='Mark if tag is superseded/not yet approved/deactivated'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='parent',
            field=models.CharField(blank=True, choices=[(1, 'Publication Types'), (2, 'Metabolism Studies'), (3, 'Countries'), (4, 'Cities'), (5, 'Scales'), (6, 'Flows'), (7, 'Time Horizon'), (9, 'Methodologies'), (10, 'Other')], help_text='This was a previous classification - can be left empty', max_length=2, null=True),
        ),
    ]
