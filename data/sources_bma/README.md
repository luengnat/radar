# BMA radar/budget source files

Source: the public Google Drive workspace shared with the investigation on
20 Sep 2026 (<https://drive.google.com/drive/folders/1RVC_vSVFcbgW2NMwwBroc3aowY1rChhT>),
a Bangkok Metropolitan Administration FY2570 budget-scrutiny collection:
`ร่างข้อบัญญัติ 70 งบประจำปี (pdf)` (per-bureau annexes of the draft BMA
annual-expenditure ordinance), `เอกสารประกอบการพิจารณา 70 งบประจำปี`
(deliberation volumes), `กมธ.ติดตามงบ` (council committee monitoring
meetings), plus provincial-budget folders (Chiang Mai, Samut Prakan) and a
PBO GFMIS xlsx set (2558–2568; same 22-column schema as the PBO-MCP).

| File | What it is |
| --- | --- |
| `bma_act70_70015_drainage.pdf` | Draft BMA Expenditure Ordinance B.E. 2570 annex, สำนักการระบายน้ำ (Drainage Bureau), 142 pp, text layer. Carries the BMA weather-radar maintenance program (BMA-01). |
| `bma_act70_70015_drainage.txt` | `pdftotext -layout` extraction of the above (OCR-mangled vowels as in source font; figures verified against the PDF). |
| `bma_consideration70_drainage_ocr.txt` | Full OCR (150 dpi, tesseract tha+eng) of the 239-page Drainage Bureau deliberation volume, with page markers. Source of BMA-02: the 4,326,000-baht X-band maintenance line (03299-5), the 1,180,800-baht radar-station security line (03275-1), and the network inventory's "ระบบตรวจอากาศด้วยเรดาร์ จำนวน ๒ แห่ง" (2 radar stations) on pp.209/218. |

Negatives checked the same day: the 70020 สำนักป้องกันและบรรเทาสาธารณภัย
(Disaster Prevention) ordinance annex contains no radar line; the two
626-page Disaster Prevention deliberation volumes were OCR-swept end-to-end
(10-agent chunked pass, fuzzy Thai variants + Latin controls) with ZERO
radar/weather content — they are firefighting-equipment files; the "OPEN SSO"
files are Social Security Office fund reports, unrelated to radar.

Deliberation volumes (scans, OCR-swept 20 Sep 2026, see ledger):
สำนักป้องกันและบรรเทาสาธารณภัย เล่ม 1–2 and สำนักการระบายน้ำ. Retained in
`tmp_drive/` during analysis; excerpts that support ledger rows are copied
here with page citations.

These are draft-budget and deliberation documents: they evidence budget
lines and project framing, not enactment, awards, suppliers, or contract
execution.
