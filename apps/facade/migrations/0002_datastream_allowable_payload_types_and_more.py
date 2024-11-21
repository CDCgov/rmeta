# Generated by Django 5.0.9 on 2024-11-20 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('facade', '0001_initial'),
        ('report_metadata', '0062_alter_requestaccess_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='datastream',
            name='allowable_payload_types',
            field=models.ManyToManyField(blank=True, related_name='allowable_payload_types', to='report_metadata.healthdatatype'),
        ),
        migrations.AddField(
            model_name='origin',
            name='data_streams',
            field=models.ManyToManyField(blank=True, related_name='data_streams', to='facade.datastream'),
        ),
        migrations.AlterField(
            model_name='datastream',
            name='reviewers',
            field=models.ManyToManyField(blank=True, related_name='reviewers', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='datastream',
            name='submitters',
            field=models.ManyToManyField(blank=True, related_name='submitters', to='auth.group'),
        ),
    ]
