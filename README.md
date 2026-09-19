# rates

European Central Bank daily reference rates, published as a single JSON file.

<https://rates.suba.info/rates.json>

```json
{ "base": "EUR", "date": "2026-09-18", "rates": { "USD": 1.0842, "TRY": 55.907, … } }
```

The point is to read the source a few times a day in one place instead of
having every client query a free rate service on its own.

- `scripts/build_rates.py` — fetches the rates and writes `public/rates.json`.
  Primary source frankfurter.dev, falling back to the ECB's own XML feed.
  Nothing is written when the table is unchanged.
- `.github/workflows/rates.yml` — runs every six hours, commits a changed
  table and deploys it to GitHub Pages.

The ECB publishes once per business day, so at weekends Friday's rates stand.
No request to this file carries anything but the request itself.
