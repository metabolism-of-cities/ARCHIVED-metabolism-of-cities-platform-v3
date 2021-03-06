# Generated by Django 2.2.2 on 2019-08-13 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0079_auto_20190807_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='site',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='people',
            name='site',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='video',
            name='site',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='videocollection',
            name='site',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sites.Site'),
        ),
    ]
