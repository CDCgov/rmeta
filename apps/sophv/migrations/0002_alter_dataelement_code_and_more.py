# Generated by Django 5.0.9 on 2024-12-16 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sophv', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataelement',
            name='code',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='code_display',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='code_system',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='code_system_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='code_system_version',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='fhir_code',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='fhir_code_display',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='fhir_code_system',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='fhir_code_system_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='fhir_code_system_version',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='version',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]