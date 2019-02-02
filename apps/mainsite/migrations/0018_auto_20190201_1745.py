# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-02 01:45
from __future__ import unicode_literals

from django.db import migrations
from mainsite.utils import generate_random_fake_badge_connect_domain


def run_data(apps, schema_editor):
    ApplicationInfo = apps.get_model('mainsite', 'ApplicationInfo')
    for row in ApplicationInfo.objects.all():
        row.manifest_domain = generate_random_fake_badge_connect_domain()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mainsite', '0017_auto_20190201_1743'),
    ]

    operations = [
        migrations.RunPython(run_data, reverse_code=migrations.RunPython.noop),
    ]
