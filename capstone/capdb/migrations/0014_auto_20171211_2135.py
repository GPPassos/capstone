# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-11 21:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capdb', '0013_auto_20171211_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackingtooluser',
            name='email',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='volumemetadata',
            name='duplicate',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='volumemetadata',
            name='hand_feed',
            field=models.BooleanField(default=False, help_text='Instructions for operator, not whether or not it happened'),
        ),
        migrations.AlterField(
            model_name='volumemetadata',
            name='has_marginalia',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='volumemetadata',
            name='out_of_scope',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='volumemetadata',
            name='publisher_deleted_pages',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='volumemetadata',
            name='rare',
            field=models.BooleanField(default=False),
        ),
    ]