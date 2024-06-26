# Generated by Django 5.0.2 on 2024-06-26 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0061_alter_requestaccess_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestaccess',
            name='notes',
            field=models.TextField(blank=True, help_text='Please provide any additional information \n                             that may be helpful in processing your request.\n                            If you are requesting write access, please indicate here.', null=True),
        ),
    ]