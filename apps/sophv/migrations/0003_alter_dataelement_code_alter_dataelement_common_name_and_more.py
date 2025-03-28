# Generated by Django 5.0.9 on 2024-12-16 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sophv', '0002_alter_dataelement_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataelement',
            name='code',
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='common_name',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='fhir_code',
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='oid',
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
