# Generated by Django 2.2.15 on 2020-11-26 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_document_filing_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userresponse',
            options={'ordering': ('question__summary_order',)},
        ),
    ]
