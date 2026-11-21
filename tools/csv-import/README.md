# CSV import: any producer's orders into the standard sheet

Not every producer uses the same wholesale platform. Some use QuickBooks, Shopify, Faire, a farm platform or just a spreadsheet. Every one of them can export their orders as a CSV.

This tool takes that export and turns it into our standard Orders and Buyers sheets. Every other tool (reorder list, sales desk, A/R call list) reads the standard sheets, so this is the only part that changes for each new client.

## Run it

```
python3 import_orders.py export.csv mapping.json --expect-total 931.50 --aliases aliases.csv --out out
```

- `mapping.json` says which of their columns is which of ours (see `mapping_example.json`).
- `--expect-total` is the sales total for the same dates from **their own system's** sales report.
- `aliases.csv` fixes stores that show up under more than one name.

Try it on the samples (made-up producer and stores):

```
python3 import_orders.py sample_export.csv mapping_example.json --expect-total 931.50 --aliases aliases_example.csv --out out
python3 import_orders.py sample_export_broken.csv mapping_example.json --expect-total 931.50 --aliases aliases_example.csv --out out
```

The first passes. The second fails on the two lines that were broken on purpose and writes nothing.

## How it checks itself

- Our total has to match the total from their own sales report. If it doesn't, nothing gets written.
- Every line's quantity times price has to equal the line total.
- Any line missing an order number, date, customer, item, quantity or amount is called out by line number.
- Dates have to match the format in the mapping, so 11/02 never turns into February 11.
- Stores with similar names get flagged ("Sample Store North" and "Sample Str. North") so a person decides if they're the same. It never merges them on its own.

## Where it breaks

- Store names. Every producer types them differently. Fixing the aliases file is the slowest part of a new setup.
- If their export changes column names, the mapping has to be updated or required fields come up missing.
- Discounts or shipping charged as their own line can make the totals check fail. That's the check doing its job: decide if those lines count as sales, then match it to how their report counts them.
