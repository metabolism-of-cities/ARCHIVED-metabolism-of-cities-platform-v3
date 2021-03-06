# Generated by Django 2.1.3 on 2018-12-01 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staf', '0007_process_code'),
        ('multiplicity', '0019_auto_20181127_2033'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('processes', models.ManyToManyField(blank=True, to='staf.Process')),
            ],
        ),
    ]
