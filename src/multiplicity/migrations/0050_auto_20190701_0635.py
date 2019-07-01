# Generated by Django 2.2.2 on 2019-07-01 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staf', '0014_auto_20190422_1638'),
        ('multiplicity', '0049_referencespace_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='referencespacetype',
            name='processes',
            field=models.ManyToManyField(blank=True, limit_choices_to={'slug__isnull': False}, related_name='referencespaces', to='staf.Process'),
        ),
        migrations.AlterField(
            model_name='referencespacetype',
            name='process',
            field=models.ForeignKey(blank=True, limit_choices_to={'slug__isnull': False}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dropsoon', to='staf.Process'),
        ),
    ]
