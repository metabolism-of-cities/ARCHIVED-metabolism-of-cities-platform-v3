# Generated by Django 2.1.3 on 2019-01-30 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0040_auto_20190129_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='referencespace',
            name='mtu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multiplicity.MTU'),
        ),
        migrations.AlterField(
            model_name='mtu',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mtu_list', to='multiplicity.ReferenceSpace'),
        ),
    ]
