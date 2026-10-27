import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Make the project root importable when running unittest discovery.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import helpdesk


class HelpdeskTests(unittest.TestCase):

    def setUp(self):
        # Each test gets its own temporary directory.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.test_dir = Path(self.temp_dir.name)
        self.tickets_file = self.test_dir / "tickets.json"

        self.data_patch = patch.object(
            helpdesk, "DATA_DIR", self.test_dir
        )
        self.file_patch = patch.object(
            helpdesk, "TICKETS_FILE", self.tickets_file
        )

        self.data_patch.start()
        self.file_patch.start()

        self.addCleanup(self.data_patch.stop)
        self.addCleanup(self.file_patch.stop)

        self.sample_ticket = {
            "id": "INC-0001",
            "requester": "John Doe",
            "summary": "No wifi",
            "description": "Laptop works wired but not wirelessly",
            "priority": "Medium",
            "status": "In Progress",
            "created_at": "2026-10-26T14:28:26-04:00",
            "updated_at": "2026-10-26T14:37:13-04:00",
            "troubleshooting_notes": [
                {
                    "timestamp": "2026-10-26T14:37:13-04:00",
                    "note": "Issue still occurs with wifi",
                }
            ],
            "resolution": "",
        }

    def test_ticket_ids_are_unique_and_sequential(self):
        tickets = [self.sample_ticket.copy()]

        self.assertEqual(
            helpdesk.next_ticket_id(tickets), "INC-0002"
        )

        tickets.append({"id": "INC-0002"})

        self.assertEqual(
            helpdesk.next_ticket_id(tickets), "INC-0003"
        )

    def test_create_ticket_saves_new_ticket(self):
        with patch(
            "builtins.input",
            side_effect=[
                "Jane Smith",
                "Cannot print",
                "Printer is connected but not responding",
                "High",
            ],
        ):
            helpdesk.create_ticket([])

        tickets = helpdesk.load_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["id"], "INC-0001")
        self.assertEqual(tickets[0]["requester"], "Jane Smith")
        self.assertEqual(tickets[0]["priority"], "High")
        self.assertEqual(tickets[0]["status"], "Open")
        self.assertTrue(tickets[0]["created_at"])
        self.assertTrue(self.tickets_file.exists())

    def test_save_and_load_tickets(self):
        helpdesk.save_tickets([self.sample_ticket])

        loaded = helpdesk.load_tickets()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], "INC-0001")
        self.assertEqual(loaded[0]["summary"], "No wifi")

    def test_invalid_json_raises_clear_error(self):
        self.tickets_file.write_text(
            "{invalid json",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            RuntimeError, "invalid JSON"
        ):
            helpdesk.load_tickets()

    def test_search_finds_ticket_case_insensitively(self):
        output = io.StringIO()

        with (
            patch("builtins.input", return_value="WIFI"),
            contextlib.redirect_stdout(output),
        ):
            helpdesk.search_tickets([self.sample_ticket])

        self.assertIn("INC-0001", output.getvalue())
        self.assertIn("Found 1 matching ticket", output.getvalue())

    def test_search_reports_no_matches(self):
        output = io.StringIO()

        with (
            patch("builtins.input", return_value="unicorn"),
            contextlib.redirect_stdout(output),
        ):
            helpdesk.search_tickets([self.sample_ticket])

        self.assertIn("No matching tickets found", output.getvalue())

    def test_recording_resolution_resolves_ticket(self):
        tickets = [self.sample_ticket.copy()]

        with patch(
            "builtins.input",
            side_effect=[
                "INC-0001",
                "3",
                "Reconnected laptop to the correct Wi-Fi network",
                "5",
            ],
        ):
            helpdesk.update_ticket(tickets)

        self.assertEqual(tickets[0]["status"], "Resolved")
        self.assertEqual(
            tickets[0]["resolution"],
            "Reconnected laptop to the correct Wi-Fi network",
        )

        saved = helpdesk.load_tickets()
        self.assertEqual(saved[0]["status"], "Resolved")

    def test_csv_export_includes_ticket_and_notes(self):
        helpdesk.export_csv([self.sample_ticket])

        export_file = self.test_dir / "tickets_export.csv"

        self.assertTrue(export_file.exists())

        with export_file.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "INC-0001")
        self.assertEqual(rows[0]["status"], "In Progress")
        self.assertIn(
            "Issue still occurs with wifi",
            rows[0]["troubleshooting_notes"],
        )

    def test_existing_ticket_id_is_preserved(self):
        # Regression check: loading existing ticket data keeps its ID.
        helpdesk.save_tickets([self.sample_ticket])

        loaded = helpdesk.load_tickets()

        self.assertEqual(loaded[0]["id"], "INC-0001")
        self.assertEqual(loaded[0]["requester"], "John Doe")


if __name__ == "__main__":
    unittest.main(verbosity=2)
