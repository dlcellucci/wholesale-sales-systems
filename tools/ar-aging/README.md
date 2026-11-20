# A/R aging to call list

Takes the weekly QuickBooks "A/R Aging Summary" PDF and turns it into a list of who owes what, so the sales team knows who to call for money and whose orders to hold.

## Run it

```
pdftotext -layout report.pdf report.txt
python3 parse_ar.py report.txt out.json
```

Try it on the sample (made-up stores):

```
python3 parse_ar.py sample_ar.txt      # CHECK PASS 6 customers
python3 parse_ar.py sample_ar_broken.txt   # CHECK FAIL, exits 1
```

## How it checks itself

- Every column (current, 1-30, 31-60, 61-90, 91+, total) has to add up to the report's TOTAL row.
- Every customer's buckets have to add up to that customer's total.
- If anything is off, it says what and exits with code 1. Whatever runs it should not write anything when that happens.

## Where it breaks

- QuickBooks leaves $0 cells blank, so the parser places each number by which column header it lines up under. If you don't use `pdftotext -layout`, the spacing is gone and numbers land in the wrong column. The total check catches that.
- If QuickBooks changes the column names, it won't find the header and stops.
- A very long customer name wraps to two lines. The parser handles the usual wrap (name, numbers, rest of name). A different wrap shows up as a `?` row and fails the check.

## How I use it

Every Sunday after the report comes in, a scheduled job runs this, rewrites the A/R tab on our call sheet (sorted by what's more than 30 days late, marked "CALL" or "Nudge"), and messages me the list. It stops if the check fails.
