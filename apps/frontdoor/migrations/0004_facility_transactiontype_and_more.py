# Generated by Django 5.0.9 on 2025-02-26 17:00

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdoor', '0003_rename_submission_transactionhistory_transaction'),
        ('report_metadata', '0062_alter_requestaccess_notes'),
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField()),
                ('postal_code', models.CharField(blank=True, max_length=10)),
                ('url', models.URLField(blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('date_created', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='transactionhistory',
            name='transaction',
        ),
        migrations.RenameField(
            model_name='origin',
            old_name='data_streams',
            new_name='transaction_types',
        ),
        migrations.RemoveField(
            model_name='datastream',
            name='program_area',
        ),
        migrations.RemoveField(
            model_name='origin',
            name='application',
        ),
        migrations.AddField(
            model_name='origin',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField()),
                ('url', models.URLField(blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('program_area', models.ManyToManyField(blank=True, related_name='program_area', to='report_metadata.programareatype')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitter_tcn', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Transaction Control Number')),
                ('submitter_tcr', models.CharField(blank=True, db_index=True, max_length=64, verbose_name='Transaction Control Reference')),
                ('destination_tcn', models.CharField(blank=True, default=uuid.uuid4, help_text='The TCN of the transaction that this transaction is a response to.', max_length=100, verbose_name='Destination Transaction Control Number')),
                ('status_url', models.URLField(blank=True, default='http://localhost:8000')),
                ('status', models.CharField(blank=True, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')], default='PENDING', max_length=20)),
                ('inbound_source_type', models.CharField(blank=True, choices=[('REST-SUBMIT-API', 'Base Submission API'), ('FHIR-PROCESS-MESSAGE-API', 'FHIR Bundle Submission via process message endpoint.'), ('FILE-DROP', 'File/folder drop such as SFTP or AWS S3'), ('WEB-FORM', 'Front Door Web Forms'), ('EMAIL-ENCRYPTED', 'Encrypted Email'), ('EMAIL-DIRECT', 'Submitted using DIRECT Protocol')], max_length=120)),
                ('person_id', models.CharField(blank=True, max_length=100)),
                ('person_id_issuer', models.CharField(blank=True, max_length=100)),
                ('metadata_json', models.TextField(blank=True)),
                ('metadata_file', models.FileField(blank=True, upload_to='uploads/metadata/')),
                ('payload_txt', models.TextField(blank=True)),
                ('payload_bin', models.BinaryField(blank=True)),
                ('payload_file', models.FileField(blank=True, upload_to='uploads/payloads/')),
                ('payload_hash', models.CharField(blank=True, max_length=100)),
                ('payload_server_reference', models.CharField(blank=True, max_length=100)),
                ('response_json', models.TextField(blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('contributors', models.ManyToManyField(blank=True, related_name='contributors', to='frontdoor.origin')),
                ('destination', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='frontdoor.destination')),
                ('facility_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='frontdoor.facility')),
                ('origin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='originating_agency', to='frontdoor.origin', verbose_name='Originating Agency Identifier')),
                ('payload_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_metadata.healthdatatype')),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')], max_length=16)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('submission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='frontdoor.submission')),
            ],
            options={
                'verbose_name': 'Transaction History',
                'verbose_name_plural': 'Transaction Histories',
            },
        ),
        migrations.CreateModel(
            name='Submitter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('url', models.URLField(blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_updated', models.DateField(auto_now=True)),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontdoor.origin')),
                ('transaction_types', models.ManyToManyField(blank=True, related_name='submitter_tx_types', to='frontdoor.transactiontype')),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='submitter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitter_agency', to='frontdoor.submitter', verbose_name='Submitter Agency Identifier'),
        ),
        migrations.AddField(
            model_name='submission',
            name='transaction_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_tx_types', to='frontdoor.transactiontype'),
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
    ]
