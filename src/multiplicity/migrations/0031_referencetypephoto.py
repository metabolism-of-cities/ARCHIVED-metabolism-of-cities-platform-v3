# Generated by Django 2.1.3 on 2018-12-19 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0030_auto_20181215_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceTypePhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiplicity.Photo')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiplicity.ReferenceSpace')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiplicity.ReferenceSpaceType')),
            ],
        ),
    ]
