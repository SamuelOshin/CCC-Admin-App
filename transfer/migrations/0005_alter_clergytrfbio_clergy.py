# Generated by Django 4.2.5 on 2024-05-11 02:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clergy_registration', '0004_alter_annointmentgazzette_rank_and_more'),
        ('transfer', '0004_remove_clergytrfbio_note_alter_clergytrfbio_clergy_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clergytrfbio',
            name='clergy',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='clergy_registration.clergydetails'),
        ),
    ]
