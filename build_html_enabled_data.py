"""
Build html_enabled_accounts.json from Cardknox payment-site reports that include ExtraHtml.
Only rows with ExtraHtml=TRUE (edited/custom HTML payment pages) are included.
"""

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "public" / "html_enabled_accounts.json"

# Same Desktop location pattern as analyze_donation_sites.py / export_merchant_list.py
HTML_REPORTS = [
    ("Payfac", Path(r"c:\Users\AAchin\OneDrive - Sola\Desktop\PayfacPaymentsiteUsageReportwithHTML.csv")),
    ("Traditional", Path(r"c:\Users\AAchin\OneDrive - Sola\Desktop\TraditionalPaymentsiteUsageReportwithHTML.csv")),
]


def extra_html_is_enabled(value: str) -> bool:
    return (value or "").strip().upper() in ("TRUE", "YES", "1", "Y")


def load_html_rows(source_label: str, path: Path) -> list[dict]:
    rows_out: list[dict] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            raw = row.get("ExtraHtml")
            if not extra_html_is_enabled(raw):
                continue
            mid = (row.get("Cardknox MID") or "").strip()
            rows_out.append(
                {
                    "merchantId": mid,
                    "merchantName": (row.get("Business Name") or "").strip(),
                    "email": (row.get("Email") or "").strip(),
                    "url": (row.get("URL") or "").strip(),
                    "sicCode": (row.get("Sic Code") or "").strip(),
                    "sicDesc": (row.get("Sic Desc") or "").strip(),
                    "sourceFile": source_label,
                }
            )
    return rows_out


def build_html_payload() -> dict:
    """Return HTML-enabled account list (same shape as html_enabled_accounts.json)."""
    all_rows: list[dict] = []
    counts: dict[str, int] = {}
    missing: list[str] = []

    for source_label, path in HTML_REPORTS:
        if not path.is_file():
            missing.append(str(path))
            continue
        part = load_html_rows(source_label, path)
        counts[source_label] = len(part)
        all_rows.extend(part)

    all_rows.sort(
        key=lambda r: (
            r["sourceFile"],
            (r["merchantName"] or "").lower(),
            r["merchantId"],
        )
    )

    return {
        "generatedAt": datetime.now().isoformat(),
        "inputFiles": [str(p) for _, p in HTML_REPORTS],
        "missingFiles": missing,
        "totals": {
            **counts,
            "all": len(all_rows),
        },
        "rows": all_rows,
    }


def main() -> None:
    payload = build_html_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(payload['rows'])} HTML-enabled accounts)")
    if payload["missingFiles"]:
        print("Missing (skipped):", "; ".join(payload["missingFiles"]))


if __name__ == "__main__":
    main()
