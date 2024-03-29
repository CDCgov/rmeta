# Generated by Django 5.0.2 on 2024-03-11 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0013_anonyomizeddataneed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anonyomizeddataneed',
            name='hippa_id',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='anonyomizeddataneed',
            name='in_syndromic_message',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='anonyomizeddataneed',
            name='keep',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='sourcesystem',
            name='other_supported_data_input_types',
            field=models.ManyToManyField(blank=True, related_name='other_dest_input_type', to='report_metadata.healthdatatype'),
        ),
        migrations.AlterField(
            model_name='sourcesystem',
            name='other_supported_data_ouput_types',
            field=models.ManyToManyField(blank=True, related_name='other_supported_source_output_data_types', to='report_metadata.healthdatatype'),
        ),
    ]
