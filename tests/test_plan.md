# IT Help Desk Ticketing System — Test Plan

## 1. Ticket Creation
- Confirm a new ticket receives a unique ID.
- Confirm required fields cannot be left empty.
- Confirm new tickets start with Open status.
- Confirm the creation and update timestamps are recorded.

## 2. Ticket Storage
- Confirm tickets are saved to tickets.json.
- Confirm saved tickets can be loaded again.
- Confirm invalid JSON produces a clear error.

## 3. Ticket Management
- Confirm ticket status can be changed.
- Confirm troubleshooting notes are timestamped and saved.
- Confirm recording a resolution changes status to Resolved.
- Confirm nonexistent ticket IDs are handled gracefully.

## 4. Search
- Confirm searches find tickets by ID, requester, issue, priority, and status.
- Confirm searches are case-insensitive.
- Confirm searches with no matches return a useful message.

## 5. CSV Export
- Confirm exported CSV includes the correct headers.
- Confirm ticket records appear in the export.
- Confirm troubleshooting notes and resolutions are included.

## 6. Regression Testing
- Confirm the existing INC-0001 ticket is preserved.
- Confirm the next ticket receives a new, non-duplicate ID.
