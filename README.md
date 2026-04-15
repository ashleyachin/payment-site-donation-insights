# Payment Site Donation Insights (Standalone)

This is a standalone mini-project separate from the Card Scanner app.

## What it does

- Builds donation analysis data from `../donation_site_classification_output.csv`
- Creates:
  - `site_data.json`
  - `donation_sites_all.csv`
  - `donation_sites_unique_merchants.csv`
- Serves a standalone dashboard (`index.html`) with:
  - All donation payment-site links
  - SIC `8398` explorer with filters and direct links

## Run

From this folder:

1. Build data:

```bash
python build_dashboard_data.py
```

2. Start a static server:

```bash
python -m http.server 8080
```

3. Open:

`http://localhost:8080`

## Notes

- Re-run `python build_dashboard_data.py` whenever classification CSV changes.
- This project does not depend on Svelte, Vite, or Card Scanner routes.
