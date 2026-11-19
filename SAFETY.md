# What never goes in this repo

- API keys, tokens or passwords
- Real store names, buyer names, emails or phone numbers
- Real order amounts or payment info
- Google Sheet IDs, n8n credential IDs or instance URLs
- Anything copied straight from a live sheet

Before every commit, run:

```
bash scripts/check.sh
```

It fails if it finds anything that looks like a key, an email, a phone number, a sheet ID, or any word in your local `.blocklist` file. The `.blocklist` file holds the real names to watch for (your brand, your stores, your strains). It's in `.gitignore`, so it never gets committed itself.

Sample data uses made-up names on purpose.
