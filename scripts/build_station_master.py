#!/usr/bin/env python3
"""Build the reproducible radar station master.

Every station and procurement field is represented as ``{"value": ..., 
"source": [...]}``.  Add verified input rows to ``data/`` and rerun this
script to rebuild both outputs.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent

SOURCE_CATALOG: dict[str, dict[str, Any]] = {
    "S-BUILD": {"label": "This generator and deterministic transformations", "file": "scripts/build_station_master.py", "evidence_status": "Derived"},
    "S-MAP": {"label": "Base station map: name, agency, approximate coordinates, radius and status", "file": "data/radar_stations_map.json", "url": "https://open.thaith.ai/radar/", "evidence_status": "Mixed input; retain row note in locator"},
    "S-TMD-FEED": {"label": "TMD public radar-feed roster and feed/index leads", "file": "data/radar_stations_map.json", "url": "https://weather.tmd.go.th/paipibat/", "evidence_status": "Public roster / lead"},
    "S-TMD-WEATHER": {"label": "TMD public weather-radar homepage and product menu", "urls": ["https://weather.tmd.go.th/", "https://weather.tmd.go.th/phb.php"], "evidence_status": "Verified public service listing; labels/products are not an equipment register"},
    "S-TMD-KNOWLEDGE": {"label": "TMD official station/type table", "file": "data/tmd_official_radar_station_list_2026-09-19.json", "url": "https://ubonmet.tmd.go.th/files/KM-base/R-3.pdf", "evidence_status": "Verified official station/type list; not an as-built asset register"},
    "S-RRD-ROSTER": {"label": "Royal Rainmaking official station roster", "file": "data/rrd_radar_station_roster_2026-09-15.json", "url": "https://www.royalrain.go.th/royalrain/Editor_Page.aspx?MenuId=43", "evidence_status": "Verified roster"},
    "S-RRD-CAPPI": {"label": "RRD official public CAPPI page for Singhanakhon mobile station", "url": "https://file.royalrain.go.th/opendata/radar_data/cappi/?station=singha", "evidence_status": "Verified public station page; page does not state band or model"},
    "S-TMD-HIST": {"label": "TMD verified historical procurement corpus", "file": "data/tmd_historical_radar_procurement_2555-2569.json", "evidence_status": "Verified records; locator URL per event"},
    "S-RRD-HIST": {"label": "RRD verified historical procurement and five-year plan corpus", "file": "data/rrd_historical_radar_procurement_2566.json", "evidence_status": "Verified records / verified plan; locator URL per event"},
    "S-RRD-FY2570": {"label": "User-supplied RRD FY2570 request originals and budget draft", "files": ["data/sources_rrd/rrd_fy2570_udon_radar_original.pdf", "data/sources_rrd/rrd_fy2570_phimai_radar_original.pdf", "data/sources_rrd/budget_draft_2570_agriculture_vol3_4.pdf"], "url": "https://drive.google.com/drive/folders/170o8gB5Snc-Y96KNaNf5N4cpxSkLoFUn", "evidence_status": "Request / draft; not an award"},
    "S-GFMIS": {"label": "GFMIS/PBO disbursement and payment trail", "file": "data/gfmis_radar_disbursements_2026-09-17.json", "url": "https://pbo-mcp.thaith.ai/manual", "evidence_status": "Verified query / reconciliation"},
    "S-EGP": {"label": "Project-specific e-GP bidder and award results", "files": ["data/egp_sband_procure_results_api_2026-09-17.json", "data/egp_sband_reconciliation_2026-09-17.json", "data/egp_sband_bidder_lists_2026-09-15.json"], "url": "https://www.gprocurement.go.th/", "evidence_status": "Verified snapshot"},
    "S-EGP-TOR": {"label": "TMD FY2569 S-band TOR and reference-price archive", "file": "data/tmd_sband_tor_specs_2568.json", "url": "https://tmd.go.th/Procurement/ProcurementAnnoucementPage?ProcurementTypeCode=B0", "evidence_status": "Verified archive / extracted text"},
    "S-TMD-AWARD": {"label": "TMD FY2569 monthly award/contract summaries", "file": "data/tmd_radar_awards_2026-09-15.json", "evidence_status": "Verified official summary"},
    "S-STATION-JOIN": {"label": "Station-to-e-GP join and historical index leads", "file": "data/station_egp_join.json", "evidence_status": "Verified join for project IDs; index leads remain leads"},
    "S-OEM-REPORTED": {"label": "OEM/model registry claims recorded in the dossier", "file": "data/oem_compliance_matrix_2026-09-17.json", "url": "https://open.thaith.ai/radar/", "evidence_status": "Reported; not a substitute for as-built records"},
    "S-LIVE": {"label": "Same-day operational liveness sweep of the public radar portals", "file": "data/radar_liveness_2026-09-17.json", "url": "https://weather.tmd.go.th/", "evidence_status": "Verified single-day portal check; not an uptime register"},
    "S-UNKNOWN": {"label": "The reviewed sources do not state this field", "evidence_status": "Unknown / disclosure gap"},
    "S-DERIVED": {"label": "Derived by this script from cited input fields", "file": "scripts/build_station_master.py", "evidence_status": "Derived; not an independent source"},
}

OEM_REPORTED: dict[str, tuple[str, str | None, str]] = {
    "สกลนคร": ("C", "EEC DWSR-3501C-SPD", "Marwin 2558 contract"),
    "นราธิวาส": ("C", "EEC DWSR-3501C-SPD (ถูกแทนที่ 2567)", "Marwin 2558; 2567 C-band dual-pol"),
    "น่าน": ("C", "EEC (dossier registry)", "Marwin 2558 Doppler"),
    "อุบลราชธานี": ("C", "EEC (dossier registry)", "Marwin 2558 Doppler"),
    "สุวรรณภูมิ": ("S", "EEC DWSR-8501S-9", "Marwin 2561"),
    "หัวหิน": ("C", "SELEX ES METEOR 735C", "Genomatch 2560"),
    "พิมาย": ("S", "METEOR 600S", "RRD 2555; request to replace in FY2570"),
    "ร้องกวาง": ("S", "Gematronik line (dossier)", "RRD 2564, Genomatch"),
    "อมก๋อย": ("S", None, "RRD 2564"),
    "ตาคลี": ("S", None, "RRD fixed roster"),
    "สัตหีบ": ("S", None, "RRD fixed roster"),
    "พนม": ("S", None, "RRD fixed roster"),
}

ENGLISH_NAMES = {
    "เชียงราย": "Chiang Rai", "สุราษฎร์ธานี": "Surat Thani", "สุวรรณภูมิ": "Suvarnabhumi", "ลำพูน": "Lamphun", "ภูเก็ต": "Phuket", "ระยอง": "Rayong", "ชัยนาท": "Chai Nat", "สกลนคร": "Sakon Nakhon", "นราธิวาส": "Narathiwat", "นครนายก": "Khao Kiew", "วิเชียรบุรี": "Wichian Buri", "สุรินทร์": "Surin", "อุบลราชธานี": "Ubon Ratchathani", "ชุมพร": "Chumphon", "หาดใหญ่": "Hat Yai", "สมุย": "Samui", "สทิงพระ": "Sathing Phra",
}
STATION_ENGLISH = {"กระบี่": "Krabi", "บึงกาฬ": "Bueng Kan", "พิษณุโลก": "Phitsanulok", "ชุมพร": "Chumphon", "ร้องกวาง": "Rong Khwang", "สัตหีบ": "Sattahip", "พิมาย": "Phimai", "พนม": "Phanom", "บ้านผือ": "Ban Phue", "หาดใหญ่": "Hat Yai", "ราษีไศล": "Rasi Salai", "อุดรธานี": "Udon Thani"}
TMD_PUBLIC_LABELS = {"แม่ฮ่องสอน": "Mae Hong Son", "เชียงราย": "Chiang Rai", "ลำพูน": "Lamphun", "ตาก": "Doi Muser, Tak Province", "วิเชียรบุรี": "Phetchabun", "ขอนแก่น": "Khon Kaen", "สกลนคร": "Sakon Nakhon", "อุบลราชธานี": "Ubon Ratchathani", "สุรินทร์": "Surin", "ชัยนาท": "Chainat", "นครนายก": "Nakhon Nayok", "สมุทรสงคราม": "Samut Songkhram", "สุวรรณภูมิ": "Suvarnabhumi", "ระยอง": "Rayong", "ชุมพร": "Chumphon", "สุราษฎร์ธานี": "Surat Thani", "ระนอง": "Ranong", "ภูเก็ต": "Phuket", "ตรัง": "Trang", "หาดใหญ่": "Hat Yai", "นราธิวาส": "Narathiwat", "สทิงพระ": "Sathing Phra"}
TMD_PUBLIC_RADII = {"ขอนแก่น": [120, 240], "อุบลราชธานี": [120, 240], "สมุทรสงคราม": [120, 240], "สุวรรณภูมิ": [120, 240], "ตาก": [240, 480], "สกลนคร": [240, 480], "นครนายก": [240, 480]}

TMD_OFFICIAL_CANONICAL = {
    "เขาเขียว": "นครนายก",
    "ท่าวังผา จ.น่าน": "น่าน",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ref(source_id: str, locator: str | None = None, note: str | None = None) -> dict[str, str]:
    item: dict[str, str] = {"id": source_id}
    if locator:
        item["locator"] = str(locator)
    if note:
        item["note"] = note
    return item


def cell(value: Any, refs: Iterable[dict[str, str]] = (), *, note: str | None = None) -> dict[str, Any]:
    source = list(refs)
    if not source:
        source = [ref("S-UNKNOWN", note=note or "Not stated in the reviewed sources")]
    elif note:
        source.append(ref("S-DERIVED", note=note))
    return {"value": value, "source": source}


def contract_fields(
    *,
    year_be: Any,
    number: Any,
    date_be: Any,
    seller: Any,
    winner: Any,
    bidders: Any,
    refs: Iterable[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    """Return one normalized contract identity block for every procurement event.

    The legacy event fields (``winner`` and ``submitted_bids``) remain intact for
    compatibility.  These explicit names make the station master easier to query
    across TMD, RRD and e-GP records.  ``year_be`` is the source fiscal year; the
    exact signed/award date, when disclosed, remains in ``contract_date_be``.
    """
    return {
        "contract_year_be": cell(year_be, refs),
        "contract_number": cell(number, refs),
        "contract_date_be": cell(date_be, refs),
        "seller": cell(seller, refs),
        "contract_winner": cell(winner, refs),
        "contract_bidders": cell(bidders, refs),
    }


def unique_refs(refs: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in refs:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def provenance_refs(node: Any, *, skip_keys: set[str] | None = None) -> list[dict[str, str]]:
    """Collect all field-level references from a station/event tree."""
    skip_keys = skip_keys or set()
    refs: list[dict[str, str]] = []
    if isinstance(node, dict):
        if "value" in node and "source" in node:
            refs.extend(node["source"])
        else:
            for key, value in node.items():
                if key not in skip_keys:
                    refs.extend(provenance_refs(value, skip_keys=skip_keys))
    elif isinstance(node, list):
        for value in node:
            refs.extend(provenance_refs(value, skip_keys=skip_keys))
    return refs


def canonical_name(raw: str) -> str:
    return {"นครนายก (เขาเขียว)": "นครนายก", "ตาก (ดอยมูเซอ)": "ตาก", "สทิงพระ (C ใหม่)": "สทิงพระ"}.get(raw, raw.split(" (")[0])


def map_source_id(source_text: str) -> str:
    text = source_text.lower()
    if "official_tmd" in text or "tmd official" in text:
        return "S-TMD-KNOWLEDGE"
    if "gfmis" in text:
        return "S-GFMIS"
    if "rrd" in text or "royal rain" in text:
        return "S-RRD-ROSTER"
    if "tor" in text:
        return "S-EGP-TOR"
    if "weather.tmd" in text or "public feed" in text:
        return "S-TMD-FEED"
    return "S-MAP"


def map_ref(entry: dict[str, Any]) -> dict[str, str]:
    return ref(map_source_id(entry.get("source", "")), locator=entry.get("source"))


def status_summary(statuses: list[str]) -> str:
    values = set(statuses)
    if values == {"official-list-only"}:
        return "official TMD list only"
    if "existing" in values and any(s.startswith("new-") for s in values):
        new = sorted(s.removeprefix("new-fy") for s in values if s.startswith("new-fy"))
        return f"existing + new FY{', FY'.join(new)} project"
    if "existing" in values and any(s.startswith("requested-") for s in values):
        requested = sorted(s.removeprefix("requested-fy") for s in values if s.startswith("requested-fy"))
        return f"existing + FY{', FY'.join(requested)} request"
    if any(s.startswith("new-") for s in values):
        new = sorted(s.removeprefix("new-fy") for s in values if s.startswith("new-fy"))
        return f"new FY{', FY'.join(new)} project"
    if any(s.startswith("requested-") for s in values):
        requested = sorted(s.removeprefix("requested-fy") for s in values if s.startswith("requested-fy"))
        return f"FY{', FY'.join(requested)} request"
    return "; ".join(dict.fromkeys(statuses)) or "not stated"


def is_dual_pol(text: Any) -> bool:
    return bool(re.search(r"dual[- ]polar|dual[- ]pol|dual polarization", str(text or ""), re.I))


def tmd_event(record: dict[str, Any]) -> dict[str, Any]:
    source_url = record.get("source_url")
    refs = [ref("S-TMD-HIST", locator=source_url)]
    values = {
        "fiscal_year_be": record.get("fiscal_year_be"), "activity_class": record.get("activity_class"), "scope": record.get("station_or_scope"), "radar_band": record.get("radar_band"), "description": record.get("description"), "procurement_method": record.get("procurement_method"), "budget_baht": record.get("budget_baht"), "reference_price_baht": record.get("reference_price_baht"), "submitted_bids": record.get("bids"), "winner": record.get("selected_supplier"), "contract_value_baht": record.get("contract_value_baht"), "contract_number": record.get("contract_number"), "contract_date_be": record.get("contract_date_be"), "project_id": record.get("project_id"), "evidence_status": record.get("evidence_status"),
    }
    event = {key: cell(value, refs) for key, value in values.items() if value is not None}
    event.update(contract_fields(year_be=record.get("fiscal_year_be"), number=record.get("contract_number"), date_be=record.get("contract_date_be"), seller=record.get("selected_supplier"), winner=record.get("selected_supplier"), bidders=record.get("bids"), refs=refs))
    event["source_url"] = cell(source_url, refs)
    return event


def rrd_event(record: dict[str, Any]) -> dict[str, Any]:
    source_url = record.get("source_url") or (record.get("source_urls") or [None])[0]
    refs = [ref("S-RRD-HIST", locator=source_url)]
    amount = record.get("contract_value_baht", record.get("amount_as_reported_baht"))
    values = {
        "fiscal_year_be": record.get("fiscal_year_be"), "activity_class": record.get("activity_class"), "scope": record.get("site") or record.get("station_or_scope") or record.get("scope"), "radar_band": record.get("radar_band"), "description": record.get("description"), "procurement_method": record.get("procurement_method"), "budget_baht": record.get("budget_or_reference_price_baht"), "amount_as_reported_baht": amount, "winner": record.get("selected_supplier"), "contract_number": record.get("contract_number"), "contract_date_be": [x.get("date_be") for x in record.get("contract_date_sources", []) if x.get("date_be")], "payment_milestones": record.get("payment_milestones"), "contract_status": record.get("contract_status"), "evidence_status": record.get("evidence_status"), "review_note": record.get("review_note"),
    }
    event = {key: cell(value, refs) for key, value in values.items() if value not in (None, [], {})}
    event.update(contract_fields(year_be=record.get("fiscal_year_be"), number=record.get("contract_number"), date_be=values["contract_date_be"], seller=record.get("selected_supplier"), winner=record.get("selected_supplier"), bidders=None, refs=refs))
    event["source_url"] = cell(source_url, refs)
    return event


def plan_event(record: dict[str, Any]) -> dict[str, Any]:
    source_url = record.get("source_url")
    refs = [ref("S-RRD-HIST", locator=source_url)]
    amount = record.get("planned_amount_million_baht")
    amount_baht = amount * 1_000_000 if isinstance(amount, (int, float)) else None
    values = {
        "fiscal_year_be": record.get("planned_fiscal_year_be"), "fiscal_years_be": record.get("planned_fiscal_years_be"), "plan_period_be": record.get("plan_period_be"), "activity_class": record.get("activity_class"), "scope": record.get("station_or_scope"), "radar_band": record.get("radar_band"), "planned_amount_baht": amount_baht, "evidence_status": record.get("evidence_status"), "review_note": record.get("review_note"),
    }
    event = {key: cell(value, refs) for key, value in values.items() if value is not None}
    event["source_url"] = cell(source_url, refs)
    return event


def egp_event(recon: dict[str, Any], api: dict[str, Any] | None, award: dict[str, Any] | None, tor: dict[str, Any]) -> dict[str, Any]:
    project_id = recon["project_id"]
    refs = [ref("S-EGP", locator=f"getProcureResult projectId={project_id}"), ref("S-TMD-AWARD", locator=(award or {}).get("source_url")), ref("S-EGP-TOR", locator=f"project {project_id}; identical TOR/reference-price package")]
    values = {
        "fiscal_year_be": 2569, "activity_class": "new_radar_purchase", "scope": recon.get("station"), "radar_band": "S-band dual-polarization", "description": "S-band dual-polarization weather radar with communications equipment, building and radar tower", "procurement_method": "e-bidding", "project_id": project_id, "budget_baht": tor.get("budget_baht"), "reference_price_baht": tor.get("reference_price_baht"), "submitted_bids": (api or {}).get("bidders"), "bidder_count": recon.get("bidder_count"), "passed_count": recon.get("passed_count"), "winner": recon.get("egp_winner"), "award_or_contract_value_baht": recon.get("egp_winner_baht"), "lowest_bidder": recon.get("lowest_bidder"), "lowest_bid_baht": recon.get("lowest_bid_baht"), "lowest_result_flag": recon.get("lowest_result_flag"), "passed_bidders": recon.get("passed_bidders"), "contract_number": (award or {}).get("contract_number"), "contract_date_be": (award or {}).get("contract_date_be"), "award_date_be": (award or {}).get("winner_notice_date_be"), "evidence_status": "Verified e-GP result + official TMD award summary", "mapping_status": recon.get("mapping_status"),
    }
    event = {key: cell(value, refs) for key, value in values.items() if value is not None}
    event.update(contract_fields(year_be=2569, number=(award or {}).get("contract_number"), date_be=(award or {}).get("contract_date_be"), seller=recon.get("egp_winner"), winner=recon.get("egp_winner"), bidders=(api or {}).get("bidders"), refs=refs))
    event["source_url"] = cell(f"https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement/getProcureResult?projectId={project_id}", refs)
    return event


def fy2570_request(name: str, description: str, *, replacement: bool) -> dict[str, Any]:
    refs = [ref("S-RRD-FY2570", locator="user-supplied original PDF; quotation pages 112–114")]
    values = {
        "fiscal_year_be": 2570, "activity_class": "replacement_request" if replacement else "new_radar_request", "scope": name, "radar_band": "S-band dual-polarization", "description": description, "planned_amount_baht": 480_000_000, "quotation_set_baht": {"Genomatch": 480_000_000, "Scientific Research": 486_300_000, "Marwin": 492_000_000}, "brand_or_platform_in_draft_tor": "LEONARDO/Gematronik", "transmitter_peak_power_kw": 850, "evidence_status": "Request / draft TOR; not an award", "review_note": "Printed source pages support the request and quotation comparison; final TOR, BOQ and procurement status remain open.",
    }
    return {key: cell(value, refs) for key, value in values.items()}


def build(root: Path) -> dict[str, Any]:
    data = root / "data"
    map_rows = load_json(data / "radar_stations_map.json")
    tmd_official = load_json(data / "tmd_official_radar_station_list_2026-09-19.json")
    tmd_official_rows = {
        TMD_OFFICIAL_CANONICAL.get(item.get("canonical_name") or item["name"], item.get("canonical_name") or item["name"]): item
        for item in tmd_official.get("stations", [])
        if item.get("physical_station", True)
    }
    tmd_hist = load_json(data / "tmd_historical_radar_procurement_2555-2569.json")
    rrd_hist = load_json(data / "rrd_historical_radar_procurement_2566.json")
    load_json(data / "gfmis_radar_disbursements_2026-09-17.json")  # input presence check; station notes cite it
    reconciliation = load_json(data / "egp_sband_reconciliation_2026-09-17.json")
    api_results = load_json(data / "egp_sband_procure_results_api_2026-09-17.json")
    awards = {item["project_id"]: item for item in load_json(data / "tmd_radar_awards_2026-09-15.json")}
    tor = load_json(data / "tmd_sband_tor_specs_2568.json")
    liveness = load_json(data / "radar_liveness_2026-09-17.json")
    rrd_live = set(liveness["rrd_cappi"]["live_today"])
    rrd_nodata = set(liveness["rrd_cappi"]["no_data_returned"])
    live_refs = [ref("S-LIVE", locator=f"data/radar_liveness_2026-09-17.json ({liveness['metadata']['checked']})")]
    api_by_project = {item["project_id"]: item for item in api_results.get("results", [])}

    grouped: OrderedDict[tuple[str, str], list[dict[str, Any]]] = OrderedDict()
    for row in map_rows:
        grouped.setdefault((row["agency"], canonical_name(row["name"])), []).append(row)

    # The official TMD knowledge table contains a few stations that are not
    # present in the THAITH map snapshot (notably Hat Yai, Narathiwat and Samui).
    # Keep them as explicit official-list-only records rather than silently
    # treating the map snapshot as a complete national asset register.
    mapped_tmd_names = {name for agency, name in grouped if agency == "TMD"}
    for name in tmd_official_rows:
        if name in mapped_tmd_names:
            continue
        grouped[("TMD", name)] = [{
            "agency": "TMD",
            "name": name,
            "status": "official-list-only",
            "lat": None,
            "lon": None,
            "radius_km": None,
            "source": "official_tmd_list",
        }]

    records: list[dict[str, Any]] = []
    for (agency, name), rows in grouped.items():
        row_refs = unique_refs(map_ref(row) for row in rows)
        statuses = [row.get("status") for row in rows if row.get("status")]
        source_ids = list(dict.fromkeys(item["id"] for item in row_refs))
        derived_refs = [ref("S-DERIVED", locator=f"canonical group {agency}/{name}")]
        official_station_refs = [ref("S-RRD-CAPPI", locator="page title: สถานีเรดาร์ฝนหลวง สิงหนคร (เคลื่อนที่)")] if agency == "RRD" and name == "สิงหนคร" else []
        lat = rows[0].get("lat") if rows else None
        lon = rows[0].get("lon") if rows else None
        radius = rows[0].get("radius_km") if rows else None
        record: dict[str, Any] = {
            "station_id": cell(f"{agency.lower()}:{name}", derived_refs), "name_th": cell(name, row_refs + official_station_refs), "aliases": [cell(row["name"], [map_ref(row)]) for row in rows if row["name"] != name], "agency": cell(agency, row_refs), "coordinates": {"lat": cell(lat, row_refs), "lon": cell(lon, row_refs)}, "coverage": {"screening_radius_km": cell(radius, row_refs), "basis": cell("geometric screening radius from station map; not a validated beam/terrain footprint", [ref("S-MAP")])}, "status": cell(status_summary(statuses), row_refs + derived_refs), "status_inputs": [cell(row.get("status"), [map_ref(row)]) for row in rows], "public_service": {}, "radar": {}, "procurement": {"events": [], "progress": [], "planned": []}, "source_ids": cell(source_ids, row_refs), "quality_flags": [],
        }
        official_tmd = tmd_official_rows.get(name) if agency == "TMD" else None
        official_tmd_refs = [ref("S-TMD-KNOWLEDGE", locator=tmd_official["metadata"]["source_url"])] if official_tmd else []
        if official_tmd:
            record["radar"]["official_tmd_type"] = cell(official_tmd.get("official_type"), official_tmd_refs)
            record["radar"]["official_tmd_code"] = cell(official_tmd.get("code"), official_tmd_refs)
            if not rows or rows[0].get("source") == "official_tmd_list":
                record["quality_flags"].append(cell("official TMD station/type listing found, but no matching THAITH map row; coordinates and as-built details remain unknown", official_tmd_refs))
        if len(rows) > 1:
            record["quality_flags"].append(cell("duplicate map rows merged into one physical station record", row_refs + derived_refs))
        if agency == "TMD" and name in TMD_PUBLIC_LABELS:
            weather_refs = [ref("S-TMD-WEATHER", locator="TMD weather-radar homepage station menu")]
            if name == "วิเชียรบุรี":
                weather_refs.append(ref("S-TMD-WEATHER", locator="https://weather.tmd.go.th/phb.php; page title/image uses Phetchabun and Wichian Buri"))
                record["quality_flags"].append(cell("TMD public feed label is Phetchabun while the station map label is Wichian Buri; identity needs an official station-name crosswalk", weather_refs + derived_refs))
            record["public_service"] = {"provider": cell("Thai Meteorological Department", weather_refs), "listed_on_homepage": cell(True, weather_refs), "public_label": cell(TMD_PUBLIC_LABELS[name], weather_refs)}
            if name in TMD_PUBLIC_RADII:
                record["public_service"]["published_product_radii_km"] = cell(TMD_PUBLIC_RADII[name], weather_refs)

        if agency == "RRD" and name in rrd_live:
            record["operational"] = cell("CAPPI frame same day (17 Sep 2026)", live_refs)
        elif agency == "RRD" and name in rrd_nodata:
            record["operational"] = cell("API returned no data this pass; not proof of outage", live_refs)
        elif agency == "TMD" and name == "กระบี่":
            record["operational"] = cell("Out-of-Service placeholder served since 2019", live_refs)
        elif agency == "TMD" and name == "หาดใหญ่":
            record["operational"] = cell("Current image verified 19 Sep 2026 (feed added with the official-list pass)", live_refs)
        elif agency == "TMD" and name == "สมุย":
            record["operational"] = cell("Feed page exists; image returned 404 on 19 Sep 2026 — not proof of outage", live_refs)
        elif agency == "TMD" and "existing" in statuses:
            record["operational"] = cell("Current image in agency feed sweep", live_refs)

        band: Any = None
        band_refs: list[dict[str, str]] = []
        model: Any = None
        model_refs: list[dict[str, str]] = []
        oem_tier: Any = None
        oem_refs: list[dict[str, str]] = []
        oem_note: Any = None
        if name in OEM_REPORTED:
            band, model, oem_note = OEM_REPORTED[name]
            band_refs = [ref("S-OEM-REPORTED", locator=f"dossier registry: {name}")]
            model_refs = band_refs
            oem_tier = "Reported (dossier registry)"
            oem_refs = band_refs
        if agency == "RRD" and band is None:
            if name in {"บ้านผือ", "ราษีไศล", "ปะทิว", "สิงหนคร"}:
                band = "C (5.6 GHz mobile)"
                band_refs = [ref("S-RRD-ROSTER", locator="RRD-02 mobile C-band roster")] + official_station_refs
            elif name == "หาดใหญ่":
                band = "S dual-pol"
                band_refs = [ref("S-GFMIS", locator="GFMIS-04 FY2567 item")]
        if agency == "TMD" and band is None and name in {"ตาก", "ระนอง", "ตรัง"}:
            band = "C dual-pol"
            band_refs = [ref("S-STATION-JOIN", locator="FY2563 C-band (verified, TMD-32)")]
        if name == "สทิงพระ":
            band = "C dual-pol"
            band_refs = row_refs

        if official_tmd and band is None:
            official_type = str(official_tmd.get("official_type") or "")
            if official_type in {"S-Band", "C-Band", "X-Band"}:
                band = official_type.removesuffix("-Band")
                band_refs = official_tmd_refs

        english = ENGLISH_NAMES.get(name, name)
        dual_refs: list[dict[str, str]] = []
        for event_record in tmd_hist.get("verified_records", []):
            scope = str(event_record.get("station_or_scope") or "")
            if english in scope:
                record["procurement"]["events"].append(tmd_event(event_record))
                if band is None and event_record.get("radar_band"):
                    band = event_record["radar_band"]
                    band_refs = [ref("S-TMD-HIST", locator=event_record.get("source_url"))]
                if is_dual_pol(event_record.get("description")) or is_dual_pol(event_record.get("radar_band")):
                    dual_refs.append(ref("S-TMD-HIST", locator=event_record.get("source_url")))
        for progress_record in tmd_hist.get("progress_records", []):
            progress_scope = str(progress_record.get("station_or_scope") or progress_record.get("site") or "")
            if english in progress_scope:
                record["procurement"]["progress"].append(tmd_event(progress_record))

        if agency == "TMD":
            for recon in reconciliation.get("records", []):
                if recon.get("station") == STATION_ENGLISH.get(name):
                    project_id = recon["project_id"]
                    record["procurement"]["events"].append(egp_event(recon, api_by_project.get(project_id), awards.get(project_id), tor))
                    band = "S-band dual-polarization"
                    band_refs = [ref("S-EGP-TOR", locator=f"project {project_id}")]
                    dual_refs.append(ref("S-EGP-TOR", locator=f"project {project_id}"))

        if agency == "RRD":
            for event_record in rrd_hist.get("verified_records", []):
                scope = str(event_record.get("site") or event_record.get("station_or_scope") or event_record.get("scope") or "")
                if STATION_ENGLISH.get(name) and STATION_ENGLISH[name] in scope:
                    record["procurement"]["events"].append(rrd_event(event_record))
                    if band is None and event_record.get("radar_band"):
                        band = event_record["radar_band"]
                        band_refs = [ref("S-RRD-HIST", locator=event_record.get("source_url"))]
                    if is_dual_pol(event_record.get("description")):
                        dual_refs.append(ref("S-RRD-HIST", locator=event_record.get("source_url")))
            for plan_record in rrd_hist.get("planned_records", []):
                scope = str(plan_record.get("station_or_scope") or "")
                if STATION_ENGLISH.get(name) and STATION_ENGLISH[name] in scope:
                    record["procurement"]["planned"].append(plan_event(plan_record))

        if agency == "RRD" and name == "อุดรธานี":
            record["procurement"]["planned"].append(fy2570_request("Udon Thani / Mueang Mon", "New fixed S-band dual-polarization radar station", replacement=False))
            band = band or "S-band dual-polarization"
            band_refs = band_refs or [ref("S-RRD-FY2570", locator="Udon original PDF, TOR/spec pages")]
            dual_refs.append(ref("S-RRD-FY2570", locator="Udon original PDF, TOR/spec pages"))
        if agency == "RRD" and name == "พิมาย":
            record["procurement"]["planned"].append(fy2570_request("Phimai / Rangka Yai", "Replacement of the existing METEOR 600S radar", replacement=True))
            band = band or "S-band dual-polarization"
            band_refs = band_refs or [ref("S-RRD-FY2570", locator="Phimai original PDF, TOR/spec pages")]
            dual_refs.append(ref("S-RRD-FY2570", locator="Phimai original PDF, TOR/spec pages"))

        gfmis_locators = {"ร้องกวาง": "Rong Khwang payment trail", "อมก๋อย": "FY2564 in-year disbursement", "หาดใหญ่": "FY2567 tranche 1", "สัตหีบ": "FY2568 upgrade"}
        if agency == "RRD" and name in gfmis_locators:
            record["procurement"]["payment_notes"] = [cell("See GFMIS reconciliation record", [ref("S-GFMIS", locator=gfmis_locators[name])])]

        record["radar"]["dual_polarization"] = cell(True, unique_refs(dual_refs)) if dual_refs else cell(None, note="No explicit dual-polarization statement matched this station")
        if official_tmd and band:
            # run after ALL band assignments so conflicts on e-GP/historical stations are caught
            def band_letter(text: str) -> set[str]:
                low = str(text).lower()
                return {b for b in ("s", "c", "x") if f"{b}-band" in low or f"{b} band" in low or (b == "c" and low.startswith("c")) or (b == "s" and low.startswith("s"))}
            if band_letter(official_tmd.get("official_type")) and band_letter(band) and band_letter(official_tmd.get("official_type")) != band_letter(band):
                record["quality_flags"].append(cell("official TMD type table and station-specific band/OEM evidence differ; could reflect legacy versus replacement equipment, or an unresolved source conflict", official_tmd_refs + band_refs + derived_refs))

        record["radar"]["band"] = cell(band, unique_refs(band_refs))
        record["radar"]["oem_model"] = cell(model, unique_refs(model_refs), note="Model is not stated in verified station-specific records" if model is None else None)
        record["radar"]["oem_tier"] = cell(oem_tier, unique_refs(oem_refs), note="No verified as-built/OEM record was found" if oem_tier is None else None)
        record["radar"]["oem_history_note"] = cell(oem_note, unique_refs(oem_refs), note="No dossier-reported OEM history matched this station" if oem_note is None else None)
        record["procurement"]["events"].sort(key=lambda event: event.get("fiscal_year_be", {}).get("value", 0) or 0)
        all_refs = unique_refs(provenance_refs(record, skip_keys={"source_ids"}))
        all_source_ids = list(dict.fromkeys(item["id"] for item in all_refs))
        record["source_ids"] = cell(all_source_ids, all_refs)
        records.append(record)

    network_plans = [plan_event(plan) for plan in rrd_hist.get("planned_records", []) if plan.get("station_or_scope") == "Royal Rainmaking radar network"]
    result = {"schema_version": cell("2.0", [ref("S-BUILD", locator="provenance wrapper schema")]), "generated_on": cell(date.today().isoformat(), [ref("S-BUILD")]), "description": cell("One record per mapped or official-list station/location; duplicate map annotations are retained as aliases. Official-list-only rows may not have coordinates. Unknown values remain null.", [ref("S-BUILD")]), "source_catalog": SOURCE_CATALOG, "stations": records, "network_plans": network_plans}

    # Audit: corpus records that matched no station must be listed explicitly,
    # never silently dropped. Matching mirrors the join loops above.
    unmatched: list[dict[str, Any]] = []

    def audit(corpus_key: str, rec: dict[str, Any], scope_keys: tuple[str, ...]) -> None:
        scope = " ".join(str(rec.get(k) or "") for k in scope_keys)
        if not scope or matched_station(scope, records):
            return
        unmatched.append({"corpus": corpus_key, "fiscal_year_be": rec.get("fiscal_year_be") or rec.get("planned_fiscal_year_be"), "scope": scope[:120],
                          "why_unmatched": "network/system-wide scope or station not in the station map (mobile unit, unnamed site, or no station stated)"})

    def matched_station(scope: str, recs: list[dict[str, Any]]) -> bool:
        # mirrors the join loops: a record is matched iff some station name
        # (Thai, alias, or mapped English form) appears in its scope string
        for station in recs:
            name_th = str(unwrap(station["name_th"]))
            candidates = [name_th] + [str(unwrap(a)) for a in station.get("aliases", [])]
            if name_th in ENGLISH_NAMES:
                candidates.append(ENGLISH_NAMES[name_th])
            if name_th in STATION_ENGLISH:
                candidates.append(STATION_ENGLISH[name_th])
            if any(c and c in scope for c in candidates):
                return True
        return False

    for rec in tmd_hist.get("verified_records", []):
        audit("tmd_verified", rec, ("station_or_scope",))
    for rec in tmd_hist.get("progress_records", []):
        audit("tmd_progress", rec, ("station_or_scope", "site"))
    for rec in rrd_hist.get("verified_records", []):
        audit("rrd_verified", rec, ("site", "station_or_scope", "scope"))
    for rec in rrd_hist.get("planned_records", []):
        audit("rrd_planned", rec, ("station_or_scope",))
    result["unmatched_events_audit"] = unmatched
    if unmatched:
        print(f"NOTE: {len(unmatched)} corpus records matched no station (kept in unmatched_events_audit)")
    validate_result(result)
    return result


def validate_result(result: dict[str, Any]) -> None:
    stations = result.get("stations", [])
    if not stations:
        raise ValueError("station master is empty")
    ids = [station["station_id"]["value"] for station in stations]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate station_id after canonical merge")

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            if "value" in node:
                if not isinstance(node.get("source"), list) or not node["source"]:
                    raise ValueError(f"missing provenance at {path}")
                return
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")

    walk({"stations": stations, "network_plans": result.get("network_plans", [])}, "result")


def unwrap(node: Any) -> Any:
    if isinstance(node, dict) and "value" in node and "source" in node:
        return node["value"]
    return node


def markdown_escape(value: Any) -> str:
    text = "—" if value in (None, "", []) else str(value)
    return text.replace("|", "／").replace("\n", " ").strip()


def money(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.2f} บาท"
    return f"{int(value):,} บาท"


def event_amount(event: dict[str, Any]) -> Any:
    for key in ("award_or_contract_value_baht", "contract_value_baht", "amount_as_reported_baht"):
        value = unwrap(event.get(key))
        if value is not None:
            return value
    return None


def bidder_summary(value: Any) -> str:
    bidders = value if isinstance(value, list) else []
    rendered: list[str] = []
    for bidder in bidders:
        if not isinstance(bidder, dict):
            rendered.append(str(bidder))
            continue
        supplier = bidder.get("supplier") or bidder.get("name") or "ไม่ระบุชื่อ"
        amount = bidder.get("price_proposal_baht")
        if amount is None:
            amount = bidder.get("amount_baht")
        if amount is None:
            amount = bidder.get("price_agree_baht")
        suffix = f" {money(amount)}" if amount is not None else ""
        flag = bidder.get("result_flag")
        if flag:
            suffix += f" [{flag}]"
        rendered.append(f"{supplier}{suffix}")
    return "; ".join(rendered) or "—"


def procurement_summary(station: dict[str, Any]) -> str:
    events = station["procurement"].get("events", [])
    planned = station["procurement"].get("planned", [])
    pieces: list[str] = []
    for event in events[-2:]:
        fy = unwrap(event.get("fiscal_year_be")) or "ปีไม่ระบุ"
        winner = unwrap(event.get("winner")) or "ไม่ระบุผู้ชนะ"
        amount = unwrap(event.get("award_or_contract_value_baht"))
        amount = amount if amount is not None else unwrap(event.get("contract_value_baht"))
        amount = amount if amount is not None else unwrap(event.get("amount_as_reported_baht"))
        contract = unwrap(event.get("contract_number"))
        text = f"{fy} {winner}"
        if amount is not None:
            text += f" {money(amount)}"
        if contract:
            text += f" ({contract})"
        pieces.append(text)
    for event in planned[-2:]:
        fy = unwrap(event.get("fiscal_year_be")) or unwrap(event.get("fiscal_years_be")) or "แผน"
        amount = unwrap(event.get("planned_amount_baht"))
        pieces.append(f"แผน {fy}{f' {money(amount)}' if amount is not None else ''}")
    return "; ".join(pieces) or "—"


def write_markdown(result: dict[str, Any], path: Path) -> None:
    stations = result["stations"]
    counts: dict[str, int] = {}
    for station in stations:
        agency = unwrap(station["agency"])
        counts[agency] = counts.get(agency, 0) + 1
    lines = [
        "# Radar station master — มองรวดเดียว", "",
        f"> สร้างจาก `data/radar_stations_map.json` และ corpora ที่ระบุใน JSON เมื่อ {unwrap(result['generated_on'])} ด้วย `scripts/build_station_master.py`; unknown = ยังไม่พบเอกสารยืนยัน", "",
        f"**{len(stations)} station records (mapped + official-list-only)** — " + ", ".join(f"{agency} {count}" for agency, count in counts.items()), "",
        "สถานีที่มีแถว map ซ้ำ (เช่น พิษณุโลก/พิมาย) ถูกรวมเป็นหนึ่ง record และเก็บชื่อเดิมไว้ใน `aliases`; รัศมีเป็นเพียง screening geometry ไม่ใช่ผลพิสูจน์ coverage จริง", "",
        "| สถานี | หน่วยงาน | พิกัด | รัศมีคัดกรอง | Band / DP / TMD official type | OEM / tier | สถานะ | ปฏิบัติการ 17–19 ก.ย. 69 | จัดซื้อ/แผนล่าสุด | source IDs |",
        "|---|---|---:|---:|---|---|---|---|---|---|",
    ]
    for station in stations:
        coords = station["coordinates"]
        lat, lon = unwrap(coords["lat"]), unwrap(coords["lon"])
        radar = station["radar"]
        band = unwrap(radar["band"])
        dp = unwrap(radar["dual_polarization"])
        dp_text = "ใช่" if dp is True else "ไม่ระบุ" if dp is None else "ไม่ใช่/ไม่ระบุ"
        official_type = unwrap(radar.get("official_tmd_type"))
        oem = unwrap(radar["oem_model"])
        tier = unwrap(radar["oem_tier"])
        oem_text = "—" if not oem else f"{oem} ({tier or 'ไม่ระบุ tier'})"
        display_source_ids = [source_id for source_id in unwrap(station["source_ids"]) if source_id not in {"S-UNKNOWN", "S-DERIVED"}]
        band_text = f"{band or '—'} / DP {dp_text}"
        if official_type:
            band_text += f" / TMD-list: {official_type}"
        values = [unwrap(station["name_th"]), unwrap(station["agency"]), f"{lat}, {lon}" if lat is not None and lon is not None else None, f"{unwrap(station['coverage']['screening_radius_km'])} km" if unwrap(station['coverage']['screening_radius_km']) is not None else None, band_text, oem_text, unwrap(station["status"]), unwrap(station.get("operational")), procurement_summary(station), ", ".join(display_source_ids)]
        lines.append("| " + " | ".join(markdown_escape(value) for value in values) + " |")
    lines.extend(["", "## Contract / bidder ledger", "", "ตารางนี้แสดงทุก procurement event ที่ผูกกับสถานี ไม่ใช่เฉพาะสองรายการล่าสุดในตารางด้านบน: `seller` คือผู้ขาย/ผู้รับสัญญาที่ระบุในหลักฐาน, `winner` คือผู้ชนะตามผลจัดซื้อ, `bidders` คือผู้ยื่นราคาที่เปิดเผย, และ `contract year` ใช้ปีงบประมาณ พ.ศ. ของ event; วันที่จริงอยู่ในช่อง contract date เมื่อเอกสารเปิดเผย", "", "| สถานี | หน่วยงาน | Contract year | กิจกรรม / band | Seller | Winner | Contract no. / date | Bidders | มูลค่าสัญญา/รางวัล | Project ID |", "|---|---|---:|---|---|---|---|---|---:|---|"])
    for station in stations:
        for event in station["procurement"].get("events", []):
            year = unwrap(event.get("contract_year_be")) or unwrap(event.get("fiscal_year_be"))
            activity = unwrap(event.get("activity_class")) or "—"
            band = unwrap(event.get("radar_band"))
            activity_text = f"{activity}{f' / {band}' if band else ''}"
            seller = unwrap(event.get("seller")) or "—"
            winner = unwrap(event.get("contract_winner")) or unwrap(event.get("winner")) or "—"
            number = unwrap(event.get("contract_number"))
            contract_date = unwrap(event.get("contract_date_be"))
            if isinstance(contract_date, list):
                contract_date = ", ".join(str(item) for item in contract_date) if contract_date else None
            contract_text = " / ".join(str(item) for item in (number, contract_date) if item not in (None, "")) or "—"
            amount = event_amount(event)
            project_id = unwrap(event.get("project_id"))
            values = [unwrap(station["name_th"]), unwrap(station["agency"]), year, activity_text, seller, winner, contract_text, bidder_summary(unwrap(event.get("contract_bidders"))), money(amount) if amount is not None else None, project_id]
            lines.append("| " + " | ".join(markdown_escape(value) for value in values) + " |")
    lines.extend(["", "## การอ่าน source IDs", "", "ทุกค่าใน JSON ใต้ `stations` และ `network_plans` มีรูป `{value, source}`; `source` เป็นหลักฐานที่ใช้รองรับค่านั้นโดยตรง ส่วน `S-DERIVED` หมายถึงค่าที่สคริปต์คำนวณจาก fields ที่อ้างแหล่งข้อมูลไว้แล้ว", "", "| ID | แหล่งข้อมูล | สถานะหลักฐาน |", "|---|---|---|"])
    for source_id, source in result["source_catalog"].items():
        locations = []
        for source_file in ([source["file"]] if source.get("file") else []) + source.get("files", []):
            locations.append(f"[`{source_file}`]({source_file})")
        for source_url in ([source["url"]] if source.get("url") else []) + source.get("urls", []):
            locations.append(f"[เว็บต้นทาง]({source_url})")
        location = "<br>".join(locations) or "—"
        lines.append(f"| `{source_id}` | {markdown_escape(source.get('label'))} — {location} | {markdown_escape(source.get('evidence_status'))} |")
    lines.extend(["", "## ขอบเขตสำคัญ", "", "- `สถานี` คือจุดจาก station map ที่รวมชื่อซ้ำแล้ว ไม่ใช่จำนวนเครื่องเรดาร์ทั้งหมด; แถว `official TMD list only` มาจากตารางสถานี/ชนิดเรดาร์ทางการที่ไม่พบแถวพิกัดใน map snapshot", "- `TMD-list` เป็นชนิดเรดาร์ตามเอกสารความรู้ทางการของ TMD ไม่ใช่ทะเบียนเครื่องหรือหลักฐานว่าเป็นเครื่องเดียวกับโครงการจัดซื้อภายหลัง", "- ใน `procurement.events[*]` มีฟิลด์ normalized สำหรับ join ข้ามหน่วยงาน: `contract_year_be`, `contract_number`, `contract_date_be`, `seller`, `contract_winner`, `contract_bidders`; ฟิลด์เดิม `winner` และ `submitted_bids` ยังเก็บไว้เพื่อ compatibility", "- เหตุการณ์ e-GP FY2569 แยก project ID และผล bidder รายสถานีแล้ว: **68099138641 = บึงกาฬ**, **68099247067 = กระบี่**", "- คำขอ RRD FY2570 มูลค่า 480 ล้านบาทถูกเก็บใต้ `planned` และไม่ถูกนับเป็น award/contract", "- TMD public menu ใช้ชื่อ feed `Phetchabun` กับหน้า `phb.php` ขณะที่ map ใช้ `วิเชียรบุรี`; เก็บเป็น quality flag จนกว่าจะมี official station-name crosswalk", "- ช่อง `ปฏิบัติการ 17–19 ก.ย. 69` มาจากการตรวจพอร์ทัลรอบเดียววันเดียว (`S-LIVE`) ไม่ใช่ uptime register; สถานีที่ไม่มีช่องนี้คือไม่มีสัญญาณรอบตรวจนั้น", "- ใน bidder rows `[P]` = ผ่านการพิจารณา `[N]` = ไม่ผ่านการพิจารณา ตามผล e-GP",
"- ระเบียน corpus ที่ไม่ผูกกับสถานีใด (งานระดับเครือข่าย รถเรดาร์เคลื่อนที่ หรือไม่ระบุสถานี) อยู่ใน `unmatched_events_audit` ของ JSON — ไม่มีการลงเงียบ", "- OEM ที่มาจาก dossier ถูกติด `Reported`; ต้องใช้ทะเบียนครุภัณฑ์, as-built และ service records เพื่อยืนยัน"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: inferred from this script)")
    args = parser.parse_args()
    root = args.root.resolve()
    result = build(root)
    json_path, md_path = root / "data/radar_station_master.json", root / "station_master.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, md_path)
    print(f"wrote {len(result['stations'])} stations to {json_path}")
    print(f"wrote glance table to {md_path}")


if __name__ == "__main__":
    main()
