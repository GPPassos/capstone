# Generated by Django 2.0.2 on 2018-05-25 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capdb', '0039_auto_20180521_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='casexml',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcasexml',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalpagexml',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalvolumexml',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pagexml',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='volumemetadata',
            name='xml_checksums_need_update',
            field=models.BooleanField(default=False, help_text='Whether checksums in volume_xml match current values in related case_xml and page_xml data.'),
        ),
        migrations.AddField(
            model_name='volumexml',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]