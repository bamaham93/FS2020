# Generated by Django 4.0.6 on 2022-08-02 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prayer', '0005_prayermessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('may_send_emails', models.BooleanField()),
                ('may_send_sms', models.BooleanField()),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='prayer.prayerprofile')),
            ],
        ),
    ]
