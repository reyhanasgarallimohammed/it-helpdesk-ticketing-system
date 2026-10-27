# IT Help Desk Ticketing System

A lightweight, Python-based IT support ticketing system built to simulate common Level 1 help desk workflows.

## Features

- Create and assign unique incident IDs
- Record requesters, issue descriptions, priorities, and timestamps
- Track ticket statuses from Open through Resolved and Closed
- Add timestamped troubleshooting notes
- Record resolutions and update ticket statuses
- Search tickets by ID, requester, issue, priority, status, and notes
- Export ticket records to CSV for reporting
- Store ticket records in JSON between sessions
- Run automated tests with Python's built-in `unittest` framework

## Technologies

- Python 3
- JSON data persistence
- CSV reporting
- `unittest` automated testing
- Git and GitHub

## Getting Started

### Requirements

Python 3.10 or newer is recommended. No third-party Python packages are required.

### Run the application

From the project directory:

```bash
python3 src/helpdesk.py
```

### Run automated tests

```bash
python3 -m unittest discover -s tests -v
```

### Data files

- `data/tickets.json` — persistent ticket records
- `data/tickets_export.csv` — generated CSV report
- `tests/test_plan.md` — manual testing checklist
- `tests/test_helpdesk.py` — automated regression tests

## Project Purpose

This project demonstrates practical IT support concepts, including incident tracking, prioritization, status management, troubleshooting documentation, data persistence, and basic reporting.

It was developed as a hands-on portfolio project to reinforce IT support and service desk skills.
