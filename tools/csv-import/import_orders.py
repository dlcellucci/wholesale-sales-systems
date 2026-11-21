"""Turn any producer's order export (CSV) into our standard Orders and Buyers sheets.

Every tool downstream (reorder list, sales desk, A/R call list) reads the standard
sheets, so this is the only part that changes from client to client.

Usage:
  python3 import_orders.py export.csv mapping.json --expect-total 931.50 [--aliases aliases.csv] [--out out_folder]

--expect-total is the sales total for the same date range from the producer's own
system (their sales report). If our total doesn't match it, nothing gets written.
"""
import argparse, csv, difflib, json, os, re, sys
from datetime import datetime

ORDER_COLS = ['line_key', 'order_id', 'order_date', 'buyer_id', 'buyer_name', 'product_name',
              'quantity', 'unit_price', 'line_total', 'payment_status']
REQUIRED = ['order_id', 'order_date', 'buyer_name', 'product_name', 'quantity', 'line_total']


def money(v):
    s = str(v or '').strip().replace('$', '').replace(',', '')
    if s.startswith('(') and s.endswith(')'):
        s = '-' + s[1:-1]
    return float(s) if s else None


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def load_aliases(path):
    if not path:
        return {}
    with open(path, newline='') as f:
        return {r['seen_as'].strip().lower(): r['use_name'].strip() for r in csv.DictReader(f)}


def convert(export_path, mapping, aliases):
    rows, problems = [], []
    with open(export_path, newline='') as f:
        for n, raw in enumerate(csv.DictReader(f), start=2):
            get = lambda k: (raw.get(mapping[k]) or '').strip() if k in mapping else ''
            missing = [k for k in REQUIRED if not get(k)]
            if missing:
                problems.append(f'line {n}: missing {", ".join(missing)}')
                continue
            try:
                date = datetime.strptime(get('order_date'), mapping.get('date_format', '%Y-%m-%d')).date().isoformat()
            except ValueError:
                problems.append(f'line {n}: date "{get("order_date")}" doesn\'t match {mapping.get("date_format")}')
                continue
            qty, price, total = money(get('quantity')), money(get('unit_price')), money(get('line_total'))
            if price is not None and abs(qty * price - total) > 0.01:
                problems.append(f'line {n}: {qty} x {price} = {round(qty * price, 2)}, but the line says {total}')
            name = get('buyer_name')
            name = aliases.get(name.lower(), name)
            rows.append({'order_id': get('order_id'), 'order_date': date, 'buyer_name': name,
                         'buyer_id': slug(name), 'product_name': get('product_name'), 'quantity': qty,
                         'unit_price': price if price is not None else '', 'line_total': total,
                         'payment_status': get('payment_status')})
    seen = {}
    for r in rows:  # line_key: order id + line number within that order, so re-imports don't duplicate
        seen[r['order_id']] = seen.get(r['order_id'], 0) + 1
        r['line_key'] = f"{r['order_id']}-{seen[r['order_id']]}"
    return rows, problems


def lookalike_buyers(rows):
    names = sorted({r['buyer_name'] for r in rows})
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.85:
                pairs.append((a, b))
    return pairs


def buyers_from(rows):
    by = {}
    for r in rows:
        b = by.setdefault(r['buyer_id'], {'buyer_id': r['buyer_id'], 'name': r['buyer_name'], 'orders': set(),
                                           'first_order': r['order_date'], 'last_order': r['order_date'], 'total_spent': 0.0})
        b['orders'].add(r['order_id'])
        b['first_order'] = min(b['first_order'], r['order_date'])
        b['last_order'] = max(b['last_order'], r['order_date'])
        b['total_spent'] = round(b['total_spent'] + r['line_total'], 2)
    out = []
    for b in by.values():
        b['total_orders'] = len(b.pop('orders'))
        out.append(b)
    return sorted(out, key=lambda b: b['name'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export'); ap.add_argument('mapping')
    ap.add_argument('--expect-total', type=float, required=True)
    ap.add_argument('--aliases'); ap.add_argument('--out', default='out')
    a = ap.parse_args()
    mapping = json.load(open(a.mapping))
    rows, problems = convert(a.export, mapping, load_aliases(a.aliases))
    got = round(sum(r['line_total'] for r in rows), 2)
    if abs(got - a.expect_total) > 0.01:
        problems.append(f'total is {got}, but their sales report says {a.expect_total}')
    for p in problems:
        print('PROBLEM', p)
    for x, y in lookalike_buyers(rows):
        print(f'CHECK NAMES: "{x}" and "{y}" look like the same store. If so, add a line to the aliases file.')
    if problems:
        print('CHECK FAIL: nothing written')
        sys.exit(1)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'orders.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=ORDER_COLS); w.writeheader(); w.writerows(rows)
    buyers = buyers_from(rows)
    with open(os.path.join(a.out, 'buyers.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(buyers[0].keys())); w.writeheader(); w.writerows(buyers)
    print(f'CHECK PASS: {len(rows)} lines, {len(buyers)} buyers, total {got} matches their report')


if __name__ == '__main__':
    main()
