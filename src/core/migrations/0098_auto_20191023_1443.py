# Generated by Django 2.2.2 on 2019-10-23 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_auto_20191023_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='method',
            name='between_flows',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], help_text='Specification of flows between sectors, industries or acticity fields, or other system components', max_length=1, null=True, verbose_name='between-flows'),
        ),
        migrations.AlterField(
            model_name='method',
            name='energy',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='method',
            name='materials',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True, verbose_name='materials / bulk materials'),
        ),
        migrations.AlterField(
            model_name='method',
            name='outputs',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True, verbose_name='outputs to environment'),
        ),
        migrations.AlterField(
            model_name='method',
            name='production',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True, verbose_name='production processes'),
        ),
        migrations.AlterField(
            model_name='method',
            name='recycling',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True, verbose_name='recyling of material and energy'),
        ),
        migrations.AlterField(
            model_name='method',
            name='specific',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True, verbose_name='specific goods and services'),
        ),
        migrations.AlterField(
            model_name='method',
            name='stock_changes',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], max_length=1, null=True, verbose_name='stock changes'),
        ),
        migrations.AlterField(
            model_name='method',
            name='substances',
            field=models.CharField(blank=True, choices=[('3', '3 - The item is a defining feature of the approach'), ('2', '2 - The feature is typically included in the techique'), ('1', '1 - The item is included only occasionally in the mode of analysis, and in a partial or conditional way')], help_text='Elements and basic compounds only', max_length=2, null=True, verbose_name='selected specific substances'),
        ),
    ]
