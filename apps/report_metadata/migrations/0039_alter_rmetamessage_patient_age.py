# Generated by Django 5.0.2 on 2024-03-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0038_alter_rmetamessage_source_patient_id_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rmetamessage',
            name='patient_age',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
    ]
