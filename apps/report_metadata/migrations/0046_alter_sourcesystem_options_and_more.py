# Generated by Django 5.0.2 on 2024-03-21 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report_metadata', '0045_sourcesystem_jurasdiction_sourcesystem_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sourcesystem',
            options={'ordering': ['program_area'], 'verbose_name': 'System: Data Source', 'verbose_name_plural': 'Systems: Data Sources'},
        ),
        migrations.RenameField(
            model_name='sourcesystem',
            old_name='jurasdiction',
            new_name='jurisdiction',
        ),
    ]
