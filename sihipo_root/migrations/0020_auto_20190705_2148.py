# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-05 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sihipo_root', '0019_auto_20190515_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantcontrollogdetail',
            name='val',
            field=models.IntegerField(choices=[(0, 'Normally Open'), (1, 'Normally Close'), (2, 'Toggle')], default=0, verbose_name='Nilai'),
        ),
    ]
