# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-08-15 19:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_route_route_short_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='trip_headsign',
        ),
    ]