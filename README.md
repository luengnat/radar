# Thai weather-radar procurement research

This workspace is an evidence ledger for examining weather-radar procurement
without treating a suspicious pattern as proof of misconduct.

## Working rule

- **Verified** means the claim is supported by a primary government document
  linked in the ledger.
- **Reported** means a credible secondary report or the supplied dossier makes
  the claim; obtain the originating document before repeating it as fact.
- **Unverified** means it is a research lead, not a conclusion.

## Scope

1. The FY 2569 four-station S-band procurement by the Thai Meteorological
   Department (TMD): Krabi, Bueng Kan, Chumphon, Phitsanulok — all four
   contracts and all four three-bid result sets verified (Genomatch 3,
   Marwin 1, total 1,647.8M). All four e-bidding document sets (TOR,
   announcement, bid document) are archived under `data/sources_egp/`:
   the TMD TOR names no brand and allows magnetron/klystron/solid-state
   transmitters at 750 kW, and all four reference prices are identical to
   the satang (446,166,666.66). In every tender the lowest-price bidder
   (AsiaMet twice, Scientific Research twice) failed qualification/
   technical consideration — the written reasons remain the top open
   document request.
2. The Royal Rainmaking Department pipeline: Phimai (480M, replacement of
   the 2555 METEOR 600S) and Udon Thani (480M, new station whose site is
   already covered by three operating radars), plus Rong Khwang (395M,
   specific/direct method) and the FY 2570 plan.
3. The recurring three-supplier pattern (Marwin → EEC, Genomatch →
   Leonardo/Gematronik, Scientific Research → EEC in RRD work) across
   10+ years of radar tenders. None proven exclusive.
4. The strongest current lead: identical quotation sets (480.0 / 486.3 /
   492.0M from the three firms, same date as the department's own forms,
   same totals across two projects with different scope mixes) used for
   budget/reference pricing at Phimai and Udon Thani.
5. Operational cross-checks against the two departments' live radar
   services (weather.tmd.go.th, file.royalrain.go.th) — station rosters
   reconcile; Krabi's old C-band has been out of service since 2019.
6. A newly reviewed TMD subcommittee budget PDF adds a domestic benchmark:
   one proposed fixed C-band radar with tower/buildings at Ang Thong is 210M,
   while two proposed mobile X-band radars total 160M. Its separate 480M
   Aviation Hub line is a multi-site aviation-weather integration package,
   not a single radar.

See [evidence-ledger.md](evidence-ledger.md) for the verified facts,
reported leads, the third-party audit-page reference, negative search
records, and the ranked document requests.

The fresh e-GP bidder/result snapshot is
[data/egp_sband_procure_results_api_2026-09-17.json](data/egp_sband_procure_results_api_2026-09-17.json);
the station-price reconciliation is
[data/egp_sband_reconciliation_2026-09-17.json](data/egp_sband_reconciliation_2026-09-17.json).
The final review and remaining evidence gaps are recorded in
[review_2026-09-17.md](review_2026-09-17.md).
The publication-ready factual summary (Thai, tier-tagged, ledger-row-cited) is
[summary_2026-09-17.md](summary_2026-09-17.md).
The station master table (band / OEM / procurement & construction dates / same-day
operational status per station, merged from all verified corpora) is
[station_master.md](station_master.md) built by
[scripts/build_station_master.py](scripts/build_station_master.py); the coverage-overlap
screen and map are [scripts/radar_coverage.py](scripts/radar_coverage.py) →
[data/radar_coverage_summary.json](data/radar_coverage_summary.json), and the
station↔e-GP award map regenerates via
[scripts/render_egp_map.py](scripts/render_egp_map.py) from
[data/station_egp_join.json](data/station_egp_join.json) — which now also carries the
verified FY 2563 C-band trio (Tak 63017151753 Marwin 147.553M; Ranong 63017153824 and
Trang 63017163547 Genomatch at an identical 146,985,900.00 each), the FY 2559
Chiang Rai + Surat Thani pair award (58096222967, Marwin 302.568M), and Sathing Phra
FY 2567 (Scientific Research 139.1M, 7.27% under its 150M budget) — all archived
portal winner notices in `data/sources_egp/`.
The station master also includes a complete contract/bidder ledger: fiscal year,
contract number/date, seller, normalized winner, all disclosed bidders and project
ID for each procurement event; missing contract fields remain explicit rather than
being inferred.
The station master also records the official TMD station/type table as a separate
field (not an as-built register), sourced from
[data/tmd_official_radar_station_list_2026-09-19.json](data/tmd_official_radar_station_list_2026-09-19.json).
หน้าเว็บมีแผนที่ SVG แบบ local จาก
[data/tha_adm0_simplified.geojson](data/tha_adm0_simplified.geojson)
และพิกัดใน station master; จุดสีแยกหน่วยงาน วงรอบใหญ่แสดงสถานะ `ตรวจเพิ่ม`
และสถานีที่ไม่มีพิกัดจะไม่ถูกวางตำแหน่งเดา.

หน้าเว็บมี fiscal-year lens สำหรับอ่านข้อมูลตามปีงบประมาณ: การ์ดสีส้มคือปีที่มี
procurement event/สัญญา ส่วนการ์ดสีฟ้าคือ plan/request ที่ยังไม่ใช่ award; dropdown
ปีจะกรองทั้ง station register และ procurement ledger. ปี 2570 ถูกทำเป็นจุดโฟกัส
ล่าสุดและแยกคำขอ/ร่าง TOR ของ RRD ออกจากผลจัดซื้อแล้ว — ใน master ปัจจุบันยังไม่มี
event/สัญญา FY2570 ที่ยืนยัน. แหล่งสำรวจงบภายนอกที่ผูกไว้ในหน้าเว็บคือ
[Budget Explorer พรรคประชาชน](http://budget-explorer.peoplesparty.or.th/)
และ [Thailand Open Budget: ร่างงบ 2570](https://openbudget.wevis.info/?budget_source=2570-draft-1)
ซึ่งใช้เป็นทางเข้าตรวจต่อ ไม่ใช่การแทนที่เอกสาร e-GP หรือสัญญา.
The price-reasonableness screening is in
[price_reasonableness_2026-09-17.md](price_reasonableness_2026-09-17.md).

หน้าเว็บมี risk triage แบบ rule-based เพื่อช่วยจัดลำดับการตรวจเอกสาร: `ตรวจเพิ่ม`
เมื่อพบสัญญาณ เช่น ผู้เสนอราคาต่ำสุดถูกระบุว่าไม่ผ่าน ราคากลางซ้ำหลายโครงการ
หรือวิธีเฉพาะเจาะจง; `เอกสารไม่พอ` เมื่อข้อมูลสัญญา/วันที่/เหตุผลยังขาด;
`ยังไม่ใช่สัญญา` สำหรับแผนหรือร่าง TOR; และ `ยังไม่พบสัญญาณเด่น` เมื่อไม่มี rule
ข้างต้นถูกกระตุ้นจาก master ปัจจุบัน สถานะเหล่านี้เป็นเครื่องมือคัดกรอง ไม่ใช่ข้อสรุป
การทุจริตหรือความผิดของบุคคล.

บริบทการเมืองของแต่ละปีงบประมาณ — รัฐบาล นายกรัฐมนตรี พรรคแกนนำ และรัฐมนตรี
ของ TMD/RRD — อยู่ใน
[data/political_context_2026-09-19.json](data/political_context_2026-09-19.json)
และถูกนำไปแสดงในหน้าเว็บเป็น context ของ event ไม่ใช่ข้อกล่าวหาว่าผู้ดำรงตำแหน่ง
มีส่วนเกี่ยวข้องกับการจัดซื้อโดยอัตโนมัติ; ปีที่คาบเกี่ยวการเปลี่ยนรัฐบาลควรตรวจวันสัญญา
รายรายการประกอบ.

The ThaiTH.AI dossier review is separated in
[thaith_radar_dossier_review_2026-09-17.md](thaith_radar_dossier_review_2026-09-17.md):
it covers the RRD FY2570 480M-per-station requests and should not be mixed
with the verified TMD FY2569 awards. The official Budget Bureau draft budget
source for the two RRD 480M lines is archived at
[data/sources_rrd/budget_draft_2570_agriculture_vol3_4.pdf](data/sources_rrd/budget_draft_2570_agriculture_vol3_4.pdf).
The user-supplied RRD source-document originals are also archived:
[Udon Thani/Mueang Mon](data/sources_rrd/rrd_fy2570_udon_radar_original.pdf)
and [Phimai/Rangka Yai](data/sources_rrd/rrd_fy2570_phimai_radar_original.pdf).
Their quotation pages 112–114 corroborate the repeated 480.0M / 486.3M /
492.0M totals and their TOR pages provide the primary-source basis for the
brand/specification lead; neither PDF is an award or final procurement result.

The international comparison set is recorded in
[data/international_radar_price_benchmarks_2026-09-17.json](data/international_radar_price_benchmarks_2026-09-17.json).

The additional TMD budget-explanation PDF and the review of its aviation,
fixed-radar, mobile-radar and AWOS proposals are recorded in
[tmd_budget_explanation_additional_review_2026-09-17.md](tmd_budget_explanation_additional_review_2026-09-17.md).
The archived source is
[data/sources_tmd/tmd_budget_explanation_subcommittee_additional_fy2570.pdf](data/sources_tmd/tmd_budget_explanation_subcommittee_additional_fy2570.pdf).
The scanned quotation pages are transcribed in
[data/tmd_additional_budget_quotations_2026-09-17.json](data/tmd_additional_budget_quotations_2026-09-17.json).

PBO-MCP GFMIS query results for the RRD radar history are archived at
[data/sources_pbo_rrd_budget_queries_2026-09-17.json](data/sources_pbo_rrd_budget_queries_2026-09-17.json).
The dataset covers FY2558–2568 only; zero matching rows are not evidence that
an item was never planned or appropriated, and it cannot validate FY2570 draft
budget lines.

Visual summary: [investigation infographic PNG](investigation_infographic_2026-09-17.png) and [editable SVG](investigation_infographic_2026-09-17.svg).

The reviewed four-station extraction snapshot is
[data/tmd_radar_awards_2026-09-15.json](data/tmd_radar_awards_2026-09-15.json).
The matching B0 tender-index extraction, including project IDs and comment
windows, is
[data/tmd_radar_tenders_2026-09-15.json](data/tmd_radar_tenders_2026-09-15.json).
The repeatable collector can read both the TMD winner (W0) and tender (B0)
indexes; use `--index tender` for the latter. It is
[scripts/extract_tmd_egp.py](scripts/extract_tmd_egp.py).

The historical pass is recorded in
[data/tmd_historical_radar_procurement_2555-2569.json](data/tmd_historical_radar_procurement_2555-2569.json).
It includes verified TMD contract-summary rows from 2555, 2556, 2559, 2560,
2561, 2562 and 2567, plus clearly labelled index and planning leads for older or unresolved
records. It also contains a separate `progress_records` section from TMD's FY
2568 performance report, including the Sathing Phra contract, advance payments,
delivery dates, and reported completion percentages. To inventory every TMD
index row mentioning radar, run:

```sh
python3 scripts/extract_tmd_egp.py --index winner --related
python3 scripts/extract_tmd_egp.py --index tender --related
```

The historical file separates core purchases, upgrades/repairs, and support.
This matters because a new radar with a tower cannot be compared directly to
an air-conditioner repair, spare part, UPS, or building-maintenance job.

The official Royal Rainmaking radar-station roster is recorded separately in
[data/rrd_radar_station_roster_2026-09-15.json](data/rrd_radar_station_roster_2026-09-15.json).
It is an asset/mission reference, not an award ledger. The file now includes a
verified historical snapshot from the RRD's 18 November 2564 knowledge page,
which listed 10 stations and classified Rong Khwang as mobile C-band; this is
kept as a historical roster difference, not treated as proof of a replacement
or reclassification event.

The first verified Royal Rainmaking historical procurement extract is in
[data/rrd_historical_radar_procurement_2566.json](data/rrd_historical_radar_procurement_2566.json).
It records the FY 2564 Rong Khwang radar contract, a FY 2565 first-installment
payment, and FY 2566 radar maintenance and spare-parts activities from
official reports. The reports identify separate Gematronik and EEC platform
spares. Supplier and award fields remain blank where the source does not name
them; the two conflicting official contract dates for Rong Khwang are retained
as a document-reconciliation issue. It also contains a separate
`planned_records` section for the official FY 2566–2570 radar plan; planned
amounts are not counted as completed procurements.
