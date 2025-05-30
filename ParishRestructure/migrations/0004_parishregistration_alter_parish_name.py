# Generated by Django 4.2.5 on 2024-02-21 01:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ParishRestructure', '0003_remove_location_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParishRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('date_of_establishment', models.DateField()),
                ('founding_patron', models.CharField(blank=True, max_length=100, null=True)),
                ('name_of_shepherd', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.CharField(blank=True, max_length=25, null=True)),
                ('date_applied', models.DateTimeField(auto_now_add=True)),
                ('date_approved', models.DateTimeField(blank=True, null=True)),
                ('date_issued_certificate', models.DateTimeField(blank=True, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('diocese', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ParishRestructure.location')),
            ],
        ),
        migrations.AlterField(
            model_name='parish',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ParishRestructure.parishregistration'),
        ),
    ]
