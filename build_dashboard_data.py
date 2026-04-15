import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_CSV_CANDIDATES = [
    ROOT / "donation_site_classification_output.csv",
    ROOT.parent / "card-scanner" / "donation_site_classification_output.csv",
    ROOT.parent / "donation_site_classification_output.csv",
]
OUTPUT_JSON = ROOT / "public" / "site_data.json"
DONATION_ALL = ROOT / "donation_sites_all.csv"
DONATION_UNIQUE = ROOT / "donation_sites_unique_merchants.csv"


def normalize_sic_code(value: str) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def load_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, headers):
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def resolve_input_csv() -> Path:
    for path in INPUT_CSV_CANDIDATES:
        if path.is_file():
            return path
    tried = ", ".join(str(p) for p in INPUT_CSV_CANDIDATES)
    raise FileNotFoundError(f"donation_site_classification_output.csv not found. Tried: {tried}")


def main():
    input_csv = resolve_input_csv()
    rows = load_rows(input_csv)
    if not rows:
        raise ValueError("No rows found in classification output.")

    headers = list(rows[0].keys())

    donation_rows = [r for r in rows if r.get("Donation Classification") == "Donation"]
    unique_merchants = []
    seen_merchants = set()
    for row in donation_rows:
        key = ((row.get("Merchant ID") or "").strip(), (row.get("Merchant Name") or "").strip())
        if key not in seen_merchants:
            seen_merchants.add(key)
            unique_merchants.append(row)

    write_csv(DONATION_ALL, donation_rows, headers)
    write_csv(DONATION_UNIQUE, unique_merchants, headers)

    sic_8398 = [r for r in rows if normalize_sic_code(r.get("SIC Code", "")) == "8398"]
    sic_classification = Counter(r.get("Donation Classification", "Unknown") for r in sic_8398)
    sic_confidence = Counter(r.get("Confidence Level", "Unknown") for r in sic_8398)
    sic_sources = Counter(r.get("Source File", "Unknown") for r in sic_8398)

    donation_links = []
    seen_urls = set()
    for row in donation_rows:
        url = (row.get("URL") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        donation_links.append(
            {
                "merchantId": row.get("Merchant ID", ""),
                "merchantName": row.get("Merchant Name", ""),
                "paymentSiteName": row.get("Payment Site Name", ""),
                "url": url,
                "score": int(row.get("Score") or 0),
                "reason": row.get("Matched Indicators / Reason", ""),
                "sourceFile": row.get("Source File", ""),
            }
        )

    donation_links.sort(key=lambda r: r["score"], reverse=True)

    data = {
        "generatedAt": __import__("datetime").datetime.now().isoformat(),
        "inputFile": str(input_csv),
        "totals": {
            "allRows": len(rows),
            "donationRows": len(donation_rows),
            "donationUniqueMerchants": len(unique_merchants),
            "donationUniqueLinks": len(donation_links),
        },
        "sic8398": {
            "rows": len(sic_8398),
            "classificationCounts": dict(sic_classification),
            "confidenceCounts": dict(sic_confidence),
            "sourceCounts": dict(sic_sources),
            "rowsData": sic_8398,
        },
        "donationLinks": donation_links,
    }

    try:
        from build_html_enabled_data import build_html_payload

        data["htmlEnabledAccounts"] = build_html_payload()
        ha = data["htmlEnabledAccounts"]
        print(
            f"HTML-enabled accounts (embedded in site_data.json): {ha['totals'].get('all', 0)}"
        )
    except Exception as exc:
        data["htmlEnabledAccounts"] = {
            "generatedAt": None,
            "inputFiles": [],
            "missingFiles": [],
            "totals": {"all": 0},
            "rows": [],
            "loadError": str(exc),
        }
        print(f"Warning: could not embed HTML report data: {exc}")

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=True, indent=2)

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {DONATION_ALL}")
    print(f"Wrote {DONATION_UNIQUE}")
    print(f"Donation rows: {len(donation_rows)}")
    print(f"Unique donation merchants: {len(unique_merchants)}")
    print(f"Unique donation links: {len(donation_links)}")


if __name__ == "__main__":
    main()
