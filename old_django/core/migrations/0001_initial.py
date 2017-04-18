# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 13:56
from __future__ import unicode_literals

import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DonkeyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.CharField(max_length=256, null=True, unique=True, verbose_name='encrypted email address')),
                ('nickname', models.CharField(default=core.utils.random_digit_and_number, max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_confirm', models.BooleanField(default=False)),
                ('is_block', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BulletinBoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_status', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=200)),
                ('desc', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegionA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegionB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.IntegerField()),
                ('region_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.RegionA')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_key', models.CharField(max_length=50)),
                ('name_value', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_update', models.IntegerField(default=2017)),
                ('code', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('domain', models.CharField(max_length=100)),
                ('region_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.RegionA')),
                ('region_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.RegionB')),
                ('school_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.SchoolType')),
            ],
        ),
        migrations.CreateModel(
            name='UniversityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBoardConnector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bulletin_board_id_str', models.TextField(null=True)),
                ('donkey_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='university',
            name='university_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.UniversityType'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='department',
            field=models.ManyToManyField(null=True, to='core.Department'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='region_a',
            field=models.ManyToManyField(null=True, to='core.RegionA'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='region_b',
            field=models.ManyToManyField(null=True, to='core.RegionB'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='school_type',
            field=models.ManyToManyField(null=True, to='core.SchoolType'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='university',
            field=models.ManyToManyField(null=True, to='core.University'),
        ),
        migrations.AddField(
            model_name='bulletinboard',
            name='university_type',
            field=models.ManyToManyField(null=True, to='core.UniversityType'),
        ),
        migrations.AddField(
            model_name='donkeyuser',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Department'),
        ),
        migrations.AddField(
            model_name='donkeyuser',
            name='university',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.University'),
        ),
    ]
