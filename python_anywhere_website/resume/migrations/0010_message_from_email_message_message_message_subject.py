# Generated by Django 4.0.6 on 2022-07-19 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resume", "0009_remove_message_message_remove_message_subject"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="from_email",
            field=models.EmailField(
                default="this_is_not_an_email_address", max_length=254
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="message",
            field=models.TextField(default="this_is_not_an_email_address"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="message",
            name="subject",
            field=models.CharField(default="this_is_not_a_subject", max_length=254),
            preserve_default=False,
        ),
    ]
