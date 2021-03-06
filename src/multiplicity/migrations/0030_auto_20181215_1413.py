# Generated by Django 2.1.3 on 2018-12-15 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multiplicity', '0029_information_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencespacetype',
            name='marker_color',
            field=models.CharField(blank=True, choices=[('blue', 'Blue'), ('red', 'Red'), ('green', 'Green'), ('darkblue', 'Dark Blue'), ('purple', 'Purple'), ('yellow', 'yellow'), ('orange', 'Orange'), ('black', 'Black'), ('grey', 'Grey'), ('pink', 'Pink'), ('brightgreen', 'Bright green'), ('white', 'White')], default='blue', max_length=10, null=True),
        ),
    ]
