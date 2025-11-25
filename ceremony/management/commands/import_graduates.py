import csv
from decimal import Decimal
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ceremony.models import Graduate


class Command(BaseCommand):
    help = (
        "Import graduates from a CSV exported from your Excel bookings sheet. "
        "Existing rows are matched by Unique ID and updated."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to the CSV file (export from Excel).",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        try:
            f = open(csv_path, newline="", encoding="utf-8-sig")
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")

        created = 0
        updated = 0

        with f:
            reader = csv.DictReader(f)
            # Map CSV column names to model field names
            header_map = {
                "Submission Date": "submission_date",
                "Name": "name",
                "Email": "email",
                "Student ID": "student_id",
                "Payment Status": "payment_status",
                (
                    "For uniformity and event standards, students must hire or purchase "
                    "an approved gown. Personal gowns are strictly prohibited."
                ): "gown_option",
                "No. of additional Guests": "additional_guests",
                "Total Amount in AUD": "total_amount",
                "Unique ID": "unique_id",
                "Gown Size": "gown_size",
                "Submission ID": "submission_id",
            }

            missing_cols = [c for c in header_map.keys() if c not in reader.fieldnames]
            if missing_cols:
                self.stdout.write(self.style.WARNING(
                    "Warning: these expected columns were not found in the CSV:\n"
                    f"  {missing_cols}\n"
                    "Check your header row names match the ones used in the import script."
                ))

            for row_num, row in enumerate(reader, start=2):  # header is row 1
                data = {}

                for csv_col, field_name in header_map.items():
                    if csv_col not in row:
                        continue

                    raw_value = (row[csv_col] or "").strip()

                    if field_name == "submission_date":
                        data[field_name] = self.parse_date(raw_value)
                    elif field_name == "additional_guests":
                        data[field_name] = self.parse_int(raw_value, default=0)
                    elif field_name == "total_amount":
                        data[field_name] = self.parse_decimal(raw_value, default=Decimal("0"))
                    else:
                        data[field_name] = raw_value

                unique_id = data.get("unique_id")
                if not unique_id:
                    self.stdout.write(self.style.WARNING(
                        f"Row {row_num}: missing Unique ID – skipping."
                    ))
                    continue

                grad, created_flag = Graduate.objects.update_or_create(
                    unique_id=unique_id,
                    defaults=data,
                )

                if created_flag:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import completed. Created: {created}, Updated: {updated}"
        ))

    # ---------- helper parsers ---------- #

    def parse_date(self, s):
        if not s:
            return None

        formats = [
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return timezone.make_aware(dt, timezone.get_current_timezone())
            except ValueError:
                continue

        self.stdout.write(self.style.WARNING(f"Could not parse date '{s}', storing as NULL"))
        return None

    def parse_int(self, s, default=0):
        if not s:
            return default
        try:
            return int(s)
        except ValueError:
            self.stdout.write(self.style.WARNING(f"Could not parse integer '{s}', using {default}"))
            return default

    def parse_decimal(self, s, default=Decimal("0")):
        if not s:
            return default
        cleaned = s.replace("$", "").replace(",", "").strip()
        try:
            return Decimal(cleaned)
        except Exception:
            self.stdout.write(self.style.WARNING(f"Could not parse decimal '{s}', using {default}"))
            return default
