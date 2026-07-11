from django.test import TestCase

from hymns.models import Hymn, Hymnal, HymnalEntry, Tune
from hymns.services import normalize_title


class HymnModelTests(TestCase):
    def test_same_title_can_exist_in_multiple_hymnals_and_numbers(self):
        umh = Hymnal.objects.create(code="UMH", title="The United Methodist Hymnal")
        bh = Hymnal.objects.create(code="BH1991", title="Baptist Hymnal 1991")
        hymn = Hymn.objects.create(
            canonical_title="Amazing Grace",
            normalized_title=normalize_title("Amazing Grace"),
            first_line="Amazing grace! How sweet the sound",
            author="John Newton",
        )
        tune = Tune.objects.create(name="NEW BRITAIN", meter="CM")

        entry1 = HymnalEntry.objects.create(
            hymnal=umh,
            number="378",
            title_as_printed="Amazing Grace",
            tune_as_printed="AMAZING GRACE",
            hymn=hymn,
            tune=tune,
            is_approved=True,
        )
        entry2 = HymnalEntry.objects.create(
            hymnal=bh,
            number="330",
            title_as_printed="Amazing Grace! How Sweet the Sound",
            tune_as_printed="NEW BRITAIN",
            hymn=hymn,
            tune=tune,
            is_approved=True,
        )

        self.assertNotEqual(entry1.id, entry2.id)
        self.assertEqual(HymnalEntry.objects.filter(hymn=hymn).count(), 2)

    def test_number_suffixes_are_distinct_entries(self):
        hymnal = Hymnal.objects.create(code="UMH", title="The United Methodist Hymnal")
        HymnalEntry.objects.create(hymnal=hymnal, number="57", title_as_printed="O for a thousand tongues")
        HymnalEntry.objects.create(hymnal=hymnal, number="57b", title_as_printed="O for a thousand tongues")
        self.assertEqual(hymnal.entries.count(), 2)
