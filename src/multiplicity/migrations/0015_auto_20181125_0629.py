# Generated by Django 2.1.3 on 2018-11-25 06:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0014_topic_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='information',
            name='dataset_types',
            field=models.ManyToManyField(blank=True, to='multiplicity.DatasetType'),
        ),
        migrations.AlterField(
            model_name='information',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multiplicity.Topic'),
        ),
    ]
