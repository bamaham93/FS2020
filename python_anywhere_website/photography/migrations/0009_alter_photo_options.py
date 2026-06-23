# Generated migration to align Photo model ordering options.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("photography", "0008_photoessay_ordering_tiebreaker"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="photo",
            options={"ordering": ["-created_at"]},
        ),
    ]
