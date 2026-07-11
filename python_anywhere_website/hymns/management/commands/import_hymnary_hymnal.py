from django.core.management.base import BaseCommand

from hymns.services import HymnaryClient, HymnaryImporter


class Command(BaseCommand):
    help = "Import metadata for a selected Hymnary hymnal into a pending review batch."

    def add_arguments(self, parser):
        parser.add_argument("hymnal_code")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int)
        parser.add_argument("--delay", type=float, default=1.0)
        parser.add_argument("--start-number")

    def handle(self, *args, **options):
        importer = HymnaryImporter(client=HymnaryClient(delay=options["delay"]))
        result = importer.import_hymnal(
            options["hymnal_code"],
            dry_run=options["dry_run"],
            limit=options.get("limit"),
            start_number=options.get("start_number"),
        )
        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run found {len(result['entry_urls'])} instance URL(s)."
                )
            )
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Created batch {result['batch'].id}: {result['created']} entries, {result['issues']} issue(s)."
            )
        )
