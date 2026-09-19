# RRD FY2570 radar source files

These are copies of the two scanned PDFs supplied through the investigation's
Google Drive folder on 17 September 2569. Each file has 114 pages.

| File | Scope | SHA-256 |
| --- | --- | --- |
| `rrd_fy2570_udon_radar_original.pdf` | Fixed S-band dual-polarization radar, Mueang Mon, Udon Thani | `d6a7c754c1e546c75df170999855bba633b625f8c8d95b25407a39a5d8a88e3a` |
| `rrd_fy2570_phimai_radar_original.pdf` | Fixed S-band dual-polarization radar, Rangka Yai, Phimai | `44ce6c8c8904f537dc4293551683089e757f7efecacc5aa2a8461473cae80fbf` |

The quotation pages are printed pages 112–114. The inspected TOR page 4 in
both files shows the `LEONARDO/Gematronik` brand line and the 850-kW magnetron
specification. Udon printed page 31 was also inspected for the 480M budget,
15% advance payment, 840-day delivery, and two-year warranty.

A full OCR pass of the six quotation pages plus the loose scan is archived at
`rrd_fy2570_quotation_pages_ocr_2026-09-19.txt` (pdftoppm 200 dpi →
tesseract tha+eng). It records the per-site quotation reference numbers:
Genomatch GMOQ-6906002 (Phimai) / GMOQ-6906003 (Udon) and Marwin
MT2606003-OQ (Udon) / MT2606004-OQ (Phimai).

`udon_genomatch_quotation_gmoq6906003_scan.jpg` is a portrait scan of the
Udon Genomatch quotation letter (ref GMOQ-6906003, 480,000,000 baht,
62,215,600-baht included-scope note, 19 June 2569) that was found unlabeled
in the workspace on 19 Sep 2026 and identified against the Udon volume's
printed page 112. It is another copy of an already-archived document, not an
independent source.

Source folder: <https://drive.google.com/drive/folders/170o8gB5Snc-Y96KNaNf5N4cpxSkLoFUn>

These source files are documentary evidence for quotations and draft/TOR
observations. They are not, by themselves, proof of an award, final contract,
technical compliance, price reasonableness, or coordination among bidders.

The public maintenance-plan API snapshot is archived at
`rrd_instrument_maintenance_api_2026-09-17.json`. It returned four records,
all for Omkoi, on 17 September 2569. This should be read as a snapshot of the
public API response, not as a complete maintenance or availability register.

The date-specific readiness API snapshot for 17 September 2567 is archived at
`rrd_instrument_readiness_radar_extract_2024-09-17.json`. It contains the 12
radar rows from the 36-record response: 9 marked usable and 3 unusable. The
API returned no data for the equivalent 2569 dates checked.

PBO-MCP budget-query results are stored separately in
`../sources_pbo_rrd_budget_queries_2026-09-17.json`; they are GFMIS
disbursement queries, not RRD source documents.
