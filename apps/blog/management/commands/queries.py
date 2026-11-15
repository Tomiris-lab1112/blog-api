from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from apps.blog import queries

SAMPLE_ARGS = {
    4: ("example-slug",),
    7: (1,),
    8: ("django",),
    9: ("gmail.com",),
    11: (["python", "django"],),
    12: (2026, 11),
    13: (30,),
    14: (None, None),
    15: ("example@gmail.com",),
    16: ("python",),
    17: ("backend",),
    21: ("python", "django"),
    22: ("django",),
    34: (2,),
    37: ("john",),
    40: ("New Tag",),
    41: (30,),
    42: ("backend", "python"),
    43: ("backend", "databases"),
}


class Command(BaseCommand):
    help = "Run Django ORM queries"

    def add_arguments(self, parser):
        parser.add_argument("--number", type=int)
        parser.add_argument("--sql", action="store_true")

    def handle(self, *args, **options):
        number = options["number"]
        show_sql = options["sql"]

        if number is not None:
            if number not in queries.QUERIES:
                raise CommandError("Query number must be from 1 to 50")
            numbers = [number]
        else:
            numbers = [
                n for n in queries.QUERIES
                if n not in range(40, 45)
            ]

        for n in numbers:
            func = queries.QUERIES[n]
            args_for_query = SAMPLE_ARGS.get(n, ())

            if n == 14:
                args_for_query = (
                    date(2026, 1, 1),
                    date(2026, 12, 31),
                )

            self.stdout.write(f"\nQuery {n}: {func.__name__}")

            with CaptureQueriesContext(connection) as captured:
                result = func(*args_for_query)

                if isinstance(result, QuerySet):
                    rows = list(result)
                    total = len(rows)
                    preview = rows[:5]

                elif isinstance(result, list):
                    total = len(result)
                    preview = result[:5]

                elif isinstance(result, tuple):
                    total = 1
                    preview = [result]

                elif isinstance(result, dict):
                    total = len(result)
                    preview = list(result.items())[:5]

                else:
                    total = 1
                    preview = [result]

            self.stdout.write(f"SQL queries: {len(captured)}")
            self.stdout.write(f"Total: {total}")

            for item in preview:
                if hasattr(item, "post_count"):
                    label = getattr(
                        item, "name", None
                    ) or getattr(item, "email", str(item))

                    self.stdout.write(
                        f"{label}: {item.post_count} posts"
                    )

                elif hasattr(item, "published_count"):
                    label = getattr(
                        item, "name", None
                    ) or getattr(item, "email", str(item))

                    self.stdout.write(
                        f"{label}: {item.published_count} published posts"
                    )

                else:
                    self.stdout.write(str(item))

            if show_sql:
                for query in captured:
                    self.stdout.write(query["sql"])
