# Workflows

n8n exports with every credential, sheet ID and instance URL removed.

## daily-data-pull.json

Pulls orders, buyers and available inventory from the wholesale platform API into three Google Sheet tabs (Orders, Buyers, Inventory). Runs at 4:30am every day and at 9am, noon and 3pm on weekdays. Read only: it never writes back to the platform.

How it checks itself:
- Orders and buyers are upserted on a key (`line_key`, `buyer_id`), so a re-run never makes duplicates.
- Inventory is cleared and rewritten every run, so the tab always matches what's live.
- THC comes only from the lab results entered on each batch. If there's no number, the cell stays blank. It never fills in a guess.

Where it can break:
- The API key expires or loses permissions. The run fails and the sheet goes stale. Check `snapshot_date` on the Inventory tab.
- The platform changes a field name. The column comes back blank instead of erroring.

To use it: import into n8n, then set your own API credential (read-only token) and Google Sheets credential, and replace `YOUR_GOOGLE_SHEET_ID`.
