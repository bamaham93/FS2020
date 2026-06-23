# Generated migration to associate prayer people with Django users.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("prayer", "0012_prayermessage_direct_recipients"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="user",
            field=models.OneToOneField(
                blank=True,
                help_text="Optional Django user account associated with this person.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="prayer_person",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
