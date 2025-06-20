# Generated by Django 5.0.1 on 2024-03-05 05:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HATApp', '0003_person_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('feedback', models.TextField()),
                ('date', models.DateField(auto_now=True)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HATApp.person')),
            ],
        ),
    ]
