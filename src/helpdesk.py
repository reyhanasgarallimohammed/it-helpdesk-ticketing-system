
import csv
import json
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
TICKETS_FILE = DATA_DIR / "tickets.json"

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Open", "In Progress", "Pending", "Resolved", "Closed"]


def timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_tickets():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not TICKETS_FILE.exists():
        return []

    try:
        with TICKETS_FILE.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Ticket data is invalid JSON: {TICKETS_FILE}"
        ) from error

    if not isinstance(tickets, list):
        raise RuntimeError("Ticket data must be a JSON list.")

    return tickets


def save_tickets(tickets):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with TICKETS_FILE.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4, ensure_ascii=False)


def next_ticket_id(tickets):
    highest = 0

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if ticket_id.startswith("INC-"):
            try:
                number = int(ticket_id[4:])
                highest = max(highest, number)
            except ValueError:
                continue

    return f"INC-{highest + 1:04d}"


def choose_option(prompt, options):
    while True:
        print("\n" + " | ".join(options))
        choice = input(prompt).strip().lower()

        for option in options:
            if choice == option.lower():
                return option

        print("Invalid choice. Please try again.")


def create_ticket(tickets):
    print("\n=== Create Ticket ===")

    requester = input("Requester name: ").strip()
    summary = input("Issue summary: ").strip()
    description = input("Issue details: ").strip()

    if not requester or not summary or not description:
        print("Requester, summary, and details cannot be empty.")
        return

    priority = choose_option("Priority: ", PRIORITIES)
    now = timestamp()

    ticket = {
        "id": next_ticket_id(tickets),
        "requester": requester,
        "summary": summary,
        "description": description,
        "priority": priority,
        "status": "Open",
        "created_at": now,
        "updated_at": now,
        "troubleshooting_notes": [],
        "resolution": "",
    }

    tickets.append(ticket)
    save_tickets(tickets)

    print(f"\nTicket created successfully: {ticket['id']}")


def find_ticket(tickets):
    ticket_id = input("Enter ticket ID (e.g. INC-0001): ").strip().upper()

    for ticket in tickets:
        if ticket.get("id", "").upper() == ticket_id:
            return ticket

    print(f"No ticket found with ID {ticket_id}.")
    return None


def list_tickets(tickets):
    print("\n=== All Tickets ===")

    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        print(
            f"{ticket.get('id', 'N/A')} | "
            f"{ticket.get('priority', 'N/A')} | "
            f"{ticket.get('status', 'N/A')} | "
            f"{ticket.get('requester', 'N/A')} | "
            f"{ticket.get('summary', 'N/A')}"
        )

    print(f"\nTotal tickets: {len(tickets)}")


def view_ticket(ticket):
    print("\n=== Ticket Details ===")
    print(f"ID: {ticket.get('id', 'N/A')}")
    print(f"Requester: {ticket.get('requester', 'N/A')}")
    print(f"Summary: {ticket.get('summary', 'N/A')}")
    print(f"Details: {ticket.get('description', 'N/A')}")
    print(f"Priority: {ticket.get('priority', 'N/A')}")
    print(f"Status: {ticket.get('status', 'N/A')}")
    print(f"Created: {ticket.get('created_at', 'N/A')}")
    print(f"Updated: {ticket.get('updated_at', 'N/A')}")

    print("\nTroubleshooting Notes:")
    notes = ticket.get("troubleshooting_notes", [])

    if not notes:
        print("No troubleshooting notes recorded.")
    else:
        for note in notes:
            print(f"- [{note.get('timestamp', 'N/A')}] {note.get('note', '')}")

    print(f"\nResolution: {ticket.get('resolution') or 'Not resolved'}")


def update_ticket(tickets):
    print("\n=== Manage Ticket ===")
    ticket = find_ticket(tickets)

    if ticket is None:
        return

    while True:
        print(f"\nManaging {ticket['id']} — {ticket['summary']}")
        print("1. Change status")
        print("2. Add troubleshooting note")
        print("3. Record resolution")
        print("4. View full ticket")
        print("5. Return to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            status = choose_option("New status: ", STATUSES)
            ticket["status"] = status
            ticket["updated_at"] = timestamp()
            save_tickets(tickets)
            print(f"Status updated to {status}.")

        elif choice == "2":
            note_text = input("Enter troubleshooting note: ").strip()

            if not note_text:
                print("Note cannot be empty.")
                continue

            note = {
                "timestamp": timestamp(),
                "note": note_text,
            }

            ticket.setdefault("troubleshooting_notes", []).append(note)
            ticket["updated_at"] = timestamp()
            save_tickets(tickets)
            print("Troubleshooting note saved.")

        elif choice == "3":
            resolution = input("Describe the resolution: ").strip()

            if not resolution:
                print("Resolution cannot be empty.")
                continue

            ticket["resolution"] = resolution
            ticket["status"] = "Resolved"
            ticket["updated_at"] = timestamp()
            save_tickets(tickets)
            print("Resolution saved. Ticket status set to Resolved.")

        elif choice == "4":
            view_ticket(ticket)

        elif choice == "5":
            break

        else:
            print("Please choose 1–5.")


def search_tickets(tickets):
    query = input(
        "Search by ID, requester, issue, priority, status, or notes: "
    ).strip().lower()

    if not query:
        print("Search cannot be empty.")
        return

    matches = []

    for ticket in tickets:
        notes = " ".join(
            note.get("note", "")
            for note in ticket.get("troubleshooting_notes", [])
        )

        searchable = " ".join([
            ticket.get("id", ""),
            ticket.get("requester", ""),
            ticket.get("summary", ""),
            ticket.get("description", ""),
            ticket.get("priority", ""),
            ticket.get("status", ""),
            notes,
            ticket.get("resolution", ""),
        ]).lower()

        if query in searchable:
            matches.append(ticket)

    if not matches:
        print("No matching tickets found.")
        return

    print(f"\nFound {len(matches)} matching ticket(s):")

    for ticket in matches:
        print(
            f"{ticket['id']} | {ticket['priority']} | "
            f"{ticket['status']} | {ticket['summary']}"
        )


def export_csv(tickets):
    output_file = DATA_DIR / "tickets_export.csv"

    fields = [
        "id",
        "created_at",
        "updated_at",
        "requester",
        "summary",
        "description",
        "priority",
        "status",
        "troubleshooting_notes",
        "resolution",
    ]

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for ticket in tickets:
            row = ticket.copy()
            row["troubleshooting_notes"] = " | ".join(
                f"{note.get('timestamp', '')}: {note.get('note', '')}"
                for note in ticket.get("troubleshooting_notes", [])
            )
            writer.writerow(row)

    print(f"\nExported {len(tickets)} ticket(s).")
    print(f"CSV file: {output_file}")


def main():
    tickets = load_tickets()

    while True:
        print("\n=== IT Help Desk Ticketing System ===")
        print("1. Create ticket")
        print("2. List tickets")
        print("3. Manage ticket")
        print("4. Search tickets")
        print("5. Export tickets to CSV")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_ticket(tickets)
        elif choice == "2":
            list_tickets(tickets)
        elif choice == "3":
            update_ticket(tickets)
        elif choice == "4":
            search_tickets(tickets)
        elif choice == "5":
            export_csv(tickets)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Please choose 1–6.")


if __name__ == "__main__":
    main()

