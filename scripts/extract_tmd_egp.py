#!/usr/bin/env python3
"""Extract radar winner notices from TMD's public e-GP mirror.

The TMD site republishes e-GP winner notices in a static HTML index.  This
script keeps the raw source URL and does not infer missing bidder information.
It writes JSON to stdout so the caller can review or redirect the result.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:  # pragma: no cover - environment-specific fallback
    certifi = None


WINNER_INDEX_URL = (
    "https://www.tmd.go.th/Procurement/ProcurementAnnoucementPage"
    "?ProcurementTypeCode=W0"
)
TENDER_INDEX_URL = (
    "https://www.tmd.go.th/Procurement/ProcurementAnnoucementPage"
    "?ProcurementTypeCode=B0"
)


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[dict[str, object]]] = []
        self.row: list[dict[str, object]] | None = None
        self.cell: dict[str, object] | None = None
        self.link: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = {"text": "", "href": None}
            self.row.append(self.cell)
        elif tag == "a" and self.cell is not None:
            self.link = attrs_dict.get("href")

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell["text"] = str(self.cell["text"]) + data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            if self.cell is not None:
                self.cell["href"] = self.link
            self.link = None
        elif tag in {"td", "th"}:
            self.cell = None
        elif tag == "tr":
            if self.row:
                self.rows.append(self.row)
            self.row = None


def fetch(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (research; radar-ledger/1.0)"},
    )
    context = (
        ssl.create_default_context(cafile=certifi.where())
        if certifi is not None
        else ssl.create_default_context()
    )
    try:
        with urlopen(request, timeout=30, context=context) as response:
            return response.read().decode("utf-8", errors="replace")
    except OSError:
        # Some macOS environments have working curl trust/DNS configuration
        # while Python's resolver does not. Keep the fallback explicit and
        # still send a bounded request with a research user agent.
        result = subprocess.run(
            ["curl", "-fsSL", "--max-time", "30", "-A", request.headers["User-agent"], url],
            check=True,
            capture_output=True,
        )
        return result.stdout.decode("utf-8", errors="replace")


def normalise(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def extract(html: str, source_url: str) -> list[dict[str, str]]:
    parser = TableParser()
    parser.feed(html)
    records: list[dict[str, str]] = []
    type_code = parse_qs(urlparse(source_url).query).get(
        "ProcurementTypeCode", [""]
    )[0]

    for row in parser.rows:
        cells = [normalise(cell.get("text")) for cell in row]
        title = next((text for text in cells if "เรดาร์ตรวจอากาศ" in text), "")
        if not title or "S Band" not in title or "Dual Polarization" not in title:
            continue

        project_id = next((text for text in cells if re.fullmatch(r"\d{11}", text)), "")
        notice_url = next(
            (str(cell.get("href") or "") for cell in row if cell.get("href")),
            "",
        )
        date = next(
            (text for text in cells if re.fullmatch(r"\d{2}/\d{2}/\d{4}", text)),
            "",
        )
        records.append(
            {
                "project_id": project_id,
                "title": title,
                "announcement_date_be": date,
                "procurement_method": "e-bidding" if "e-bidding" in title else "",
                "notice_url": notice_url,
                "source_index_url": source_url,
                "announcement_type_code": type_code,
                "bidder_count": "unknown",
                "bidder_count_note": (
                    "Winner notice/index does not disclose the complete bid-opening list."
                ),
            }
        )

    unique_records: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        key = (
            record["project_id"],
            record["announcement_date_be"],
            record["title"],
        )
        if key in seen:
            continue
        seen.add(key)
        unique_records.append(record)
    return unique_records


def extract_related(html: str, source_url: str) -> list[dict[str, str]]:
    """Extract every index row whose title mentions radar.

    This deliberately returns leads rather than award facts: the public index
    title/date is useful for inventorying radar-related work, while amounts,
    bidders, and contract details belong to the linked notice or contract
    summary.
    """
    parser = TableParser()
    parser.feed(html)
    records: list[dict[str, str]] = []
    type_code = parse_qs(urlparse(source_url).query).get(
        "ProcurementTypeCode", [""]
    )[0]

    for row in parser.rows:
        cells = [normalise(cell.get("text")) for cell in row]
        title = next(
            (text for text in cells if "เรดาร์" in text or "radar" in text.lower()),
            "",
        )
        if not title:
            continue
        project_id = next(
            (text for text in cells if re.fullmatch(r"(?:\d{10,12}|M\d+)", text)),
            "",
        )
        notice_url = next(
            (str(cell.get("href") or "") for cell in row if cell.get("href")),
            "",
        )
        dates = [
            text for text in cells if re.fullmatch(r"\d{2}/\d{2}/\d{4}", text)
        ]
        records.append(
            {
                "project_id": project_id,
                "title": title,
                "announcement_date_be": dates[-1] if dates else "",
                "notice_url": notice_url,
                "source_index_url": source_url,
                "announcement_type_code": type_code,
            }
        )

    unique_records: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        key = (
            record["project_id"],
            record["announcement_date_be"],
            record["title"],
        )
        if key in seen:
            continue
        seen.add(key)
        unique_records.append(record)
    return unique_records


def main() -> int:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--index",
        choices=("winner", "tender"),
        default="winner",
        help="TMD index to read; winner is the W0 index, tender is the B0 index.",
    )
    argument_parser.add_argument(
        "--url",
        help="Override the selected TMD index URL.",
    )
    argument_parser.add_argument(
        "--related",
        action="store_true",
        help="Extract all radar-related rows, not only S-band dual-polarization rows.",
    )
    args = argument_parser.parse_args()
    source_url = args.url or (
        WINNER_INDEX_URL if args.index == "winner" else TENDER_INDEX_URL
    )

    try:
        html = fetch(source_url)
        records = extract_related(html, source_url) if args.related else extract(html, source_url)
    except Exception as exc:  # pragma: no cover - command-line error path
        print(f"extract failed: {exc}", file=sys.stderr)
        return 1

    json.dump(records, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
