"""
Export merchant name + email for:
  - 70 unique donation-classified payment links, and
  - all SIC 8398 rows (1350),

as one deduplicated list (1351 rows: 1350 SIC 8398 + 1 donation link not in 8398).

Email is joined from the same Cardknox payment-site usage reports used to build
donation_site_classification_output.csv (Cardknox MID -> Email).
"""

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SITE_DATA = ROOT / "public" / "site_data.json"
OUTPUT = ROOT / "merchant_list_donation_and_sic8398.csv"
OUTPUT_FALLBACK = ROOT / "merchant_list_donation_and_sic8398_with_email.csv"

# Same sources as card-scanner/analyze_donation_sites.py (contains Email + Cardknox MID).
EMAIL_SOURCE_FILES = [
    Path(r"c:\Users\AAchin\OneDrive - Sola\Desktop\PayfacPaymentsiteUsageReport.csv"),
    Path(r"c:\Users\AAchin\OneDrive - Sola\Desktop\TraditionalPaymentsiteUsageReport.csv"),
]


def load_email_by_merchant_id(paths: list[Path]) -> dict[str, str]:
    """Last non-empty email wins if a MID appears in multiple rows or files."""
    by_mid: dict[str, str] = {}
    loaded_any = False
    for path in paths:
        if not path.is_file():
            print(f"Warning: email source not found (skipped): {path}", file=sys.stderr)
            continue
        loaded_any = True
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                mid = (row.get("Cardknox MID") or "").strip()
                if not mid:
                    continue
                email = (row.get("Email") or "").strip()
                if email:
                    by_mid[mid] = email
    if not loaded_any:
        print(
            "Warning: no email source files loaded; email column will be empty. "
            "Place Payfac/Traditional PaymentsiteUsageReport.csv on this machine or "
            "edit EMAIL_SOURCE_FILES in export_merchant_list.py.",
            file=sys.stderr,
        )
    return by_mid


def main():
    if not SITE_DATA.exists():
        raise FileNotFoundError(f"Missing {SITE_DATA}; run build_dashboard_data.py first.")

    data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
    donation_links = data.get("donationLinks") or []
    sic_rows = (data.get("sic8398") or {}).get("rowsData") or []
    email_by_mid = load_email_by_merchant_id(EMAIL_SOURCE_FILES)

    dl_keys = set()
    for link in donation_links:
        mid = (link.get("merchantId") or "").strip()
        url = (link.get("url") or "").strip().lower()
        dl_keys.add((mid, url))

    rows_out = []

    for row in sic_rows:
        mid = (row.get("Merchant ID") or "").strip()
        url = (row.get("URL") or "").strip()
        url_l = url.lower()
        in_dl = (mid, url_l) in dl_keys
        rows_out.append(
            {
                "merchant_id": mid,
                "merchant_name": (row.get("Merchant Name") or "").strip(),
                "email": email_by_mid.get(mid, ""),
                "url": url,
                "payment_site_name": (row.get("Payment Site Name") or "").strip(),
                "donation_classification": (row.get("Donation Classification") or "").strip(),
                "confidence_level": (row.get("Confidence Level") or "").strip(),
                "source_file": (row.get("Source File") or "").strip(),
                "sic_code": (row.get("SIC Code") or "").strip(),
                "in_70_donation_links": "yes" if in_dl else "no",
                "in_sic_8398": "yes",
            }
        )

    sic_keys = {(r["merchant_id"], (r["url"] or "").lower()) for r in rows_out}

    for link in donation_links:
        mid = (link.get("merchantId") or "").strip()
        url = (link.get("url") or "").strip()
        key = (mid, url.lower())
        if key in sic_keys:
            continue
        rows_out.append(
            {
                "merchant_id": mid,
                "merchant_name": (link.get("merchantName") or "").strip(),
                "email": email_by_mid.get(mid, ""),
                "url": url,
                "payment_site_name": (link.get("paymentSiteName") or "").strip(),
                "donation_classification": "Donation",
                "confidence_level": "",
                "source_file": (link.get("sourceFile") or "").strip(),
                "sic_code": "",
                "in_70_donation_links": "yes",
                "in_sic_8398": "no",
            }
        )

    fieldnames = [
        "merchant_id",
        "merchant_name",
        "email",
        "url",
        "payment_site_name",
        "donation_classification",
        "confidence_level",
        "source_file",
        "sic_code",
        "in_70_donation_links",
        "in_sic_8398",
    ]
    out_path = OUTPUT
    try:
        fh = OUTPUT.open("w", encoding="utf-8-sig", newline="")
    except OSError:
        out_path = OUTPUT_FALLBACK
        print(
            f"Warning: could not write {OUTPUT} (file in use?). Writing {out_path} instead.",
            file=sys.stderr,
        )
        fh = out_path.open("w", encoding="utf-8-sig", newline="")
    with fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)

    with_email = sum(1 for r in rows_out if (r.get("email") or "").strip())
    print(f"Wrote {out_path} ({len(rows_out)} rows, {with_email} with email)")


if __name__ == "__main__":
    main()
