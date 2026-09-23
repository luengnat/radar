# Radar station master — มองรวดเดียว

> สร้างจาก `data/radar_stations_map.json` และ corpora ที่ระบุใน JSON เมื่อ 2026-09-23 ด้วย `scripts/build_station_master.py`; unknown = ยังไม่พบเอกสารยืนยัน

**43 station records (mapped + official-list-only)** — TMD 29, RRD 12, BMA 2

สถานีที่มีแถว map ซ้ำ (เช่น พิษณุโลก/พิมาย) ถูกรวมเป็นหนึ่ง record และเก็บชื่อเดิมไว้ใน `aliases`; รัศมีเป็นเพียง screening geometry ไม่ใช่ผลพิสูจน์ coverage จริง

| สถานี | หน่วยงาน | พิกัด | รัศมีคัดกรอง | Band / DP / TMD official type | OEM / tier | สถานะ | ปฏิบัติการ 17–19 ก.ย. 69 | จัดซื้อ/แผนล่าสุด | source IDs |
|---|---|---:|---:|---|---|---|---|---|---|
| ขอนแก่น | TMD | 16.46, 102.79 | 240 km | — / DP ไม่ระบุ / TMD-list: Dual Polarization | — | existing | Current image in agency feed sweep | — | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-LIVE |
| สกลนคร | TMD | 17.16, 104.13 | 240 km | C / DP ใช่ / TMD-list: Dual Polarization | EEC DWSR-3501C-SPD (Reported (dossier registry)) | existing | Current image in agency feed sweep | 2556 Marwin Technologies Co., Ltd. 308,994,600 บาท (สข.83/2556) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-OEM-REPORTED, S-LIVE |
| อุบลราชธานี | TMD | 15.25, 104.87 | 240 km | C / DP ใช่ / TMD-list: Dual Polarization | EEC (dossier registry) (Reported (dossier registry)) | existing | Current image in agency feed sweep | 2567 Marwin Technologies Co., Ltd. 44,292,500 บาท (สข.148/2567) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-OEM-REPORTED, S-LIVE |
| พิษณุโลก | TMD | 16.78, 100.28 | 240 km | S-band dual-polarization / DP ใช่ / TMD-list: Dual Polarization | — | existing + new FY2568 project | Current image in agency feed sweep | 2569 บริษัท มาร์วิน เทคโนโลยีส์ จำกัด 408,954,000 บาท | S-MAP, S-EGP-TOR, S-TMD-KNOWLEDGE, S-EGP, S-TMD-AWARD, S-LIVE |
| เชียงราย | TMD | 19.95, 99.88 | 240 km | Doppler / DP ไม่ระบุ / TMD-list: Dual Polarization | — | existing | Current image in agency feed sweep | 2559 Marwin Technologies Co., Ltd. 302,568,000 บาท (สข.75/2559) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| ลำพูน | TMD | 18.57, 99.03 | 240 km | C / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2559 Marwin Technologies Co., Ltd. 4,815,000 บาท (สจ.63/2559); 2561 Scientific Research Limited Partnership 86,670,000 บาท (สข.71/2561) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| สุราษฎร์ธานี | TMD | 9.13, 99.15 | 240 km | S / DP ไม่ระบุ / TMD-list: S-Band | — | existing | Current image in agency feed sweep | 2559 Marwin Technologies Co., Ltd. 302,568,000 บาท (สข.75/2559) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| ภูเก็ต | TMD | 8.11, 98.32 | 240 km | C / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2561 Scientific Research Limited Partnership 86,670,000 บาท (สข.71/2561) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| สงขลา | TMD | 7.18, 100.61 | 240 km | — / DP ไม่ระบุ | — | existing | Current image in agency feed sweep | — | S-MAP, S-LIVE |
| ชัยนาท | TMD | 15.15, 100.17 | 240 km | — / DP ไม่ระบุ / TMD-list: Dual Polarization | — | existing | Current image in agency feed sweep | 2559 C & K Power Gen Co., Ltd. 208,650 บาท (สจ.135/2559) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| ระยอง | TMD | 12.68, 101.27 | 240 km | C / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2562 Scientific Research Limited Partnership 43,174,500 บาท (สข.79/2562); 2567 Genomatch Co., Ltd. 47,193,600 บาท (สข.159/2567) | S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| หัวหิน | TMD | 12.57, 99.95 | 240 km | C / DP ไม่ระบุ / TMD-list: S-Band | SELEX ES METEOR 735C (Reported (dossier registry)) | existing | Current image in agency feed sweep | — | S-MAP, S-TMD-KNOWLEDGE, S-OEM-REPORTED, S-LIVE |
| อมก๋อย | RRD | 17.79, 98.36 | 240 km | S / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | — | S-MAP, S-OEM-REPORTED, S-GFMIS, S-LIVE |
| ตาคลี | RRD | 15.26, 100.34 | 240 km | S / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | — | S-MAP, S-OEM-REPORTED, S-LIVE |
| สัตหีบ | RRD | 12.68, 100.98 | 240 km | S / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | แผน 2567 230,000,000 บาท | S-MAP, S-OEM-REPORTED, S-RRD-HIST, S-GFMIS, S-LIVE |
| พนม | RRD | 8.86, 98.77 | 240 km | S / DP ไม่ระบุ | — | existing | API returned no data this pass; not proof of outage | แผน 2569 240,000,000 บาท | S-MAP, S-OEM-REPORTED, S-RRD-HIST, S-LIVE |
| ร้องกวาง | RRD | 18.34, 100.32 | 150 km | S / DP ใช่ | Gematronik line (dossier) (Reported (dossier registry)) | existing | CAPPI frame same day (17 Sep 2026) | 2564 Genomatch Co., Ltd. 394,295,000 บาท (คภ./ฝล.37/2564) | S-MAP, S-RRD-HIST, S-OEM-REPORTED, S-GFMIS, S-LIVE |
| บ้านผือ | RRD | 17.68, 102.47 | 150 km | C (5.6 GHz mobile) / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | แผน 2567 460,000,000 บาท | S-MAP, S-RRD-ROSTER, S-RRD-HIST, S-LIVE |
| ราษีไศล | RRD | 15.34, 104.15 | 150 km | C (5.6 GHz mobile) / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | แผน 2570 475,000,000 บาท | S-MAP, S-RRD-ROSTER, S-RRD-HIST, S-LIVE |
| ปะทิว | RRD | 10.7, 99.25 | 150 km | C (5.6 GHz mobile) / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | — | S-MAP, S-RRD-ROSTER, S-LIVE |
| สิงหนคร | RRD | 7.23, 100.56 | 150 km | C (5.6 GHz mobile) / DP ไม่ระบุ | — | existing | CAPPI frame same day (17 Sep 2026) | — | S-MAP, S-RRD-CAPPI, S-RRD-ROSTER, S-LIVE |
| หาดใหญ่ | RRD | 6.97, 100.53 | 240 km | S dual-pol / DP ไม่ระบุ | — | new FY2567 project | — | แผน 2567 460,000,000 บาท | S-GFMIS, S-MAP, S-RRD-HIST |
| กระบี่ | TMD | 8.06, 98.96 | 240 km | S-band dual-polarization / DP ใช่ / TMD-list: C-Band | — | new FY2568 project | Out-of-Service placeholder served since 2019 | 2569 บริษัท จีโนแมทช์ จำกัด 412,699,000 บาท (สข.39/2569) | S-EGP-TOR, S-MAP, S-TMD-KNOWLEDGE, S-EGP, S-TMD-AWARD, S-LIVE |
| ชุมพร | TMD | 10.49, 99.18 | 240 km | S-band dual-polarization / DP ใช่ / TMD-list: C-Band | — | new FY2568 project | — | 2562 Scientific Research Limited Partnership 43,121,500 บาท (สข.80/2562); 2569 บริษัท จีโนแมทช์ จำกัด 410,987,000 บาท | S-EGP-TOR, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-EGP, S-TMD-AWARD |
| บึงกาฬ | TMD | 18.36, 103.65 | 240 km | S-band dual-polarization / DP ใช่ | — | new FY2568 project | — | 2569 บริษัท จีโนแมทช์ จำกัด 415,160,000 บาท (สข.40/2569) | S-EGP-TOR, S-MAP, S-EGP, S-TMD-AWARD |
| อุดรธานี | RRD | 17.45, 102.78 | 240 km | S-band dual-polarization / DP ใช่ | — | FY2570 request | — | แผน 2570 480,000,000 บาท | S-MAP, S-RRD-FY2570 |
| พิมาย | RRD | 15.22, 102.49 | 240 km | S / DP ใช่ | METEOR 600S (Reported (dossier registry)) | existing + FY2570 request | CAPPI frame same day (17 Sep 2026) | แผน 2568 235,000,000 บาท; แผน 2570 480,000,000 บาท | S-MAP, S-RRD-ROSTER, S-RRD-FY2570, S-OEM-REPORTED, S-RRD-HIST, S-LIVE |
| น่าน | TMD | 18.78, 100.78 | 240 km | C / DP ไม่ระบุ / TMD-list: Dual Polarization | EEC (dossier registry) (Reported (dossier registry)) | existing | Current image in agency feed sweep | — | S-TMD-FEED, S-MAP, S-TMD-KNOWLEDGE, S-OEM-REPORTED, S-LIVE |
| แม่ฮ่องสอน | TMD | 19.3, 97.97 | 240 km | X / DP ไม่ระบุ / TMD-list: X-Band | — | existing | Current image in agency feed sweep | — | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-LIVE |
| ตาก | TMD | 16.75, 98.7 | 240 km | C dual-pol / DP ใช่ | — | existing | Current image in agency feed sweep | 2563 Marwin Technologies Co., Ltd. 147,553,000 บาท | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-HIST, S-STATION-JOIN, S-LIVE |
| วิเชียรบุรี | TMD | 15.66, 101.1 | 240 km | C / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2562 Scientific Research Limited Partnership 43,174,500 บาท (สข.85/2562); 2567 ไม่ระบุผู้ชนะ 44,163,800 บาท (สข.142/2567) | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| สุรินทร์ | TMD | 14.88, 103.42 | 240 km | C / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2567 Marwin Technologies Co., Ltd. 138,565,000 บาท (สข.168/2567) | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| นครนายก | TMD | 14.1, 101.2 | 240 km | C / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2562 Scientific Research Limited Partnership 59,385,000 บาท (สข.84/2562); 2567 Scientific Research Limited Partnership 57,988,500 บาท (สข.145/2567) | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| สมุทรสงคราม | TMD | 13.41, 100.0 | 240 km | — / DP ไม่ระบุ / TMD-list: Dual Polarization | — | existing | Current image in agency feed sweep | — | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-LIVE |
| สุวรรณภูมิ | TMD | 13.68, 100.75 | 240 km | S / DP ไม่ระบุ / TMD-list: S-Band | EEC DWSR-8501S-9 (Reported (dossier registry)) | existing | Current image in agency feed sweep | 2567 Marwin Technologies Co., Ltd. 62,589,500 บาท (สข.147/2567); 2570 Marwin Technologies Co., Ltd. 31,200,000 บาท | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-OEM-REPORTED, S-TMD-HIST, S-LIVE |
| ระนอง | TMD | 9.94, 98.62 | 240 km | C dual-pol / DP ใช่ / TMD-list: X-Band | — | existing | Current image in agency feed sweep | 2563 Genomatch Co., Ltd. 146,985,900 บาท | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-STATION-JOIN, S-LIVE |
| ตรัง | TMD | 7.55, 99.61 | 240 km | C dual-pol / DP ใช่ / TMD-list: X-Band | — | existing | Current image in agency feed sweep | 2563 Genomatch Co., Ltd. 146,985,900 บาท | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-STATION-JOIN, S-LIVE |
| สทิงพระ | TMD | 7.22, 100.1 | 240 km | C dual-pol / DP ใช่ / TMD-list: C-Band | — | existing | Current image in agency feed sweep | 2567 Scientific Research Limited Partnership 139,100,000 บาท (สข.133/2567) | S-TMD-FEED, S-MAP, S-TMD-WEATHER, S-TMD-KNOWLEDGE, S-TMD-HIST, S-LIVE |
| หนองจอก | BMA | 13.83, 100.82 | 120 km | — / DP ไม่ระบุ | — | existing | — | — | S-TMD-FEED, S-MAP |
| หนองแขม | BMA | 13.7, 100.4 | 120 km | — / DP ไม่ระบุ | — | existing | — | — | S-TMD-FEED, S-MAP |
| สมุย | TMD | 9.47, 100.06 | 240 km | C / DP ไม่ระบุ / TMD-list: C-Band | — | existing | Feed page exists; image returned 404 on 19 Sep 2026 — not proof of outage | — | S-TMD-KNOWLEDGE, S-MAP, S-LIVE |
| หาดใหญ่ | TMD | 7.09, 100.6 | 240 km | C / DP ไม่ระบุ / TMD-list: C-Band | — | existing | Current image verified 19 Sep 2026 (feed added with the official-list pass) | — | S-TMD-KNOWLEDGE, S-MAP, S-TMD-WEATHER, S-LIVE |
| นราธิวาส | TMD | — | — | C / DP ใช่ / TMD-list: Dual Polarization | EEC DWSR-3501C-SPD (ถูกแทนที่ 2567) (Reported (dossier registry)) | official TMD list only | — | 2556 Marwin Technologies Co., Ltd. 308,994,600 บาท (สข.83/2556); 2567 Marwin Technologies Co., Ltd. 141,775,000 บาท (สข.167/2567) | S-TMD-KNOWLEDGE, S-MAP, S-TMD-WEATHER, S-TMD-HIST, S-OEM-REPORTED |

## Contract / bidder ledger

ตารางนี้แสดงทุก procurement event ที่ผูกกับสถานี ไม่ใช่เฉพาะสองรายการล่าสุดในตารางด้านบน: `seller` คือผู้ขาย/ผู้รับสัญญาที่ระบุในหลักฐาน, `winner` คือผู้ชนะตามผลจัดซื้อ, `bidders` คือผู้ยื่นราคาที่เปิดเผย, และ `contract year` ใช้ปีงบประมาณ พ.ศ. ของ event; วันที่จริงอยู่ในช่อง contract date เมื่อเอกสารเปิดเผย

| สถานี | หน่วยงาน | Contract year | กิจกรรม / band | Seller | Winner | Contract no. / date | Bidders | มูลค่าสัญญา/รางวัล | Project ID |
|---|---|---:|---|---|---|---|---|---:|---|
| สกลนคร | TMD | 2556 | core_purchase | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.83/2556 / 11 April 2556 | Marwin Technologies Co., Ltd. 308,994,600 บาท; Scientific Research Limited Partnership 310,380,000 บาท; Genomatch Co., Ltd. 309,872,000 บาท | 308,994,600 บาท | — |
| อุบลราชธานี | TMD | 2567 | upgrade_or_repair / C-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.148/2567 / 16 August 2567 | — | 44,292,500 บาท | 67059024156 |
| พิษณุโลก | TMD | 2569 | new_radar_purchase / S-band dual-polarization | บริษัท มาร์วิน เทคโนโลยีส์ จำกัด | บริษัท มาร์วิน เทคโนโลยีส์ จำกัด | — | บริษัท จีโนแมทช์ จำกัด 410,987,000 บาท [P]; บริษัท มาร์วิน เทคโนโลยีส์ จำกัด 408,954,000 บาท [P]; บริษัท เอเซียเมท จำกัด 389,480,000 บาท [N] | 408,954,000 บาท | 68099138724 |
| เชียงราย | TMD | 2559 | core_purchase / Doppler | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.75/2559 / 12 February 2559 | Marwin Technologies Co., Ltd. 302,568,000 บาท; Genomatch Co., Ltd. 306,880,000 บาท; Scientific Research Limited Partnership 304,900,000 บาท | 302,568,000 บาท | 58096222967 |
| ลำพูน | TMD | 2559 | spare_parts | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สจ.63/2559 / 26 January 2559 | — | 4,815,000 บาท | — |
| ลำพูน | TMD | 2561 | upgrade_or_repair | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.71/2561 / 16 January 2561 | Scientific Research Limited Partnership 86,670,000 บาท; Genomatch Co., Ltd. 88,596,000 บาท; Marwin Technologies Co., Ltd. 89,238,000 บาท | 86,670,000 บาท | — |
| สุราษฎร์ธานี | TMD | 2559 | core_purchase / Doppler | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.75/2559 / 12 February 2559 | Marwin Technologies Co., Ltd. 302,568,000 บาท; Genomatch Co., Ltd. 306,880,000 บาท; Scientific Research Limited Partnership 304,900,000 บาท | 302,568,000 บาท | 58096222967 |
| ภูเก็ต | TMD | 2561 | upgrade_or_repair | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.71/2561 / 16 January 2561 | Scientific Research Limited Partnership 86,670,000 บาท; Genomatch Co., Ltd. 88,596,000 บาท; Marwin Technologies Co., Ltd. 89,238,000 บาท | 86,670,000 บาท | — |
| ชัยนาท | TMD | 2559 | support_or_maintenance | C & K Power Gen Co., Ltd. | C & K Power Gen Co., Ltd. | สจ.135/2559 / 28 September 2559 | — | 208,650 บาท | — |
| ระยอง | TMD | 2559 | support_or_maintenance | C & K Power Gen Co., Ltd. | C & K Power Gen Co., Ltd. | สจ.135/2559 / 28 September 2559 | — | 208,650 บาท | — |
| ระยอง | TMD | 2562 | upgrade_or_repair | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.79/2562 / 21 January 2562 | Scientific Research Limited Partnership 43,174,500 บาท | 43,174,500 บาท | — |
| ระยอง | TMD | 2567 | upgrade_or_repair / C-band | Genomatch Co., Ltd. | Genomatch Co., Ltd. | สข.159/2567 / 30 August 2567 | — | 47,193,600 บาท | 67059309257 |
| ร้องกวาง | RRD | 2564 | new_radar_purchase / S-band | Genomatch Co., Ltd. | Genomatch Co., Ltd. | คภ./ฝล.37/2564 / 2 สิงหาคม 2564, 27 สิงหาคม 2564 | — | 394,295,000 บาท | — |
| กระบี่ | TMD | 2569 | new_radar_purchase / S-band dual-polarization | บริษัท จีโนแมทช์ จำกัด | บริษัท จีโนแมทช์ จำกัด | สข.39/2569 / 09/01/2569 | บริษัท จีโนแมทช์ จำกัด 412,699,000 บาท [P]; บริษัท มาร์วิน เทคโนโลยีส์ จำกัด 414,625,000 บาท [P]; ห้างหุ้นส่วนจำกัด ไซแอนติฟิค รีเสิร์ช 375,570,000 บาท [N] | 412,699,000 บาท | 68099247067 |
| ชุมพร | TMD | 2562 | upgrade_or_repair | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.80/2562 / 18 January 2562 | Scientific Research Limited Partnership 43,121,500 บาท | 43,121,500 บาท | — |
| ชุมพร | TMD | 2569 | new_radar_purchase / S-band dual-polarization | บริษัท จีโนแมทช์ จำกัด | บริษัท จีโนแมทช์ จำกัด | — | บริษัท จีโนแมทช์ จำกัด 410,987,000 บาท [P]; บริษัท มาร์วิน เทคโนโลยีส์ จำกัด 412,142,600 บาท [P]; บริษัท เอเซียเมท จำกัด 391,620,000 บาท [N] | 410,987,000 บาท | 68099138543 |
| บึงกาฬ | TMD | 2569 | new_radar_purchase / S-band dual-polarization | บริษัท จีโนแมทช์ จำกัด | บริษัท จีโนแมทช์ จำกัด | สข.40/2569 / 09/01/2569 | บริษัท จีโนแมทช์ จำกัด 415,160,000 บาท [P]; บริษัท มาร์วิน เทคโนโลยีส์ จำกัด 419,440,000 บาท [P]; ห้างหุ้นส่วนจำกัด ไซแอนติฟิค รีเสิร์ช 375,570,000 บาท [N] | 415,160,000 บาท | 68099138641 |
| ตาก | TMD | 2563 | core_purchase / C-band dual-polarization | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | — | — | 147,553,000 บาท | 63017151753 |
| วิเชียรบุรี | TMD | 2562 | upgrade_or_repair | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.85/2562 / 25 January 2562 | — | 43,174,500 บาท | — |
| วิเชียรบุรี | TMD | 2567 | upgrade_or_repair / C-band | — | — | สข.142/2567 / 13 August 2567 | — | 44,163,800 บาท | 67059026010 |
| สุรินทร์ | TMD | 2567 | core_purchase / C-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.168/2567 / 10 September 2567 | — | 138,565,000 บาท | 67039615683 |
| นครนายก | TMD | 2562 | upgrade_or_repair / C-band | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.84/2562 / 25 January 2562 | — | 59,385,000 บาท | — |
| นครนายก | TMD | 2567 | upgrade_or_repair / C-band | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.145/2567 / 14 August 2567 | — | 57,988,500 บาท | 67059024371 |
| สุวรรณภูมิ | TMD | 2555 | support_or_maintenance / S-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | 71/2555 / 31 May 2555 | — | 2,889,000 บาท | — |
| สุวรรณภูมิ | TMD | 2559 | support_or_maintenance / S-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สจ.116/2559 / 29 July 2559 | — | 2,889,000 บาท | — |
| สุวรรณภูมิ | TMD | 2560 | support_or_maintenance / S-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สจ.14/2560 / 17 October 2559 | Marwin Technologies Co., Ltd. 17,333,000 บาท | 17,333,000 บาท | — |
| สุวรรณภูมิ | TMD | 2561 | core_purchase / S-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.70/2561 / 12 January 2561 | Marwin Technologies Co., Ltd. 304,950,000 บาท; Scientific Research Limited Partnership 308,748,500 บาท; Genomatch Co., Ltd. 310,621,000 บาท | 304,950,000 บาท | — |
| สุวรรณภูมิ | TMD | 2563 | maintenance / S-band Doppler | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | — | — | 8,667,000 บาท | 62097300070 |
| สุวรรณภูมิ | TMD | 2565 | maintenance / S-band Doppler | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | — | — | 5,243,000 บาท | 65027031796 |
| สุวรรณภูมิ | TMD | 2567 | upgrade_or_repair / S-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.147/2567 / 16 August 2567 | — | 62,589,500 บาท | 67049456830 |
| สุวรรณภูมิ | TMD | 2570 | maintenance / S-band Doppler | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | — | — | 31,200,000 บาท | — |
| ระนอง | TMD | 2563 | core_purchase / C-band dual-polarization | Genomatch Co., Ltd. | Genomatch Co., Ltd. | — | — | 146,985,900 บาท | 63017153824 |
| ตรัง | TMD | 2563 | core_purchase / C-band dual-polarization | Genomatch Co., Ltd. | Genomatch Co., Ltd. | — | — | 146,985,900 บาท | 63017163547 |
| สทิงพระ | TMD | 2567 | core_purchase / C-band dual-polarization | Scientific Research Limited Partnership | Scientific Research Limited Partnership | สข.133/2567 / 17 July 2567 | — | 139,100,000 บาท | — |
| นราธิวาส | TMD | 2556 | core_purchase | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.83/2556 / 11 April 2556 | Marwin Technologies Co., Ltd. 308,994,600 บาท; Scientific Research Limited Partnership 310,380,000 บาท; Genomatch Co., Ltd. 309,872,000 บาท | 308,994,600 บาท | — |
| นราธิวาส | TMD | 2567 | core_purchase / C-band | Marwin Technologies Co., Ltd. | Marwin Technologies Co., Ltd. | สข.167/2567 / 10 September 2567 | — | 141,775,000 บาท | 67049316538 |

## การอ่าน source IDs

ทุกค่าใน JSON ใต้ `stations` และ `network_plans` มีรูป `{value, source}`; `source` เป็นหลักฐานที่ใช้รองรับค่านั้นโดยตรง ส่วน `S-DERIVED` หมายถึงค่าที่สคริปต์คำนวณจาก fields ที่อ้างแหล่งข้อมูลไว้แล้ว

| ID | แหล่งข้อมูล | สถานะหลักฐาน |
|---|---|---|
| `S-BUILD` | This generator and deterministic transformations — [`scripts/build_station_master.py`](scripts/build_station_master.py) | Derived |
| `S-MAP` | Base station map: name, agency, approximate coordinates, radius and status — [`data/radar_stations_map.json`](data/radar_stations_map.json)<br>[เว็บต้นทาง](https://open.thaith.ai/radar/) | Mixed input; retain row note in locator |
| `S-TMD-FEED` | TMD public radar-feed roster and feed/index leads — [`data/radar_stations_map.json`](data/radar_stations_map.json)<br>[เว็บต้นทาง](https://weather.tmd.go.th/paipibat/) | Public roster / lead |
| `S-TMD-WEATHER` | TMD public weather-radar homepage and product menu — [เว็บต้นทาง](https://weather.tmd.go.th/)<br>[เว็บต้นทาง](https://weather.tmd.go.th/phb.php) | Verified public service listing; labels/products are not an equipment register |
| `S-TMD-KNOWLEDGE` | TMD official station/type table — [`data/tmd_official_radar_station_list_2026-09-19.json`](data/tmd_official_radar_station_list_2026-09-19.json)<br>[เว็บต้นทาง](https://ubonmet.tmd.go.th/files/KM-base/R-3.pdf) | Verified official station/type list; not an as-built asset register |
| `S-RRD-ROSTER` | Royal Rainmaking official station roster — [`data/rrd_radar_station_roster_2026-09-15.json`](data/rrd_radar_station_roster_2026-09-15.json)<br>[เว็บต้นทาง](https://www.royalrain.go.th/royalrain/Editor_Page.aspx?MenuId=43) | Verified roster |
| `S-RRD-CAPPI` | RRD official public CAPPI page for Singhanakhon mobile station — [เว็บต้นทาง](https://file.royalrain.go.th/opendata/radar_data/cappi/?station=singha) | Verified public station page; page does not state band or model |
| `S-TMD-HIST` | TMD verified historical procurement corpus — [`data/tmd_historical_radar_procurement_2555-2569.json`](data/tmd_historical_radar_procurement_2555-2569.json) | Verified records; locator URL per event |
| `S-RRD-HIST` | RRD verified historical procurement and five-year plan corpus — [`data/rrd_historical_radar_procurement_2566.json`](data/rrd_historical_radar_procurement_2566.json) | Verified records / verified plan; locator URL per event |
| `S-RRD-FY2570` | User-supplied RRD FY2570 request originals and budget draft — [`data/sources_rrd/rrd_fy2570_udon_radar_original.pdf`](data/sources_rrd/rrd_fy2570_udon_radar_original.pdf)<br>[`data/sources_rrd/rrd_fy2570_phimai_radar_original.pdf`](data/sources_rrd/rrd_fy2570_phimai_radar_original.pdf)<br>[`data/sources_rrd/budget_draft_2570_agriculture_vol3_4.pdf`](data/sources_rrd/budget_draft_2570_agriculture_vol3_4.pdf)<br>[เว็บต้นทาง](https://drive.google.com/drive/folders/170o8gB5Snc-Y96KNaNf5N4cpxSkLoFUn) | Request / draft; not an award |
| `S-GFMIS` | GFMIS/PBO disbursement and payment trail — [`data/gfmis_radar_disbursements_2026-09-17.json`](data/gfmis_radar_disbursements_2026-09-17.json)<br>[เว็บต้นทาง](https://pbo-mcp.thaith.ai/manual) | Verified query / reconciliation |
| `S-EGP` | Project-specific e-GP bidder and award results — [`data/egp_sband_procure_results_api_2026-09-17.json`](data/egp_sband_procure_results_api_2026-09-17.json)<br>[`data/egp_sband_reconciliation_2026-09-17.json`](data/egp_sband_reconciliation_2026-09-17.json)<br>[`data/egp_sband_bidder_lists_2026-09-15.json`](data/egp_sband_bidder_lists_2026-09-15.json)<br>[เว็บต้นทาง](https://www.gprocurement.go.th/) | Verified snapshot |
| `S-EGP-TOR` | TMD FY2569 S-band TOR and reference-price archive — [`data/tmd_sband_tor_specs_2568.json`](data/tmd_sband_tor_specs_2568.json)<br>[เว็บต้นทาง](https://tmd.go.th/Procurement/ProcurementAnnoucementPage?ProcurementTypeCode=B0) | Verified archive / extracted text |
| `S-TMD-AWARD` | TMD FY2569 monthly award/contract summaries — [`data/tmd_radar_awards_2026-09-15.json`](data/tmd_radar_awards_2026-09-15.json) | Verified official summary |
| `S-STATION-JOIN` | Station-to-e-GP join and historical index leads — [`data/station_egp_join.json`](data/station_egp_join.json) | Verified join for project IDs; index leads remain leads |
| `S-OEM-REPORTED` | OEM/model registry claims recorded in the dossier — [`data/oem_compliance_matrix_2026-09-17.json`](data/oem_compliance_matrix_2026-09-17.json)<br>[เว็บต้นทาง](https://open.thaith.ai/radar/) | Reported; not a substitute for as-built records |
| `S-LIVE` | Same-day operational liveness sweep of the public radar portals — [`data/radar_liveness_2026-09-17.json`](data/radar_liveness_2026-09-17.json)<br>[เว็บต้นทาง](https://weather.tmd.go.th/) | Verified single-day portal check; not an uptime register |
| `S-UNKNOWN` | The reviewed sources do not state this field — — | Unknown / disclosure gap |
| `S-DERIVED` | Derived by this script from cited input fields — [`scripts/build_station_master.py`](scripts/build_station_master.py) | Derived; not an independent source |

## ขอบเขตสำคัญ

- `สถานี` คือจุดจาก station map ที่รวมชื่อซ้ำแล้ว ไม่ใช่จำนวนเครื่องเรดาร์ทั้งหมด; แถว `official TMD list only` มาจากตารางสถานี/ชนิดเรดาร์ทางการที่ไม่พบแถวพิกัดใน map snapshot
- `TMD-list` เป็นชนิดเรดาร์ตามเอกสารความรู้ทางการของ TMD ไม่ใช่ทะเบียนเครื่องหรือหลักฐานว่าเป็นเครื่องเดียวกับโครงการจัดซื้อภายหลัง
- ใน `procurement.events[*]` มีฟิลด์ normalized สำหรับ join ข้ามหน่วยงาน: `contract_year_be`, `contract_number`, `contract_date_be`, `seller`, `contract_winner`, `contract_bidders`; ฟิลด์เดิม `winner` และ `submitted_bids` ยังเก็บไว้เพื่อ compatibility
- เหตุการณ์ e-GP FY2569 แยก project ID และผล bidder รายสถานีแล้ว: **68099138641 = บึงกาฬ**, **68099247067 = กระบี่**
- คำขอ RRD FY2570 มูลค่า 480 ล้านบาทถูกเก็บใต้ `planned` และไม่ถูกนับเป็น award/contract
- TMD public menu ใช้ชื่อ feed `Phetchabun` กับหน้า `phb.php` ขณะที่ map ใช้ `วิเชียรบุรี`; เก็บเป็น quality flag จนกว่าจะมี official station-name crosswalk
- ช่อง `ปฏิบัติการ 17–19 ก.ย. 69` มาจากการตรวจพอร์ทัลรอบเดียววันเดียว (`S-LIVE`) ไม่ใช่ uptime register; สถานีที่ไม่มีช่องนี้คือไม่มีสัญญาณรอบตรวจนั้น
- ใน bidder rows `[P]` = ผ่านการพิจารณา `[N]` = ไม่ผ่านการพิจารณา ตามผล e-GP
- ระเบียน corpus ที่ไม่ผูกกับสถานีใด (งานระดับเครือข่าย รถเรดาร์เคลื่อนที่ หรือไม่ระบุสถานี) อยู่ใน `unmatched_events_audit` ของ JSON — ไม่มีการลงเงียบ
- OEM ที่มาจาก dossier ถูกติด `Reported`; ต้องใช้ทะเบียนครุภัณฑ์, as-built และ service records เพื่อยืนยัน
