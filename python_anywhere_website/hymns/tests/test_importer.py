from pathlib import Path

from django.test import TestCase

from hymns.models import HymnalEntry
from hymns.services import HymnaryImporter, HymnaryParser


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FakeClient:
    def __init__(self):
        self.pages = {
            "https://hymnary.org/hymnal/UMH": (FIXTURES / "hymnal_umh.html").read_text(),
            "https://hymnary.org/hymn/UMH/378": (FIXTURES / "instance_umh_378.html").read_text(),
            "https://hymnary.org/hymn/UMH/57": (FIXTURES / "instance_umh_378.html").read_text(),
            "https://hymnary.org/hymn/UMH/57b": (FIXTURES / "instance_umh_378.html").read_text(),
        }

    def get(self, url):
        return self.pages[url]


class HymnaryImporterTests(TestCase):
    def test_hymnal_parser_finds_instance_urls(self):
        html = (FIXTURES / "hymnal_umh.html").read_text()
        parsed = HymnaryParser().parse_hymnal(html, "UMH", "https://hymnary.org/hymnal/UMH")
        self.assertEqual(parsed.title, "The United Methodist Hymnal")
        self.assertIn("https://hymnary.org/hymn/UMH/378", parsed.entry_urls)

    def test_entry_parser_ignores_full_text_and_extracts_metadata(self):
        html = (FIXTURES / "instance_umh_378.html").read_text()
        parsed = HymnaryParser().parse_entry(html, "https://hymnary.org/hymn/UMH/378")
        self.assertEqual(parsed.number, "378")
        self.assertEqual(parsed.title, "Amazing Grace")
        self.assertEqual(parsed.first_line, "Amazing grace! How sweet the sound")
        self.assertIn("Grace", parsed.topics)
        self.assertNotIn("This text must not be saved", parsed.first_line)

    def test_import_creates_pending_entries(self):
        importer = HymnaryImporter(client=FakeClient())
        result = importer.import_hymnal("UMH", limit=1)
        self.assertEqual(result["created"], 1)
        entry = HymnalEntry.objects.get()
        self.assertFalse(entry.is_approved)
        self.assertEqual(entry.hymnal.code, "UMH")
        self.assertEqual(entry.title_as_printed, "Amazing Grace")
