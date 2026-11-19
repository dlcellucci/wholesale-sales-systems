# Rules for this repo

This repo is public. It shares tools built for a real wholesale brand using sample data only.

- Never commit API keys, tokens, passwords, credential IDs, Google Sheet IDs or n8n instance URLs.
- Never commit real store names, buyer names, emails, phone numbers, order amounts or strain names. Use "Sample Store …" and "Sample Strain …".
- Run `bash scripts/check.sh` before every commit. Don't commit if it fails.
- Workflow exports: replace every credential `id` with `SET_YOUR_OWN` and every sheet ID with `YOUR_GOOGLE_SHEET_ID`.
- Every tool gets a short note on how it checks its own output and where it can break.
- The owner is newer to code. Keep explanations plain and steps short.
