# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-24 12:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sihipo_root', '0006_auto_20180819_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='plantbase',
            name='model_name',
            field=models.TextField(blank=True, null=True, verbose_name='Nama Model'),
        ),
    ]