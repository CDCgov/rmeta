# Generated by Django 5.0.2 on 2024-03-11 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0014_alter_anonyomizeddataneed_hippa_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='anonyomizeddataneed',
            name='pprl_hash',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
