# Generated by Django 3.1.5 on 2021-01-31 02:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('needley', '0002_auto_20210130_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avator',
            field=models.URLField(blank=True, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
    ]