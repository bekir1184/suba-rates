#!/usr/bin/env python3
"""Reads European Central Bank reference rates and writes the published file.

Clients read one small file (~1 KB, behind a CDN) instead of each copy
querying a free rate service on its own.

Primary source frankfurter.dev, which serves the ECB data as JSON; if that is
unreachable the ECB's own XML feed is read instead. If neither answers the
existing file is left alone — an old but correct rate beats no rate at all.
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

OUTPUT = pathlib.Path(__file__).resolve().parent.parent / "public" / "rates.json"
FRANKFURTER = "https://api.frankfurter.dev/v1/latest?base=EUR"
ECB_XML = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "rates-builder/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def from_frankfurter() -> dict | None:
    try:
        payload = json.loads(fetch(FRANKFURTER))
        return {"base": payload["base"], "date": payload["date"], "rates": payload["rates"]}
    except Exception as error:  # noqa: BLE001 — kaynak ne kırarsa kırsın yedeğe geç
        print(f"frankfurter okunamadı: {error}", file=sys.stderr)
        return None


def from_ecb() -> dict | None:
    try:
        tree = ET.fromstring(fetch(ECB_XML))
        namespace = {"ecb": "http://www.ecb.int/vocabulary/2002-08-01"}
        day = tree.find(".//ecb:Cube[@time]", namespace)
        if day is None:
            return None
        rates = {
            cube.attrib["currency"]: float(cube.attrib["rate"])
            for cube in day.findall("ecb:Cube", namespace)
        }
        return {"base": "EUR", "date": day.attrib["time"], "rates": rates}
    except Exception as error:  # noqa: BLE001
        print(f"ECB okunamadı: {error}", file=sys.stderr)
        return None


def main() -> int:
    table = from_frankfurter() or from_ecb()
    if table is None:
        print("Hiçbir kaynak okunamadı; var olan dosya korunuyor.", file=sys.stderr)
        return 1 if not OUTPUT.exists() else 0

    table["source"] = "European Central Bank"
    table["fetchedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if OUTPUT.exists():
        current = json.loads(OUTPUT.read_text())
        # Aynı günün kuru tekrar yazılmasın: gereksiz commit üretmeyelim.
        if current.get("date") == table["date"] and current.get("rates") == table["rates"]:
            print(f"Değişiklik yok ({table['date']}).")
            return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(table, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Yazıldı: {table['date']}, {len(table['rates'])} para birimi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
