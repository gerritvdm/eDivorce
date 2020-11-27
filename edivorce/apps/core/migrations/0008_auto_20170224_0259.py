# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170210_1702'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userresponse',
            unique_together=set([('bceid_user', 'question')]),
        ),
    ]
