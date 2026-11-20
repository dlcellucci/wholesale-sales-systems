"""Turn a QuickBooks "A/R Aging Summary" report into rows you can put on a call sheet.

Usage:
  pdftotext -layout report.pdf report.txt
  python3 parse_ar.py report.txt [out.json]

QuickBooks leaves a cell blank when it's $0, so a plain text dump can't tell which
column a number belongs to. This reads the -layout text and puts each number in the
column whose header it lines up under. Then it checks itself: every column has to add
up to the report's TOTAL row, and every customer's buckets have to add up to their
total. If anything is off it prints what and exits with code 1, so nothing downstream
should write the results.
"""
import json, re, sys

COLS = ['CURRENT', '1 - 30', '31 - 60', '61 - 90', '91 AND OVER', 'Total']
KEYS = ['current', 'd1_30', 'd31_60', 'd61_90', 'd91', 'total']
NUM = re.compile(r'-?[\d,]+\.\d{2}')


def parse(text):
    lines = text.splitlines()
    hi = next(i for i, l in enumerate(lines) if 'CURRENT' in l)
    hdr = lines[hi]
    ends = [hdr.index(c) + len(c) for c in COLS]
    body = [l for l in lines[hi + 1:] if l.strip() and 'GMT' not in l]
    rows, i = [], 0
    while i < len(body):
        l = body[i]
        m = NUM.search(l)
        if m and l[:m.start()].strip():          # normal row: name then numbers
            name = l[:m.start()].strip(); i += 1
        elif not m:                               # long name wrapped: name / numbers / rest of name
            name = l.strip(); l = body[i + 1]; name += ' ' + body[i + 2].strip(); i += 3
        else:                                     # numbers with no name: flag it
            name = '?'; i += 1
        vals = [0.0] * 6
        for mm in NUM.finditer(l):
            k = min(range(6), key=lambda k: abs(ends[k] - mm.end()))
            vals[k] = float(mm.group().replace(',', ''))
        rows.append({'customer': name, **dict(zip(KEYS, vals))})
    total = next(r for r in rows if r['customer'] == 'TOTAL')
    rows = [r for r in rows if r['customer'] != 'TOTAL']
    for r in rows:
        r['over_30'] = round(r['d31_60'] + r['d61_90'] + r['d91'], 2)
    return rows, total


def check(rows, total):
    problems = []
    for k in KEYS:
        s = round(sum(r[k] for r in rows), 2)
        if abs(s - total[k]) > 0.01:
            problems.append(f'column {k}: rows add to {s}, report says {total[k]}')
    for r in rows:
        if r['customer'] == '?':
            problems.append('a row of numbers had no customer name')
        if abs(sum(r[k] for k in KEYS[:5]) - r['total']) > 0.01:
            problems.append(f"{r['customer']}: buckets don't add up to its total")
    return problems


if __name__ == '__main__':
    rows, total = parse(open(sys.argv[1]).read())
    problems = check(rows, total)
    for p in problems:
        print('MISMATCH', p)
    print('CHECK', 'FAIL' if problems else 'PASS', len(rows), 'customers')
    if len(sys.argv) > 2:
        json.dump({'ok': not problems, 'rows': rows, 'total': total}, open(sys.argv[2], 'w'), indent=1)
    sys.exit(1 if problems else 0)
