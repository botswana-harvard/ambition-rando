# Generated by Django 2.0.1 on 2018-01-17 16:19

from django.db import migrations
import django.db.models.manager
import edc_base.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_rando', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='randomizationlist',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', edc_base.sites.managers.CurrentSiteManager('allocated_site')),
            ],
        ),
    ]