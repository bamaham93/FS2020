import re
import time
from dataclasses import dataclass, field
from datetime import timedelta
from urllib.parse import urljoin

import requests
from django.db.models import Count, Max
from django.utils import timezone

from hymns.models import (
    Hymn,
    Hymnal,
    HymnalEntry,
    HymnImportBatch,
    HymnImportIssue,
    ScriptureReference,
    Topic,
    Tune,
)


HYMNARY_BASE_URL = "https://hymnary.org"
USER_AGENT = "FS2020 hymn metadata importer; contact via jacob-mcgowin.us"


def normalize_title(value):
    normalized = re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def _clean(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def _load_soup(html):
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError(
            "beautifulsoup4 is required for Hymnary imports. Install requirements first."
        ) from exc
    return BeautifulSoup(html, "html.parser")


@dataclass
class ParsedHymnal:
    code: str
    title: str = ""
    publisher: str = ""
    publication_year: int | None = None
    denomination: str = ""
    language: str = ""
    source_url: str = ""
    entry_urls: list[str] = field(default_factory=list)
    page_urls: list[str] = field(default_factory=list)


@dataclass
class ParsedEntry:
    hymnal_code: str
    number: str
    hymnal_title: str = ""
    title: str = ""
    text_title: str = ""
    first_line: str = ""
    author: str = ""
    tune_name: str = ""
    tune_meter: str = ""
    tune_key: str = ""
    tune_source: str = ""
    arranger_or_harmonizer: str = ""
    entry_meter: str = ""
    language: str = ""
    publication_date: str = ""
    copyright_status: str = ""
    source_url: str = ""
    topics: list[str] = field(default_factory=list)
    scripture_references: list[str] = field(default_factory=list)


class HymnaryClient:
    def __init__(self, delay=1.0, timeout=10):
        self.delay = float(delay)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def get(self, url):
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return response.text


class HymnaryParser:
    instance_pattern = re.compile(r"^/hymn/([^/]+)/([^/?#]+)")

    def parse_hymnal(self, html, code, source_url):
        soup = _load_soup(html)
        title = _clean(soup.find("h1").get_text(" ")) if soup.find("h1") else code
        parsed = ParsedHymnal(code=code, title=title, source_url=source_url)

        text = soup.get_text("\n")
        publisher_match = re.search(r"Publisher:\s*(.+?)(?:,?\s*(\d{4}))?$", text, re.MULTILINE)
        if publisher_match:
            parsed.publisher = _clean(publisher_match.group(1))
            if publisher_match.group(2):
                parsed.publication_year = int(publisher_match.group(2))
        denomination_match = re.search(r"Denomination:\s*(.+)$", text, re.MULTILINE)
        if denomination_match:
            parsed.denomination = _clean(denomination_match.group(1))
        language_match = re.search(r"Language:\s*(.+)$", text, re.MULTILINE)
        if language_match:
            parsed.language = _clean(language_match.group(1))

        entry_urls = set()
        page_urls = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            match = self.instance_pattern.match(href)
            if match and match.group(1).lower() == code.lower():
                entry_urls.add(urljoin(HYMNARY_BASE_URL, href))
            if href.startswith(f"/hymnal/{code}") and href != f"/hymnal/{code}":
                page_urls.add(urljoin(HYMNARY_BASE_URL, href))
        parsed.entry_urls = sorted(entry_urls)
        parsed.page_urls = sorted(page_urls)
        return parsed

    def parse_entry(self, html, source_url):
        soup = _load_soup(html)
        path_match = re.search(r"/hymn/([^/]+)/([^/?#]+)", source_url)
        if not path_match:
            raise ValueError(f"Not a Hymnary instance URL: {source_url}")
        parsed = ParsedEntry(
            hymnal_code=path_match.group(1),
            number=path_match.group(2),
            source_url=source_url,
        )

        heading = soup.find("h2")
        if heading:
            heading_text = _clean(heading.get_text(" "))
            heading_match = re.match(r"(.+?)\s+#(.+)$", heading_text)
            parsed.hymnal_title = heading_match.group(1) if heading_match else heading_text

        numbered_heading = None
        for h2 in soup.find_all("h2"):
            candidate = _clean(h2.get_text(" "))
            if candidate.startswith(f"{parsed.number}."):
                numbered_heading = candidate
                break
        if numbered_heading:
            parsed.title = _clean(numbered_heading.split(".", 1)[1])

        text = soup.get_text("\n")
        parsed.text_title = self._field(text, "Text")
        parsed.author = self._field(text, "Author") or self._field(text, "Author (st. 1-5)")
        parsed.tune_name = self._field(text, "Tune") or self._field(text, "Name")
        parsed.arranger_or_harmonizer = self._field(text, "Arranger") or self._field(text, "Harmonizer")
        parsed.first_line = self._field(text, "First Line")
        parsed.entry_meter = self._field(text, "Meter")
        parsed.language = self._field(text, "Language")
        parsed.publication_date = self._field(text, "Publication Date")
        parsed.copyright_status = self._field(text, "Copyright")
        parsed.tune_key = self._field(text, "Key")
        parsed.tune_source = self._field(text, "Source")
        parsed.tune_meter = parsed.entry_meter
        parsed.topics = self._topics(text)
        parsed.scripture_references = self._scriptures(text)

        if not parsed.title:
            parsed.title = parsed.text_title or parsed.first_line or f"Hymn {parsed.number}"
        return parsed

    def _field(self, text, label):
        pattern = rf"^{re.escape(label)}:\s*(.+)$"
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            return ""
        value = _clean(match.group(1))
        value = re.sub(r"\s+\([^)]+\)$", "", value).strip()
        return value

    def _topics(self, text):
        match = re.search(r"^Topic:\s*(.+)$", text, re.MULTILINE)
        if not match:
            return []
        topic_text = re.sub(r"\(\d+ more\.\.\.\)", "", match.group(1))
        parts = []
        for chunk in re.split(r";|,", topic_text):
            value = _clean(chunk)
            if value:
                parts.append(value)
        return parts

    def _scriptures(self, text):
        results = []
        capture = False
        for line in text.splitlines():
            clean_line = _clean(line)
            if clean_line == "Scripture:":
                capture = True
                continue
            if capture and clean_line in {"Topic:", "Tune Information", "Media"}:
                break
            if capture and re.match(r"^[1-3]?\s?[A-Za-z ]+\s+\d", clean_line):
                results.append(clean_line)
        return list(dict.fromkeys(results))


class HymnaryImporter:
    def __init__(self, client=None, parser=None):
        self.client = client or HymnaryClient()
        self.parser = parser or HymnaryParser()

    def import_hymnal(self, code, *, dry_run=False, limit=None, start_number=None):
        code = code.strip()
        source_url = f"{HYMNARY_BASE_URL}/hymnal/{code}"
        html = self.client.get(source_url)
        parsed_hymnal = self.parser.parse_hymnal(html, code, source_url)

        urls = list(parsed_hymnal.entry_urls)
        for page_url in parsed_hymnal.page_urls:
            page_html = self.client.get(page_url)
            page = self.parser.parse_hymnal(page_html, code, page_url)
            urls.extend(page.entry_urls)
        urls = list(dict.fromkeys(urls))

        if start_number:
            urls = [url for url in urls if url.rstrip("/").split("/")[-1] >= str(start_number)]
        if limit:
            urls = urls[: int(limit)]

        if dry_run:
            return {"hymnal": parsed_hymnal, "entry_urls": urls, "batch": None, "created": 0, "issues": 0}

        hymnal = self._save_hymnal(parsed_hymnal)
        batch = HymnImportBatch.objects.create(
            hymnal_code=code,
            source_url=source_url,
            notes=f"Imported {len(urls)} Hymnary instance URLs for review.",
        )

        created = 0
        for url in urls:
            try:
                entry_html = self.client.get(url)
                parsed_entry = self.parser.parse_entry(entry_html, url)
                self._save_entry(hymnal, batch, parsed_entry)
                created += 1
            except Exception as exc:
                HymnImportIssue.objects.create(batch=batch, source_url=url, message=str(exc))
        return {"hymnal": parsed_hymnal, "entry_urls": urls, "batch": batch, "created": created, "issues": batch.issues.count()}

    def _save_hymnal(self, parsed):
        hymnal, _ = Hymnal.objects.update_or_create(
            code=parsed.code,
            defaults={
                "title": parsed.title or parsed.code,
                "publisher": parsed.publisher,
                "publication_year": parsed.publication_year,
                "denomination": parsed.denomination,
                "language": parsed.language,
                "source_url": parsed.source_url,
            },
        )
        return hymnal

    def _save_entry(self, hymnal, batch, parsed):
        hymn, _ = Hymn.objects.get_or_create(
            normalized_title=normalize_title(parsed.title),
            first_line=parsed.first_line,
            author=parsed.author,
            defaults={
                "canonical_title": parsed.title,
                "meter": parsed.entry_meter,
                "language": parsed.language,
                "copyright_status": parsed.copyright_status,
                "source_url": parsed.source_url,
            },
        )
        tune = None
        if parsed.tune_name:
            tune, _ = Tune.objects.get_or_create(
                name=parsed.tune_name,
                meter=parsed.tune_meter,
                defaults={
                    "key": parsed.tune_key,
                    "source": parsed.tune_source,
                    "composer": parsed.arranger_or_harmonizer,
                },
            )
        entry, _ = HymnalEntry.objects.update_or_create(
            hymnal=hymnal,
            number=parsed.number,
            defaults={
                "title_as_printed": parsed.title,
                "first_line_as_printed": parsed.first_line,
                "tune_as_printed": parsed.tune_name,
                "meter_as_printed": parsed.entry_meter,
                "key": parsed.tune_key,
                "publication_date": parsed.publication_date,
                "source_url": parsed.source_url,
                "hymn": hymn,
                "tune": tune,
                "import_batch": batch,
                "is_approved": False,
            },
        )
        for topic_name in parsed.topics:
            topic, _ = Topic.objects.get_or_create(name=topic_name)
            entry.topics.add(topic)
            hymn.topics.add(topic)
        for reference in parsed.scripture_references:
            scripture, _ = ScriptureReference.objects.get_or_create(reference=reference)
            entry.scripture_references.add(scripture)
            hymn.scripture_references.add(scripture)
        return entry


def recommend_entries(limit=6):
    cutoff = timezone.localdate() - timedelta(days=120)
    entries = (
        HymnalEntry.objects.filter(is_approved=True)
        .annotate(usage_count=Count("usages"), last_used=Max("usages__used_on"))
        .select_related("hymnal", "tune")
        .prefetch_related("topics", "scripture_references")
    )
    scored = []
    used_tunes = set()
    for entry in entries:
        score = 100
        if entry.last_used and entry.last_used >= cutoff:
            score -= 50
        score -= min(entry.usage_count, 10) * 3
        if entry.tune_as_printed and entry.tune_as_printed in used_tunes:
            score -= 10
        scored.append((score, entry.title_as_printed.lower(), entry))
        used_tunes.add(entry.tune_as_printed)
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [entry for _, __, entry in scored[:limit]]
