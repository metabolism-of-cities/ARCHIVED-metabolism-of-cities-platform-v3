# Generated by Django 2.2.2 on 2019-08-02 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('multiplicity', '0050_auto_20190701_0635'),
        ('core', '0071_auto_20190802_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataViz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=255, null=True)),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('process_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multiplicity.ProcessGroup')),
                ('reference', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Reference')),
                ('space', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multiplicity.ReferenceSpace')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
