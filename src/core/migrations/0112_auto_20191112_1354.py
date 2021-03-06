# Generated by Django 2.2.2 on 2019-11-12 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0050_auto_20190701_0635'),
        ('core', '0111_merge_20191109_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='budget',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='cityloops',
            field=models.CharField(blank=True, choices=[('no', 'No'), ('pending', 'Yes - pending'), ('yes', 'Yes - completed')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='eu_contribution',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='funding_program',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='methodologies',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='reference_spaces',
            field=models.ManyToManyField(blank=True, limit_choices_to={'type': 3}, to='multiplicity.ReferenceSpace'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='hidden',
            field=models.BooleanField(db_index=True, default=False, help_text='Mark if tag is superseded/not yet approved/deactivated'),
        ),
    ]
