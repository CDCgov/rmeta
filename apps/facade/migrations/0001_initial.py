# Generated by Django 5.0.9 on 2024-11-20 15:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('report_metadata', '0062_alter_requestaccess_notes'),
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('reviewers', models.ManyToManyField(blank=True, null=True, related_name='reviewers', to='auth.group')),
                ('submitters', models.ManyToManyField(blank=True, null=True, related_name='submitters', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('url', models.URLField(blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tcn', models.CharField(blank=True, max_length=100, verbose_name='Transaction Control Number')),
                ('tcr', models.CharField(blank=True, max_length=100, verbose_name='Transaction Control Reference')),
                ('dai_tcn', models.CharField(blank=True, max_length=100, verbose_name='Destination Transaction Control Number')),
                ('cri_1', models.CharField(blank=True, max_length=100, verbose_name='Contributing Identifier 1')),
                ('cri_2', models.CharField(blank=True, max_length=100, verbose_name='Contributing Identifier 2')),
                ('cri_3', models.CharField(blank=True, max_length=100, verbose_name='Contributing Identifier 3')),
                ('cri_4', models.CharField(blank=True, max_length=100, verbose_name='Contributing Identifier 4')),
                ('cri_5', models.CharField(blank=True, max_length=100, verbose_name='Contributing Identifier 5')),
                ('dai', models.CharField(blank=True, default='CDC-1CDP-1', max_length=100, verbose_name='Destination Agency Identifier')),
                ('status_url', models.URLField(blank=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')], max_length=100)),
                ('multiple_entries', models.BooleanField(blank=True, default=False)),
                ('payload', models.TextField(blank=True)),
                ('payload_file', models.FileField(blank=True, upload_to='uploads/')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('ori', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='originating_agency', to='facade.origin', verbose_name='Originating Agency Identifier')),
                ('payload_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_metadata.healthdatatype')),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')], max_length=100)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facade.submission')),
            ],
        ),
    ]
