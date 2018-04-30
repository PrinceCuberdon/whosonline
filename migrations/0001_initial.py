# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousOnline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=60)),
                ('last_visit', models.DateTimeField(help_text='Derni\xe8re heure de passage', verbose_name=b'Heure de passage', auto_now_add=True)),
                ('ip', models.GenericIPAddressField(null=True, blank=True)),
                ('referer', models.CharField(help_text=b'Derniere page visitee.', max_length=200, null=True, verbose_name=b'Derniere visite', blank=True)),
            ],
            options={
                'db_table': 'online_anonymousonline',
            },
        ),
        migrations.CreateModel(
            name='Online',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_visit', models.DateTimeField(help_text='Date de la derni\xe8re visite', verbose_name='Derni\xe8re viste')),
                ('online', models.BooleanField(help_text="Est-ce que l'utilisateur est en ligne ?", verbose_name='En Ligne')),
                ('referer', models.CharField(default=b'Non Applicable', max_length=200, blank=True, help_text=b'Derniere page visitee.', null=True, verbose_name=b'Derniere visite')),
                ('user', models.ForeignKey(verbose_name='Utilisateur', to=settings.AUTH_USER_MODEL, help_text='Utilisateur')),
            ],
            options={
                'db_table': 'online_online',
                'verbose_name': 'Qui est en ligne ?',
                'verbose_name_plural': 'Qui est en ligne ?',
            },
        ),
    ]
