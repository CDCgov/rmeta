# Generated by Django 5.0.9 on 2025-03-05 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdoor', '0010_alter_submission_transaction_control_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='transaction_control_number',
            field=models.CharField(db_index=True, max_length=64, verbose_name='Transaction Control Number'),
        ),
    ]
