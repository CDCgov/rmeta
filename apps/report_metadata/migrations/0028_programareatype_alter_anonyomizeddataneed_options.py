# Generated by Django 5.0.2 on 2024-03-14 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0027_rename_transport_in_type_sourcesystem_input_transport_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramAreaType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='', max_length=255, unique=True)),
                ('name', models.CharField(default='', max_length=255)),
                ('adult_records_contain_child_records', models.BooleanField(blank=True, default=False)),
                ('description', models.TextField(blank=True, default='', max_length=2048)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Type: Program Area',
                'verbose_name_plural': 'Types: Program Areas',
            },
        ),
        migrations.AlterModelOptions(
            name='anonyomizeddataneed',
            options={'verbose_name': 'Anonyomized Data Need', 'verbose_name_plural': 'Anonyomized Data Needs'},
        ),
    ]
