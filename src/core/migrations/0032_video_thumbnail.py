# Generated by Django 2.1.3 on 2019-01-19 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20190119_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='video_thumbnails'),
        ),
    ]
