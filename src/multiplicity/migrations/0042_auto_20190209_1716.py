# Generated by Django 2.1.3 on 2019-02-09 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0041_auto_20190130_2020'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceSpaceSector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sectors', to='multiplicity.ReferenceSpace')),
            ],
        ),
        migrations.AddField(
            model_name='topic',
            name='color',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='referencespacesector',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiplicity.Topic'),
        ),
    ]
