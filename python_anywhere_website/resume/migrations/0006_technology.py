# Generated by Django 4.0.4 on 2022-04-16 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resume", "0005_certification"),
    ]

    operations = [
        migrations.CreateModel(
            name="Technology",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("short_description", models.CharField(max_length=100)),
                ("long_description", models.TextField(blank=True)),
                ("start_date", models.DateField(blank=True, null=True)),
            ],
        ),
    ]
