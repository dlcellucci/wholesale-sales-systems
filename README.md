# Wholesale Sales Systems

AI sales tools for founder-led producers who sell wholesale: farms, food, cannabis, makers.

I run sales for a craft cannabis brand in Maine. Every tool here started as something I needed on a real sales day. What's shared here uses sample data only. No real stores, no customer info, no API keys.

## What's in here

- **Daily inventory and order pull.** An n8n workflow that pulls orders, buyers and inventory from our wholesale platform into a Google Sheet four times a day. Read only.
- **Sales Desk.** A one-page tool for sales calls. It shows who's due to reorder, what's on hand, and builds a menu to text a buyer.
- **Retailer newsletter.** Sends to buyer emails, skips anyone who opted out, and only shows potency from a passing lab test.
- **Cultivation Desk.** A shared grow calendar for every room, with a locked cycle plan, label rates for IPM, planned vs. actual labor, and a morning Slack bot that sends each person their tasks and logs their replies. See `cultivation-desk/`.
- **A/R check.** Turns the weekly accounts receivable report into a call list of who owes money and who to hold.

## How I check the output

Every tool has a check built in: totals that have to match the source, blanks instead of guesses, and a log of what ran.

## Folder layout

- `sample-data/` has fake inventory, orders, buyers and A/R data that matches the real sheet layout.
- `workflows/` has n8n exports with every credential and sheet ID removed. Each one has notes on how it checks itself and where it breaks.
- `scripts/check.sh` scans the repo for keys, emails, phone numbers, sheet IDs and real names before every commit.
- `SAFETY.md` lists what never goes in here.

Built while working through a 24-week AI build program.
