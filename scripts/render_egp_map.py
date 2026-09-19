#!/usr/bin/env python3
"""Render the station ↔ e-GP award map from data/station_egp_join.json.

Inputs (all public):
  - data/radar_stations_map.json      station coordinates/agency
  - data/station_egp_join.json        verified e-GP anchors per station
  - data/tha_adm0_simplified.geojson  geoBoundaries THA ADM0 outline

Output: data/radar_egp_map.svg (+ .png via qlmanage when available).

Reproducible replacement for the one-off render of 17 Sep 2026.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WINNER_SHORT = {"จีโนแมทช์": "จีโนแมทช์", "มาร์วิน": "มาร์วิน", "ไซแอนติฟิค": "ไซแอนติฟิค", "เอเซียเมท": "เอเซียเมท"}


def winner_short(name: str | None) -> str:
    if not name:
        return "—"
    for key, short in WINNER_SHORT.items():
        if key in name:
            return short
    return name[:14]


def millions(baht: float | None) -> str:
    return f"{baht / 1_000_000:,.3f}M" if baht else "—"


def anchor_lines(entry: dict) -> list[str]:
    res = entry.get("verified_result") or {}
    pid = entry.get("project_id") or (entry.get("template_id") or "?")[:8]
    year = (entry.get("announce_date_be") or "").split("/")[-1]
    if "bidders" in res:  # FY2568 S-band shape: full bidder list
        rows = sorted(res["bidders"], key=lambda b: b[1])
        lines = [f"e-GP {pid}:"]
        for bidder, value, flag in res["bidders"]:
            mark = "✔" if flag == "P" else "✘"
            lines.append(f"{mark} {winner_short(bidder)} {millions(value)}")
        if rows[0][2] == "N":
            lines.append(f"lowest {winner_short(rows[0][0])} {millions(rows[0][1])} not passed")
        return lines
    return [f"e-GP {pid} ({year}):", f"{winner_short(res.get('winner'))} {millions(res.get('value_baht'))}"]


def main() -> None:
    stations = json.loads((ROOT / "data" / "radar_stations_map.json").read_text())
    join = json.loads((ROOT / "data" / "station_egp_join.json").read_text())
    rings = []
    for feat in json.loads((ROOT / "data" / "tha_adm0_simplified.geojson").read_text())["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            rings.append(geom["coordinates"][0])
        elif geom["type"] == "MultiPolygon":
            rings.extend(poly[0] for poly in geom["coordinates"])

    def match_join(name: str) -> list[dict]:
        base = name.split(" (")[0]
        for key, entries in join.items():
            if key == base or key.split(" (")[0] == base:
                return entries
        return []

    W, H = 1000, 1400
    lo0, lo1, la1, la0 = 96.5, 106.5, 21.5, 5.0

    def x(lo):
        return (lo - lo0) / (lo1 - lo0) * (W - 260) + 30

    def y(la):
        return (la1 - la) / (la1 - la0) * (H - 120) + 60

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,Thonburi">']
    parts.append(f'<rect width="{W}" height="{H}" fill="#f7f9fa"/>')
    for ring in rings:
        pts = " ".join(f"{x(lo):.0f},{y(la):.0f}" for lo, la in ring)
        parts.append(f'<polygon points="{pts}" fill="#e2eaee" stroke="#7d939d" stroke-width="1.4"/>')

    n_anchor = 0
    seen: set[tuple[str, str]] = set()  # (station base name, project_id)
    for st in stations:
        col = "#005f73" if st["agency"] == "TMD" else ("#9d4edd" if st["agency"] == "RRD" else "#d1495b")
        cx, cy = x(st["lon"]), y(st["lat"])
        dash = ' stroke-dasharray="4,3"' if st.get("status") != "existing" else ""
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{st.get("radius_km", 240) / 111 * ((W - 260) / (lo1 - lo0)):.0f}" fill="{col}" fill-opacity="0.04" stroke="{col}" stroke-opacity="0.35"{dash}/>')
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="5" fill="{col}"/>')
        for entry in match_join(st["name"]):
            if not entry.get("verified_result"):
                continue  # index lead: no award annotation yet
            key = (st["name"].split(" (")[0], entry.get("project_id", ""))
            if key in seen:
                continue  # duplicate map row for the same physical station
            seen.add(key)
            n_anchor += 1
            lines = anchor_lines(entry)
            bx = min(cx + 12, W - 250)
            by = max(cy - 10, 70)
            parts.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="235" height="{16 * len(lines) + 10}" rx="4" fill="#ffffff" fill-opacity="0.92" stroke="{col}" stroke-opacity="0.6"/>')
            parts.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{bx:.0f}" y2="{by + 12:.0f}" stroke="{col}" stroke-opacity="0.5" stroke-width="1"/>')
            for i, line in enumerate(lines):
                parts.append(f'<text x="{bx + 8:.0f}" y="{by + 18 + 16 * i:.0f}" font-size="12" fill="#1c2b33">{line}</text>')

    parts.append(f'<text x="30" y="34" font-size="24" fill="#1c2b33">Thai weather-radar stations ↔ verified e-GP awards</text>')
    parts.append('<text x="30" y="58" font-size="14" fill="#5a6b73">Anchors from data/station_egp_join.json — FY2568 S-band four (full bidder lists), FY2567 five, FY2563 C-band trio, FY2559 pair. Winner notices archived; bidder counts open except where shown.</text>')
    parts.append('<text x="30" y="H-30" font-size="13" fill="#005f73">● TMD</text>'.replace("H-30", str(H - 30)))
    parts.append(f'<text x="110" y="{H - 30}" font-size="13" fill="#9d4edd">● RRD</text>')
    parts.append(f'<text x="190" y="{H - 30}" font-size="13" fill="#d1495b">● BMA</text>')
    parts.append(f'<text x="260" y="{H - 30}" font-size="13" fill="#5a6b73">◌ dashed = new/planned · ✔ passed · ✘ not passed · value incl. VAT</text>')
    parts.append("</svg>")
    out = ROOT / "data" / "radar_egp_map.svg"
    out.write_text("".join(parts), encoding="utf-8")
    try:
        subprocess.run(["qlmanage", "-t", "-s", "1400", "-o", str(ROOT / "data"), str(out)], capture_output=True, timeout=60, check=False)
    except FileNotFoundError:
        pass
    print(f"rendered {n_anchor} award anchors -> {out}")


if __name__ == "__main__":
    main()
