# Generated by Django 5.0.2 on 2024-03-19 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0032_alter_rmetamessage_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonHashType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='', max_length=255, unique=True)),
                ('name', models.CharField(default='', max_length=255)),
                ('prefix', models.CharField(default='', max_length=255)),
                ('series', models.SmallIntegerField(default=1)),
                ('description', models.TextField(blank=True, default='', max_length=2048)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Types: Person Hash',
                'verbose_name_plural': 'Types: Person Hashes',
            },
        ),
        migrations.RenameField(
            model_name='anonyomizeddataneed',
            old_name='rmeta_field_name',
            new_name='message_field_name',
        ),
        migrations.AddField(
            model_name='anonyomizeddataneed',
            name='other_path',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AddField(
            model_name='anonyomizeddataneed',
            name='other_url',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AddField(
            model_name='rmetamessage',
            name='cdc_payload_csv',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='rmetamessage',
            name='cdc_payload_json',
            field=models.TextField(blank=True, default=''),
        ),
    ]
