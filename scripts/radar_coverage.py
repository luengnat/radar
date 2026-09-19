#!/usr/bin/env python3
"""Compute weather-radar coverage overlap over Thai land area.

Inputs (all public):
  - data/radar_stations_map.json   stations with lat/lon/radius_km (THAITH page
    coordinates + new-station district centroids from the archived TORs)
  - data/tha_adm0_simplified.geojson   geoBoundaries THA ADM0 simplified

Outputs:
  - data/radar_coverage_summary.json
  - data/radar_coverage_map.svg

Method: 0.04° grid over the land polygon (ray-casting point-in-polygon),
count stations whose circle covers each cell centre (haversine km).
Caveat: geometric screening only — no beam height, terrain, or elevation
mask; states that plainly in every output. // ponytail: grid mask, not real
propagation; upgrade path = beam-blockage DEM analysis.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R_EARTH = 6371.0
STEP = 0.04


def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(a))


def load_polygon():
    g = json.loads((ROOT / "data" / "tha_adm0_simplified.geojson").read_text())
    rings = []
    for feat in g["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            rings.append(geom["coordinates"][0])
        elif geom["type"] == "MultiPolygon":
            rings.extend(poly[0] for poly in geom["coordinates"])
    return rings


def inside(lat, lon, rings):
    for ring in rings:
        if point_in_ring(lat, lon, ring):
            return True
    return False


def point_in_ring(lat, lon, ring):
    hit = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        yi, xi = ring[i][1], ring[i][0]
        yj, xj = ring[j][1], ring[j][0]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def main():
    stations = json.loads((ROOT / "data" / "radar_stations_map.json").read_text())
    rings = load_polygon()

    lat = 5.5
    cells = []  # (lat, lon)
    while lat <= 20.6:
        lon = 97.0
        while lon <= 106.0:
            if inside(lat, lon, rings):
                cells.append((lat, lon))
            lon += STEP
        lat += STEP

    def counts_for(active):
        n = [0] * len(cells)
        for idx, (la, lo) in enumerate(cells):
            c = 0
            for st in active:
                if haversine(la, lo, st["lat"], st["lon"]) <= st["radius_km"]:
                    c += 1
            n[idx] = c
        return n

    existing = [s for s in stations if s["status"] == "existing"]
    planned = [s for s in stations if s["status"] != "existing"]
    n_tmd = sum(1 for s in existing if s["agency"] == "TMD")
    n_rrd = sum(1 for s in existing if s["agency"] == "RRD")
    n_bma = len(existing) - n_tmd - n_rrd

    base = counts_for(existing)
    area_cell = (111.32 * STEP) * (111.32 * STEP * math.cos(math.radians(14.5)))
    total = len(cells)
    dist = {k: base.count(k) for k in range(5)}
    summary = {
        "metadata": {
            "grid_step_deg": STEP,
            "land_cells": total,
            "approx_land_area_km2": round(total * area_cell),
            "method": "geometric circle coverage over geoBoundaries THA ADM0 land cells; no beam-height/terrain masking",
            "source_stations": f"{len(existing)} existing stations ({n_tmd} TMD + {n_rrd} RRD + {n_bma} BMA X-band) from the THAITH radar page, weather.tmd.go.th feed roster, RRD roster, TMD official list (R-3.pdf) and TOR district centroids + new/planned stations",
        },
        "existing_coverage_pct": {
            "0": round(100 * dist.get(0, 0) / total, 1),
            "1": round(100 * dist.get(1, 0) / total, 1),
            "2": round(100 * dist.get(2, 0) / total, 1),
            "3plus": round(100 * (total - dist.get(0, 0) - dist.get(1, 0) - dist.get(2, 0)) / total, 1),
        },
        "new_stations_marginal": {},
    }

    for st in planned:
        after = counts_for(existing + [st])
        gained = sum(1 for i in range(total) if after[i] > 0 and base[i] == 0)
        upgraded = sum(1 for i in range(total) if after[i] > base[i]) - gained
        udon_cell = min(range(len(cells)), key=lambda i: haversine(*cells[i], 17.45, 102.78))
        summary["new_stations_marginal"][st["name"]] = {
            "newly_covered_cells": gained,
            "newly_covered_km2": round(gained * area_cell),
            "newly_covered_pct_of_thailand": round(100 * gained / total, 2),
            "cells_gaining_extra_overlap": upgraded,
        }
        if "อุดร" in st["name"]:
            summary["udon_site_coverage_before"] = base[udon_cell]

    out = ROOT / "data" / "radar_coverage_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- SVG map ----
    W, H = 760, 1100
    lo0, lo1, la1, la0 = 96.5, 106.5, 21.0, 5.0

    def x(lo):
        return (lo - lo0) / (lo1 - lo0) * W

    def y(la):
        return (la1 - la) / (la1 - la0) * H

    bands = ["#f5f1e6", "#cfe3f3", "#8fc1e3", "#4a90c4", "#1f4e79"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial">']
    parts.append(f'<rect width="{W}" height="{H}" fill="#eaf4f4"/>')
    for idx, (la, lo) in enumerate(cells):
        parts.append(
            f'<rect x="{x(lo):.1f}" y="{y(la):.1f}" width="3.2" height="3.2" '
            f'fill="{bands[min(base[idx], 4)]}"/>'
        )
    for st in stations:
        col = "#005f73" if st["agency"] == "TMD" else ("#9d4edd" if st["agency"] == "RRD" else "#d1495b")
        dash = ' stroke-dasharray="4,3"' if st["status"] != "existing" else ""
        parts.append(
            f'<circle cx="{x(st["lon"]):.0f}" cy="{y(st["lat"]):.0f}" r="{st["radius_km"] / 111 * (W / (lo1 - lo0)):.0f}" '
            f'fill="{col}" fill-opacity="0.05" stroke="{col}" stroke-opacity="0.5"{dash}/>'
        )
        parts.append(f'<circle cx="{x(st["lon"]):.0f}" cy="{y(st["lat"]):.0f}" r="4" fill="{col}"/>')
    parts.append(
        f'<text x="20" y="30" font-size="22" fill="#222">Thailand weather-radar geometric coverage '
        f'({len(existing)} existing stations)</text>'
    )
    parts.append('<text x="20" y="56" font-size="15" fill="#555">0/1/2/3+ radar overlap — screening only, no beam-height/terrain analysis</text>')
    parts.append(f'<text x="20" y="1076" font-size="13" fill="#005f73">● TMD ({n_tmd})</text>')
    parts.append(f'<text x="120" y="1076" font-size="13" fill="#9d4edd">● RRD ({n_rrd})</text>')
    parts.append('<text x="220" y="1076" font-size="13" fill="#d1495b">◌ new/planned (from TOR districts)</text>')
    parts.append("</svg>")
    (ROOT / "data" / "radar_coverage_map.svg").write_text("".join(parts))

    print(json.dumps(summary["existing_coverage_pct"], ensure_ascii=False))
    for k, v in summary["new_stations_marginal"].items():
        print(k, "->", v["newly_covered_pct_of_thailand"], "% new land")
    print("Udon site existing coverage:", summary.get("udon_site_coverage_before"))


if __name__ == "__main__":
    main()
