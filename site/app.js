const DATA_URL = "data/radar_station_master.json";
const POLITICAL_DATA_URL = "data/political_context_2026-09-19.json";
const MAP_DATA_URL = "data/tha_adm0_simplified.geojson";
const COVERAGE_DATA_URL = "data/radar_coverage_summary.json";
const COVERAGE_STATIONS_URL = "data/radar_stations_map.json";
const PUBLIC_REPO_BASE = "https://github.com/luengnat/radar/blob/main/";
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const unwrap = (node) => node && typeof node === "object" && "value" in node ? node.value : node;
const moneyFormatter = new Intl.NumberFormat("th-TH");

let master = null;
let political = null;
let mapGeo = null;
let coverageSummary = null;
let coverageStations = [];
let stations = [];
let activeAgency = "all";
let activeYear = "all";
let selectedMapStationId = null;
let mapAgencyFilter = "all";
let mapBandFilter = "all";

function money(value) {
  if (value === null || value === undefined || value === "") return "—";
  return `${moneyFormatter.format(Number(value))} บาท`;
}

function compactMoney(value) {
  if (value === null || value === undefined || value === "") return "—";
  const number = Number(value);
  if (number >= 1_000_000_000) return `${(number / 1_000_000_000).toFixed(3)}B`;
  if (number >= 1_000_000) return `${(number / 1_000_000).toFixed(1)}M`;
  return money(value);
}

function valueAt(node, fallback = null) {
  const value = unwrap(node);
  return value === undefined ? fallback : value;
}

function nameOf(station) {
  return valueAt(station.name_th, "ไม่ระบุสถานี");
}

function agencyOf(station) {
  return valueAt(station.agency, "ไม่ระบุหน่วยงาน");
}

function agencyLabel(agency) {
  return { TMD: "กรมอุตุนิยมวิทยา", RRD: "กรมฝนหลวงฯ", BMA: "กรุงเทพมหานคร" }[agency] || agency;
}

function eventsOf(station) {
  return station.procurement?.events || [];
}

function plannedOf(station) {
  return station.procurement?.planned || [];
}

function eventYear(event) {
  return valueAt(event.contract_year_be) ?? valueAt(event.fiscal_year_be) ?? 0;
}

function plannedYear(plan) {
  const direct = valueAt(plan.fiscal_year_be, null);
  if (direct !== null && direct !== "") return Number(direct) || 0;
  const years = valueAt(plan.fiscal_years_be, null);
  if (Array.isArray(years)) return Number(years[0]) || 0;
  const match = String(years || "").match(/25\d{2}/);
  return match ? Number(match[0]) : 0;
}

function stationHasYear(station, year) {
  if (year === "all") return true;
  return eventsOf(station).some((event) => String(eventYear(event)) === String(year))
    || plannedOf(station).some((plan) => String(plannedYear(plan)) === String(year));
}

function yearSummaries() {
  const summary = new Map();
  const ensure = (year) => {
    if (!year || !Number.isFinite(Number(year))) return null;
    const key = Number(year);
    if (!summary.has(key)) summary.set(key, { year: key, eventCount: 0, planCount: 0, eventValue: 0, planValue: 0, stations: new Set(), items: [] });
    return summary.get(key);
  };
  stations.forEach((station) => {
    eventsOf(station).forEach((event) => {
      const row = ensure(eventYear(event));
      if (!row) return;
      row.eventCount += 1;
      row.eventValue += Number(eventAmount(event) || 0);
      row.stations.add(nameOf(station));
      row.items.push({ kind: "event", station, record: event });
    });
    plannedOf(station).forEach((plan) => {
      const row = ensure(plannedYear(plan));
      if (!row) return;
      row.planCount += 1;
      row.planValue += Number(valueAt(plan.planned_amount_baht, 0) || 0);
      row.stations.add(nameOf(station));
      row.items.push({ kind: "plan", station, record: plan });
    });
  });
  return [...summary.values()].sort((a, b) => a.year - b.year);
}

function yearLabel(summary) {
  if (summary.year === 2570 && summary.eventCount && summary.planCount) return "ปีปัจจุบัน · ประกาศผล + แผน";
  if (summary.year === 2570 && summary.eventCount) return "ปีปัจจุบัน · พบประกาศผล";
  if (summary.year === 2570) return "ปีปัจจุบัน · แผน/คำขอ";
  if (summary.eventCount && summary.planCount) return "ผลจัดซื้อ + แผน";
  if (summary.eventCount) return "ผลจัดซื้อ / ประกาศผล";
  return "แผน / คำขอ";
}

function politicalContextFor(station, event) {
  const fiscalYear = String(eventYear(event));
  const yearContext = political?.fiscal_year_context?.[fiscalYear];
  if (!yearContext) return null;
  const government = yearContext.government || {};
  const timelineItem = (political.government_timeline || []).find((item) => item.id === government.government_id);
  const agency = yearContext.agencies?.[agencyOf(station)] || null;
  return {
    government,
    party: government.party || timelineItem?.party || "ยังไม่ระบุพรรค",
    agency,
    sourceUrl: agency?.source_url || timelineItem?.source_url || "",
  };
}

function politicalCell(station, event) {
  const context = politicalContextFor(station, event);
  if (!context) return '<span class="political-missing">ยังไม่ระบุ</span>';
  const minister = context.agency?.minister || "ยังไม่ระบุ รมว.";
  return `<span class="political-government">${context.government.label || "รัฐบาลยังไม่ระบุ"}</span><br /><span class="bidder-note">${context.party}</span><br /><span class="bidder-note">รมว. ${minister}</span>`;
}

function politicalDialogBlock(station, event) {
  const context = politicalContextFor(station, event);
  if (!context) return "";
  const government = context.government || {};
  const agency = context.agency || {};
  const source = context.sourceUrl ? `<a href="${context.sourceUrl}" target="_blank" rel="noreferrer">ตรวจแหล่งอ้างอิงทางการ ↗</a>` : "";
  return `<div class="dialog-politics"><label>บริบทการเมือง ณ ปีของรายการ</label><strong>${government.label || "รัฐบาลยังไม่ระบุ"}</strong><span>นายกรัฐมนตรี: ${government.prime_minister || "ยังไม่ระบุ"}</span><span>พรรค/ฐานรัฐบาล: ${context.party}</span><span>${agency.ministry || agencyOf(station)} · รมว.: ${agency.minister || "ยังไม่ระบุ"}</span><small>${agency.basis || "จับคู่จากปีงบประมาณ; ตรวจวันสัญญาประกอบ"}</small>${source}</div>`;
}

const RISK_META = {
  review: { label: "ตรวจเพิ่ม", className: "risk-review" },
  gap: { label: "เอกสารไม่พอ", className: "risk-gap" },
  planned: { label: "ยังไม่ใช่สัญญา", className: "risk-planned" },
  clear: { label: "ยังไม่พบสัญญาณเด่น", className: "risk-clear" },
};

function riskBadge(status) {
  const meta = RISK_META[status] || RISK_META.clear;
  return `<span class="risk-chip ${meta.className}">${meta.label}</span>`;
}

function sameReferencePriceCount(event) {
  const reference = Number(valueAt(event.reference_price_baht, NaN));
  if (!Number.isFinite(reference)) return 0;
  return stations.flatMap((station) => eventsOf(station).map((item) => ({ station, item })))
    .filter(({ station, item }) => agencyOf(station) === "TMD" && eventYear(item) === 2569 && valueAt(item.activity_class) === "new_radar_purchase")
    .filter(({ item }) => Number(valueAt(item.reference_price_baht, NaN)) === reference).length;
}

function eventRiskAssessment(station, event) {
  const flags = [];
  const activity = valueAt(event.activity_class, "");
  const isNewRadar = activity === "new_radar_purchase";
  const bidders = displayBidders(event);
  const lowestBidder = valueAt(event.lowest_bidder, "");
  const lowestPrice = valueAt(event.lowest_bid_baht, null);
  const lowestResult = valueAt(event.lowest_result_flag, "");
  const referencePrice = Number(valueAt(event.reference_price_baht, NaN));
  const budget = Number(valueAt(event.budget_baht, NaN));
  const officialType = String(valueAt(station.radar?.official_tmd_type, "")).toLowerCase();
  const eventBand = String(valueAt(event.radar_band, "")).toLowerCase();

  if (isNewRadar && lowestBidder && String(lowestResult).toUpperCase() === "N") {
    flags.push({ kind: "watch", label: "ผู้เสนอราคาต่ำสุดถูกระบุว่าไม่ผ่าน", detail: `${lowestBidder}${lowestPrice ? ` · ${money(lowestPrice)}` : ""}` });
  }
  const repeatedReferenceCount = sameReferencePriceCount(event);
  if (isNewRadar && repeatedReferenceCount >= 2) {
    flags.push({ kind: "watch", label: `ราคากลางซ้ำกัน ${repeatedReferenceCount} โครงการ`, detail: referencePrice ? money(referencePrice) : "ตัวเลขเดียวกันในชุด FY2569" });
  }
  if (isNewRadar && Number.isFinite(referencePrice) && Number.isFinite(budget) && referencePrice > budget) {
    flags.push({ kind: "gap", label: "ราคากลางสูงกว่าวงเงินงบประมาณ", detail: `${money(referencePrice)} เทียบกับงบ ${money(budget)} · ควรตรวจเอกสารงบ/ราคากลาง` });
  }
  if (isNewRadar && eventBand.includes("s-band") && officialType.includes("c-band")) {
    flags.push({ kind: "gap", label: "band ในบัญชี TMD กับโครงการไม่ตรงกัน", detail: `บัญชี TMD ระบุ ${valueAt(station.radar?.official_tmd_type)} แต่ event ระบุ ${valueAt(event.radar_band)} · ต้องแยกชนิดบัญชีกับเครื่องที่จัดซื้อ` });
  }
  if (isNewRadar && (!valueAt(event.contract_number, "") || !valueAt(event.contract_date_be, ""))) {
    flags.push({ kind: "gap", label: "ข้อมูลเลขที่หรือวันที่สัญญายังไม่ครบ", detail: "ผลผู้ชนะพบแล้ว แต่ควรขอสัญญาที่ลงนามแล้ว" });
  }
  if (/specific|direct|เฉพาะเจาะจง/i.test(String(valueAt(event.procurement_method, "")))) {
    flags.push({ kind: "watch", label: "ใช้วิธีเฉพาะเจาะจง/โดยตรง", detail: "ต้องตรวจฐานเหตุผล วิธีคัดเลือก และเอกสารเปรียบเทียบราคา" });
    if (!bidders.length) flags.push({ kind: "gap", label: "ไม่พบรายชื่อผู้ยื่นราคาใน event", detail: "ยังสรุปการแข่งขันด้านราคาไม่ได้" });
  }
  if (/disagree|conflict|ขัดแย้ง|ต่างกัน/i.test(String(valueAt(event.review_note, "")))) {
    flags.push({ kind: "gap", label: "เอกสารทางการระบุวันที่ไม่ตรงกัน", detail: valueAt(event.review_note, "ต้องขอเอกสารต้นฉบับเพื่อชี้ขาด") });
  }

  const status = flags.some((flag) => flag.kind === "watch") ? "review" : flags.length ? "gap" : "clear";
  return { status, flags };
}

function plannedRiskAssessment(plan) {
  const flags = [{ kind: "planned", label: "เป็นแผน/คำขอหรือร่าง TOR ยังไม่ใช่ผลจัดซื้อ", detail: valueAt(plan.evidence_status, "ยังไม่พบ award") }];
  const quoteSet = valueAt(plan.quotation_set_baht, null);
  if (quoteSet && typeof quoteSet === "object") {
    const quoteValues = Object.values(quoteSet).map(Number).filter(Number.isFinite);
    if (quoteValues.length >= 2) flags.push({ kind: "planned", label: "เอกสารคำขอมีชุดใบเสนอราคาหลายราย", detail: quoteValues.map((value) => compactMoney(value)).join(" / ") });
  }
  if (valueAt(plan.brand_or_platform_in_draft_tor, "")) flags.push({ kind: "planned", label: "มีชื่อ platform ในร่าง TOR", detail: valueAt(plan.brand_or_platform_in_draft_tor) });
  return { status: "planned", flags };
}

function stationRiskAssessment(station) {
  const events = eventsOf(station).map((event) => eventRiskAssessment(station, event));
  const plans = plannedOf(station).map((plan) => plannedRiskAssessment(plan));
  const flags = [...events.flatMap((assessment) => assessment.flags), ...plans.flatMap((assessment) => assessment.flags)];
  let status = "clear";
  if (events.some((assessment) => assessment.status === "review")) status = "review";
  else if (events.some((assessment) => assessment.status === "gap")) status = "gap";
  else if (plans.length) status = "planned";
  return { status, flags, events, plans };
}

function riskPanel(title, assessment) {
  const meta = RISK_META[assessment.status] || RISK_META.clear;
  const flags = assessment.flags.length ? `<ul>${assessment.flags.map((flag) => `<li><b>${flag.label}</b><span>${flag.detail}</span></li>`).join("")}</ul>` : "<p>จากข้อมูลใน master ตอนนี้ยังไม่พบสัญญาณเด่นที่ถูกตั้งเป็น rule</p>";
  const next = assessment.status === "review" ? "ขั้นถัดไป: ขอรายงานผลคุณสมบัติ/เทคนิคและเอกสารราคากลาง" : assessment.status === "gap" ? "ขั้นถัดไป: เติมสัญญาที่ลงนามแล้วและเอกสารประกอบที่ขาด" : assessment.status === "planned" ? "ขั้นถัดไป: รอ TOR ฉบับสุดท้าย ประกาศ e-GP และผลผู้ชนะ" : "สถานะนี้ไม่ได้รับรองว่าไม่มีปัญหา เพียงยังไม่มี rule ที่กระตุ้นจากข้อมูลที่พบ";
  return `<div class="risk-panel ${meta.className}"><div class="risk-panel-head"><span>คัดกรองเบื้องต้น</span>${riskBadge(assessment.status)}</div>${flags}<small>${next}</small></div>`;
}

function eventAmount(event) {
  return valueAt(event.award_or_contract_value_baht) ?? valueAt(event.contract_value_baht) ?? valueAt(event.amount_as_reported_baht) ?? null;
}

function eventWinner(event) {
  return valueAt(event.contract_winner) ?? valueAt(event.winner) ?? valueAt(event.seller) ?? "ยังไม่ระบุ";
}

function latestStationRecord(station) {
  return [
    ...eventsOf(station).map((record) => ({ kind: "event", year: eventYear(record), record })),
    ...plannedOf(station).map((record) => ({ kind: "plan", year: plannedYear(record), record })),
  ].filter((item) => item.year).sort((a, b) => b.year - a.year || (a.kind === "event" ? -1 : 1))[0] || null;
}

function bandOf(station) {
  return valueAt(station.radar?.band, "");
}

function bandKey(station) {
  const classify = (raw) => {
    const text = String(raw || "").trim().toUpperCase();
    if (/^S(?:$|[-\s/(])|\bS[- ]?BAND\b/.test(text)) return "S";
    if (/^C(?:$|[-\s/(])|\bC[- ]?BAND\b/.test(text)) return "C";
    if (/^X(?:$|[-\s/(])|\bX[- ]?BAND\b/.test(text)) return "X";
    return "unknown";
  };
  const primary = classify(bandOf(station));
  if (primary !== "unknown") return primary;
  const official = classify(valueAt(station.radar?.official_tmd_type, ""));
  if (official !== "unknown") return official;
  return "unknown";
}

function statusClass(station) {
  const status = String(valueAt(station.status, "")).toLowerCase();
  return status.includes("new") || status.includes("request") ? "status-new" : "";
}

function statusLabel(station) {
  const status = String(valueAt(station.status, "ยังไม่ระบุสถานะ"));
  if (status === "official TMD list only") return "อยู่ในบัญชี TMD เท่านั้น";
  return status
    .replaceAll("existing", "มีสถานีเดิม")
    .replaceAll("new FY", "โครงการใหม่ ปี ")
    .replaceAll("requested FY", "คำขอ ปี ")
    .replaceAll("project", "")
    .replaceAll("request", "คำขอ")
    .replaceAll(" + ", " + ")
    .trim();
}

function displayBidders(event) {
  const bidders = valueAt(event.contract_bidders, []) || valueAt(event.submitted_bids, []) || [];
  return Array.isArray(bidders) ? bidders : [];
}

function bidderName(bidder) {
  return bidder?.supplier || bidder?.name || "ไม่ระบุชื่อ";
}

function bidderAmount(bidder) {
  return bidder?.price_proposal_baht ?? bidder?.amount_baht ?? bidder?.price_agree_baht ?? null;
}

function eventLabel(event) {
  const activity = valueAt(event.activity_class, "procurement");
  const labels = {
    new_radar_purchase: "ซื้อเรดาร์ใหม่",
    core_purchase: "จัดซื้อหลัก",
    upgrade_or_repair: "อัปเกรด / ซ่อม",
    support_or_maintenance: "บำรุงรักษา",
    maintenance: "บำรุงรักษา",
    spare_parts: "อะไหล่",
  };
  return labels[activity] || activity.replaceAll("_", " ");
}

function eventStage(event) {
  const contractNumber = valueAt(event.contract_number, "");
  const contractDate = valueAt(event.contract_date_be, "");
  if (contractNumber || (Array.isArray(contractDate) ? contractDate.length : contractDate)) return "สัญญา";
  if (valueAt(event.winner_notice_date_be, "") || eventWinner(event) !== "ยังไม่ระบุ") return "ประกาศผู้ชนะ";
  return "ผลจัดซื้อ";
}

function sourceHref(sourceId, locator = "") {
  if (locator && /^https?:\/\//i.test(locator)) return locator;
  const source = master?.source_catalog?.[sourceId] || {};
  if (source.url) return source.url;
  if (source.urls?.length) return source.urls[0];
  const file = source.file || source.files?.[0];
  if (file && file.split("/").length > 2) return `${PUBLIC_REPO_BASE}${file}`;
  return file || "README.md";
}

function firstSourceLink(event) {
  const sourceUrl = valueAt(event.source_url, "");
  if (sourceUrl) {
    if (/^https?:\/\//i.test(sourceUrl)) return sourceUrl;
    if (sourceUrl.split("/").length > 2) return `${PUBLIC_REPO_BASE}${sourceUrl}`;
    return sourceUrl;
  }
  const refs = [];
  Object.values(event).forEach((node) => {
    if (node && typeof node === "object" && Array.isArray(node.source)) refs.push(...node.source);
  });
  const first = refs[0] || {};
  return sourceHref(first.id, first.locator);
}

function setText(selector, text) {
  const element = $(selector);
  if (element) element.textContent = text;
}

function calculateStats() {
  const agencies = stations.reduce((result, station) => {
    const agency = agencyOf(station);
    result[agency] = (result[agency] || 0) + 1;
    return result;
  }, {});
  const eventCount = stations.reduce((sum, station) => sum + eventsOf(station).length, 0);
  setText("#generated-date", valueAt(master.generated_on, "—"));
  setText("#stat-stations", String(stations.length));
  setText("#stat-agencies", String(Object.keys(agencies).length));
  setText("#stat-agency-detail", Object.entries(agencies).map(([name, count]) => `${name} ${count}`).join(" · "));
  setText("#stat-events", String(eventCount));
  setText("#stat-sources", String(Object.keys(master.source_catalog || {}).length));
  setText("#filter-all-count", String(stations.length));
  setText("#filter-tmd-count", String(agencies.TMD || 0));
  setText("#filter-rrd-count", String(agencies.RRD || 0));
  setText("#filter-bma-count", String(agencies.BMA || 0));
}

function fy2569Awards() {
  return stations.flatMap((station) => eventsOf(station)
    .filter((event) => eventYear(event) === 2569 && valueAt(event.activity_class) === "new_radar_purchase" && agencyOf(station) === "TMD")
    .map((event) => ({ station, event })));
}

function renderAwards() {
  const awards = fy2569Awards();
  const total = awards.reduce((sum, { event }) => sum + Number(eventAmount(event) || 0), 0);
  setText("#award-total", compactMoney(total));
  const container = $("#award-list");
  if (!awards.length) {
    container.innerHTML = '<p class="muted">ยังไม่พบ event FY2569 ในชุดข้อมูล</p>';
    return;
  }
  container.innerHTML = awards.map(({ station, event }, index) => {
    const lowBidder = valueAt(event.lowest_bidder, "");
    const lowPrice = valueAt(event.lowest_bid_baht, null);
    const name = nameOf(station);
    const winner = eventWinner(event);
    return `<button class="award-row" data-station-id="${station.station_id.value}">
      <span class="award-place">0${index + 1} / ${name}</span>
      <span class="award-winner"><b>${winner}</b><small>${lowBidder ? `<span class="flag">ต่ำสุดไม่ผ่าน · ${compactMoney(lowPrice)}</span>` : "ผลผู้ชนะจาก source"}</small></span>
      <span class="award-price">${compactMoney(eventAmount(event))}</span>
    </button>`;
  }).join("");
  $$(".award-row", container).forEach((row) => row.addEventListener("click", () => openStation(row.dataset.stationId)));
}

function renderRiskOverview() {
  const assessments = stations.map((station) => stationRiskAssessment(station));
  const counts = assessments.reduce((result, assessment) => {
    result[assessment.status] = (result[assessment.status] || 0) + 1;
    return result;
  }, {});
  setText("#risk-review-count", String(counts.review || 0));
  const gapCount = assessments.filter((assessment) => assessment.flags.some((flag) => flag.kind === "gap")).length;
  setText("#risk-gap-count", String(gapCount));
  setText("#risk-planned-count", String(counts.planned || 0));
  setText("#risk-clear-count", String(counts.clear || 0));

  const tmdAwards = fy2569Awards();
  const lowestRejected = tmdAwards.filter(({ event }) => String(valueAt(event.lowest_result_flag, "")).toUpperCase() === "N").length;
  const referencePrices = [...new Set(tmdAwards.map(({ event }) => valueAt(event.reference_price_baht, null)).filter((value) => value !== null))];
  const plannedQuoteSet = stations.flatMap((station) => plannedOf(station).map((plan) => ({ station, plan })))
    .filter(({ plan }) => valueAt(plan.fiscal_year_be) === 2570 && valueAt(plan.quotation_set_baht, null));
  const signals = [
    { className: "signal-orange", number: `${lowestRejected}/${tmdAwards.length}`, title: "ผู้เสนอราคาต่ำสุดไม่ผ่าน", detail: "ในงาน TMD S-band FY2569 ที่มีผลผู้ยื่นราคา · ต้องขอเหตุผลทางเทคนิค" },
    { className: "signal-orange", number: String(referencePrices.length === 1 && tmdAwards.length ? tmdAwards.length : 0), title: "โครงการใช้ราคากลางตัวเลขเดียวกัน", detail: referencePrices.length === 1 && tmdAwards.length ? money(referencePrices[0]) : "ยังไม่พบรูปแบบราคากลางซ้ำในชุดนี้" },
    { className: "signal-blue", number: String(plannedQuoteSet.length), title: "คำขอ RRD มีชุดใบเสนอราคา", detail: plannedQuoteSet.length ? "พิมายและอุดรฯ ยังเป็น draft/request ไม่ใช่ award" : "ยังไม่พบ" },
    { className: "signal-gray", number: "1", title: "งานที่ต้องตรวจวิธีจัดซื้อและวันที่เอกสาร", detail: "ร้องกวาง: specific/direct และรายงานทางการระบุวันที่ต่างกัน" },
  ];
  $("#risk-signals").innerHTML = signals.map((signal) => `<article class="risk-signal ${signal.className}"><strong>${signal.number}</strong><div><b>${signal.title}</b><p>${signal.detail}</p></div></article>`).join("");
}

function coordinatePairs(node, output = []) {
  if (!Array.isArray(node)) return output;
  if (typeof node[0] === "number" && typeof node[1] === "number") {
    output.push(node);
    return output;
  }
  node.forEach((child) => coordinatePairs(child, output));
  return output;
}

function mapProjector(geojson) {
  const pairs = (geojson.features || []).flatMap((feature) => coordinatePairs(feature.geometry?.coordinates));
  const lons = pairs.map(([lon]) => lon);
  const lats = pairs.map(([, lat]) => lat);
  const minLon = Math.min(...lons) - .25;
  const maxLon = Math.max(...lons) + .25;
  const minLat = Math.min(...lats) - .25;
  const maxLat = Math.max(...lats) + .25;
  return ([lon, lat]) => [10 + ((lon - minLon) / (maxLon - minLon)) * 80, 132 - ((lat - minLat) / (maxLat - minLat)) * 124];
}

function svgGeometryPath(geometry, project) {
  const ringPath = (ring) => ring.map((pair, index) => {
    const [x, y] = project(pair);
    return `${index ? "L" : "M"}${x.toFixed(3)} ${y.toFixed(3)}`;
  }).join(" ") + " Z";
  if (geometry?.type === "Polygon") return geometry.coordinates.map(ringPath).join(" ");
  if (geometry?.type === "MultiPolygon") return geometry.coordinates.flatMap((polygon) => polygon.map(ringPath)).join(" ");
  return "";
}

function stationCoordinates(station) {
  const coordinates = station.coordinates || {};
  const rawLat = valueAt(coordinates.lat, null);
  const rawLon = valueAt(coordinates.lon, null);
  if (rawLat === null || rawLat === "" || rawLon === null || rawLon === "") return null;
  const lat = Number(rawLat);
  const lon = Number(rawLon);
  return Number.isFinite(lat) && Number.isFinite(lon) ? [lon, lat] : null;
}

function renderMapSelected(station) {
  const panel = $("#map-selected");
  const button = $("#map-open-station");
  if (!station) {
    panel.innerHTML = "<p>เลือกจุดบนแผนที่เพื่อดูสถานี ผู้ขาย และสถานะคัดกรอง</p>";
    button.disabled = true;
    return;
  }
  const risk = stationRiskAssessment(station);
  const latest = latestStationRecord(station);
  const latestAmount = latest?.kind === "event" ? eventAmount(latest.record) : valueAt(latest?.record?.planned_amount_baht, null);
  const latestLabel = latest ? `${latest.year} · ${latest.kind === "event" ? eventLabel(latest.record) : `แผน/คำขอ · ${eventLabel(latest.record)}`} · ${latestAmount ? compactMoney(latestAmount) : "มูลค่าไม่ระบุ"}` : "ยังไม่มี procurement event หรือแผนที่ผูกกับสถานีนี้";
  const coverageRow = coverageStationFor(station);
  const rangeOverride = coverageRangeOverride();
  const radius = coverageRow ? (rangeOverride ?? Number(coverageRow.radius_km)) : null;
  const radiusLabel = Number.isFinite(radius) ? ` · รัศมี ${radius.toLocaleString("th-TH")} กม.${rangeOverride ? " (ทดลอง)" : ""}` : "";
  const overlap = stationOverlapSummary(station);
  const overlapList = overlap.neighbors.slice(0, 5).map((neighbor) => `<li><b>${normalizedMapStationName(neighbor.row.name)}</b><span>${neighbor.distance.toLocaleString("th-TH", { maximumFractionDigits: 0 })} กม. · ${agencyLabel(neighbor.row.agency)} · ${mapBandLabel(coverageBandKey(neighbor.row))}</span></li>`).join("");
  const overlapCopy = !overlap.available
    ? ($("#coverage-toggle")?.checked ? "ไม่พบวงรัศมีของสถานีนี้ในชั้นข้อมูลที่เปิดอยู่" : "เปิด ‘วงรัศมีครอบคลุม’ เพื่อคำนวณสถานีที่วงตัดกัน")
    : overlap.neighbors.length ? `วงของสถานีนี้ตัดกับ ${overlap.neighbors.length} สถานี ภายใต้ตัวกรองและระยะที่กำลังใช้` : "ไม่พบวงของสถานีอื่นตัดกับสถานีนี้ภายใต้ตัวกรองและระยะที่กำลังใช้";
  panel.innerHTML = `<h4>${nameOf(station)}</h4><div class="map-selected-meta">${agencyLabel(agencyOf(station))} · ${mapBandLabel(bandKey(station))}${radiusLabel} · ${RISK_META[risk.status].label}</div><p class="map-selected-note">${latestLabel}</p><div class="map-overlap"><div><span>วงทับซ้อนกับ</span><strong>${overlap.available ? overlap.neighbors.length : "—"}</strong></div><p>${overlapCopy}</p>${overlapList ? `<ul>${overlapList}</ul>` : ""}<small>ระยะในรายการคือระยะระหว่างจุดศูนย์กลาง ไม่ใช่ระยะขอบวง</small></div>`;
  button.disabled = false;
}

function selectMapStation(stationId) {
  const station = stations.find((item) => valueAt(item.station_id) === stationId);
  if (!station) return;
  selectedMapStationId = stationId;
  renderMapSelected(station);
  $$(".map-point").forEach((point) => point.classList.toggle("selected", point.dataset.stationId === stationId));
}

function haversineKm(first, second) {
  const toRadians = (degrees) => degrees * Math.PI / 180;
  const lat1 = toRadians(Number(first.lat));
  const lat2 = toRadians(Number(second.lat));
  const deltaLat = lat2 - lat1;
  const deltaLon = toRadians(Number(second.lon) - Number(first.lon));
  const a = Math.sin(deltaLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(deltaLon / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function overlapPairCount(rows, radiusOverride) {
  const pairs = new Set();
  rows.forEach((station, index) => {
    rows.slice(index + 1).forEach((other) => {
      const firstKey = coverageRowKey(station);
      const secondKey = coverageRowKey(other);
      if (firstKey === secondKey) return;
      const firstRadius = radiusOverride ?? Number(station.radius_km);
      const secondRadius = radiusOverride ?? Number(other.radius_km);
      if ([firstRadius, secondRadius].every(Number.isFinite) && haversineKm(station, other) <= firstRadius + secondRadius) pairs.add([firstKey, secondKey].sort().join("||"));
    });
  });
  return pairs.size;
}

function coverageRowKey(row) {
  return `${row.agency}::${normalizedMapStationName(row.name)}`;
}

function visibleCoverageRows() {
  const showCoverage = $("#coverage-toggle")?.checked ?? true;
  if (!showCoverage) return [];
  const includePlanned = $("#planned-coverage-toggle")?.checked ?? false;
  return coverageStations.filter((station) => (includePlanned || station.status === "existing") && coverageStationMatches(station));
}

function stationOverlapSummary(station) {
  const rows = visibleCoverageRows();
  const selectedKey = `${agencyOf(station)}::${nameOf(station)}`;
  const selectedRows = rows.filter((row) => coverageRowKey(row) === selectedKey);
  if (!selectedRows.length) return { available: false, neighbors: [] };
  const radiusOverride = coverageRangeOverride();
  const neighbors = new Map();
  rows.forEach((row) => {
    const rowKey = coverageRowKey(row);
    if (rowKey === selectedKey) return;
    const rowRadius = radiusOverride ?? Number(row.radius_km);
    const intersections = selectedRows.map((selectedRow) => {
      const selectedRadius = radiusOverride ?? Number(selectedRow.radius_km);
      return { distance: haversineKm(selectedRow, row), threshold: selectedRadius + rowRadius };
    }).filter(({ distance, threshold }) => Number.isFinite(distance) && Number.isFinite(threshold) && distance <= threshold);
    if (!intersections.length) return;
    const distance = Math.min(...intersections.map((item) => item.distance));
    const previous = neighbors.get(rowKey);
    if (!previous || distance < previous.distance) neighbors.set(rowKey, { row, distance });
  });
  return { available: true, neighbors: [...neighbors.values()].sort((a, b) => a.distance - b.distance) };
}

function renderCoverageBrief(visibleCoverage = coverageStations, radiusOverride = null) {
  const panel = $("#coverage-brief");
  if (!panel || !coverageSummary) return;
  if (!($("#coverage-toggle")?.checked ?? true)) {
    panel.innerHTML = '<p><strong>ปิดวงรัศมีอยู่</strong><br />เปิด “วงรัศมีครอบคลุม” เพื่อดูจำนวนคู่สถานีที่วงตัดกันและรายละเอียดรายสถานี</p>';
    return;
  }
  const existing = coverageStations.filter((station) => station.status === "existing").length;
  const planned = coverageStations.filter((station) => station.status !== "existing").length;
  const percentages = coverageSummary.existing_coverage_pct || {};
  const marginal = Object.values(coverageSummary.new_stations_marginal || {});
  const newLand = marginal.reduce((sum, item) => sum + Number(item.newly_covered_km2 || 0), 0);
  const udon = coverageSummary.udon_site_coverage_before;
  const filteredScenario = mapAgencyFilter !== "all" || mapBandFilter !== "all" || radiusOverride !== null || visibleCoverage.length !== existing;
  const overlapPairs = overlapPairCount(visibleCoverage, radiusOverride);
  const rangeLabel = radiusOverride === null ? "ตามค่าที่บันทึกของแต่ละสถานี" : `${radiusOverride.toLocaleString("th-TH")} กม. เท่ากันทุกวง`;
  const baseline = filteredScenario ? "" : `<strong>${percentages["3plus"] ?? "—"}%</strong> ของ land grid อยู่ในรัศมี <b>3 สถานีขึ้นไป</b> จากสถานีเดิม ${existing} แห่ง<br /><b>${planned} รายการใหม่</b> เพิ่มพื้นที่ที่ยังไม่ถูกครอบคลุมรวมประมาณ <b>${newLand.toLocaleString("th-TH")} km²</b> ตามแบบจำลอง${udon ? `<br />จุดอุดรฯ ก่อนเพิ่มโครงการมี overlap อยู่แล้ว <b>${udon} ชั้น</b><br />` : ""}`;
  panel.innerHTML = `<p>${baseline}<strong>${visibleCoverage.length}</strong> วงที่กำลังแสดง · <b>${overlapPairs.toLocaleString("th-TH")} คู่สถานี</b> มีวงตัดกัน<br />ระยะที่ใช้: <b>${rangeLabel}</b><br /><span>${filteredScenario ? "ตัวกรอง/ระยะทดลองเปลี่ยนเฉพาะภาพและจำนวนคู่วงตัดกัน ไม่ได้คำนวณ land grid 3 ชั้นใหม่ · " : ""}วงกลมเชิงเรขาคณิตยังไม่หักภูเขา ความสูงลำคลื่น หรือ beam blockage</span></p>`;
}

function normalizedMapStationName(name) {
  return String(name || "").replace(/\s*\([^)]*\)\s*$/, "").trim();
}

function coverageMasterStation(coverageStation) {
  const normalizedName = normalizedMapStationName(coverageStation.name);
  return stations.find((station) => agencyOf(station) === coverageStation.agency && nameOf(station) === normalizedName) || null;
}

function coverageStationFor(station) {
  return coverageStations.find((row) => row.agency === agencyOf(station) && normalizedMapStationName(row.name) === nameOf(station)) || null;
}

function coverageBandKey(coverageStation) {
  const station = coverageMasterStation(coverageStation);
  return station ? bandKey(station) : "unknown";
}

function mapBandLabel(key) {
  return { all: "ทุก band", S: "S-band", C: "C-band", X: "X-band", unknown: "ยังไม่ระบุ band" }[key] || key;
}

function mapAgencyLabel(key) {
  return key === "all" ? "ทุกหน่วยงาน" : agencyLabel(key);
}

function mapStationMatches(station) {
  return (mapAgencyFilter === "all" || agencyOf(station) === mapAgencyFilter)
    && (mapBandFilter === "all" || bandKey(station) === mapBandFilter);
}

function coverageStationMatches(station) {
  return (mapAgencyFilter === "all" || station.agency === mapAgencyFilter)
    && (mapBandFilter === "all" || coverageBandKey(station) === mapBandFilter);
}

function coverageRangeOverride() {
  const enabled = $("#coverage-range-toggle")?.checked ?? false;
  const value = Number($("#coverage-range")?.value);
  return enabled && Number.isFinite(value) ? value : null;
}

function coverageEllipse(station, project, radiusOverride = null) {
  const lat = Number(station.lat);
  const lon = Number(station.lon);
  const radius = radiusOverride ?? Number(station.radius_km);
  if (![lat, lon, radius].every(Number.isFinite)) return "";
  const [x, y] = project([lon, lat]);
  const lonDelta = radius / (111.32 * Math.max(Math.cos(lat * Math.PI / 180), .25));
  const latDelta = radius / 111.32;
  const [x2] = project([lon + lonDelta, lat]);
  const [, y2] = project([lon, lat + latDelta]);
  const planned = station.status !== "existing";
  return `<ellipse class="coverage-ring agency-${station.agency} ${planned ? "planned" : "existing"}" cx="${x.toFixed(3)}" cy="${y.toFixed(3)}" rx="${Math.abs(x2 - x).toFixed(3)}" ry="${Math.abs(y2 - y).toFixed(3)}"></ellipse>`;
}

function mapPointShape(band, radius) {
  const r = Number(radius.toFixed(3));
  if (band === "C") return `<rect class="map-dot" x="${-r}" y="${-r}" width="${2 * r}" height="${2 * r}" rx=".12"></rect>`;
  if (band === "X") return `<path class="map-dot" d="M0 ${-r} L${r} ${r * .82} L${-r} ${r * .82} Z"></path>`;
  if (band === "unknown") return `<path class="map-dot" d="M0 ${-r} L${r} 0 L0 ${r} L${-r} 0 Z"></path>`;
  return `<circle class="map-dot" r="${r}"></circle>`;
}

function renderMap() {
  const container = $("#station-map");
  if (!container || !mapGeo) return;
  const project = mapProjector(mapGeo);
  const landPaths = (mapGeo.features || []).map((feature) => `<path class="map-land" d="${svgGeometryPath(feature.geometry, project)}"></path>`).join("");
  const showCoverage = $("#coverage-toggle")?.checked ?? true;
  const radiusOverride = coverageRangeOverride();
  const visibleCoverage = visibleCoverageRows();
  const coverageLayer = showCoverage ? visibleCoverage.map((station) => coverageEllipse(station, project, radiusOverride)).join("") : "";
  const eligibleStations = stations.filter(mapStationMatches);
  const mappedStations = eligibleStations.filter((station) => stationCoordinates(station));
  const points = mappedStations.map((station) => {
    const coordinates = stationCoordinates(station);
    const [x, y] = project(coordinates);
    const risk = stationRiskAssessment(station);
    const radius = risk.status === "review" ? 1.35 : risk.status === "planned" ? 1.08 : .82;
    const halo = risk.status === "review" ? 2.35 : risk.status === "planned" ? 1.75 : 1.2;
    const id = valueAt(station.station_id, "");
    const band = bandKey(station);
    return `<g class="map-point agency-${agencyOf(station)} band-${band} ${risk.status === "review" ? "risk-review" : risk.status === "planned" ? "risk-planned" : ""}" data-station-id="${id}" tabindex="0" role="button" aria-label="${nameOf(station)} · ${agencyLabel(agencyOf(station))} · ${mapBandLabel(band)} · ${RISK_META[risk.status].label}" transform="translate(${x.toFixed(3)} ${y.toFixed(3)})"><circle class="map-halo" r="${halo}"></circle>${mapPointShape(band, radius)}<text class="map-point-label" x="${radius + .8}" y="${-radius - .45}">${nameOf(station)}</text><title>${nameOf(station)} · ${agencyLabel(agencyOf(station))} · ${mapBandLabel(band)} · ${RISK_META[risk.status].label}</title></g>`;
  }).join("");
  container.innerHTML = `<svg viewBox="0 0 100 140" role="img" aria-label="แผนที่ตำแหน่งสถานีเรดาร์ประเทศไทย"><g aria-hidden="true"><path class="map-water-grid" d="M5 24H95 M5 48H95 M5 72H95 M5 96H95 M5 120H95 M25 4V136 M50 4V136 M75 4V136"></path></g><g>${landPaths}</g><g aria-hidden="true">${coverageLayer}</g><g>${points}</g></svg>`;
  renderCoverageBrief(showCoverage ? visibleCoverage : [], radiusOverride);
  setText("#map-count", `${mappedStations.length} จุดบนแผนที่ · ${mapAgencyLabel(mapAgencyFilter)} / ${mapBandLabel(mapBandFilter)}${eligibleStations.length - mappedStations.length ? ` · ${eligibleStations.length - mappedStations.length} รายการไม่มีพิกัด` : ""}`);
  $$(".map-point", container).forEach((point) => {
    point.addEventListener("click", () => selectMapStation(point.dataset.stationId));
    point.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectMapStation(point.dataset.stationId); } });
  });
  if (selectedMapStationId && mappedStations.some((station) => valueAt(station.station_id) === selectedMapStationId)) selectMapStation(selectedMapStationId);
  else if (selectedMapStationId) {
    selectedMapStationId = null;
    renderMapSelected(null);
  }
}

function renderPoliticalTimeline() {
  const container = $("#government-timeline");
  if (!container) return;
  const timeline = political?.government_timeline || [];
  if (!timeline.length) {
    container.innerHTML = '<p class="muted">ยังไม่มีข้อมูลช่วงรัฐบาล</p>';
    return;
  }
  container.innerHTML = timeline.map((item, index) => `<article class="government-card ${index === timeline.length - 1 ? "government-card-current" : ""}">
    <span class="government-index">${String(index + 1).padStart(2, "0")}</span>
    <p class="government-label">${item.label}</p>
    <h3>${item.prime_minister}</h3>
    <p class="government-party">${item.party || "ยังไม่ระบุพรรค"}</p>
    <p class="government-period">${item.period}</p>
    <a href="${item.source_url}" target="_blank" rel="noreferrer">แหล่งทางการ ↗</a>
  </article>`).join("");
}

function selectYear(year) {
  activeYear = year === "all" ? "all" : Number(year);
  const select = $("#year-filter");
  if (select) select.value = String(activeYear);
  renderYearView();
  renderStations();
  renderLedger();
}

function renderYearView() {
  const strip = $("#year-strip");
  const detail = $("#year-detail");
  const select = $("#year-filter");
  if (!strip || !detail) return;
  const summaries = yearSummaries();
  const current = summaries.find((summary) => summary.year === 2570);
  if (current) {
    setText("#hero-current-year-title", `ปีปัจจุบัน: พบประกาศผล ${current.eventCount} รายการ + แผน/คำขอ ${current.planCount} รายการ`);
  }
  const selected = activeYear === "all" ? current : summaries.find((summary) => summary.year === Number(activeYear));
  if (select) {
    select.innerHTML = `<option value="all">ทุกปีงบประมาณ</option>${summaries.map((summary) => `<option value="${summary.year}">ปี ${summary.year}</option>`).join("")}`;
    select.value = String(activeYear);
  }
  if (!summaries.length) {
    strip.innerHTML = '<div class="empty-state">ยังไม่มีข้อมูลปีงบประมาณ</div>';
    detail.innerHTML = '<p class="eyebrow">YEAR DETAIL</p><h3>ยังไม่มีข้อมูล</h3>';
    return;
  }
  strip.innerHTML = summaries.map((summary) => {
    const isCurrent = summary.year === 2570;
    const isActive = (activeYear === "all" && isCurrent) || Number(activeYear) === summary.year;
    const valueSummary = summary.eventValue && summary.planValue
      ? `ผล ${compactMoney(summary.eventValue)} · แผน ${compactMoney(summary.planValue)}`
      : summary.eventValue ? `ผลที่พบ · ${compactMoney(summary.eventValue)}`
        : summary.planValue ? `มูลค่าแผน · ${compactMoney(summary.planValue)}` : "ยังไม่ระบุมูลค่า";
    return `<button type="button" class="year-card ${isCurrent ? "year-card-current" : ""} ${isActive ? "year-card-active" : ""}" data-year="${summary.year}" role="listitem" aria-pressed="${isActive}">
      <span class="year-card-top"><b>ปี ${summary.year}</b>${isCurrent ? '<i>ปัจจุบัน</i>' : ""}</span>
      <span class="year-card-label">${yearLabel(summary)}</span>
      <span class="year-card-count"><strong>${summary.eventCount}</strong><small>ผล/สัญญา</small><strong>${summary.planCount}</strong><small>แผน</small></span>
      <span class="year-card-value">${valueSummary}</span>
    </button>`;
  }).join("");
  $$(".year-card", strip).forEach((card) => card.addEventListener("click", () => selectYear(card.dataset.year)));

  const focus = selected || current;
  if (!focus) return;
  const isCurrent = focus.year === 2570;
  const status = yearLabel(focus);
  const itemHtml = focus.items.slice().sort((a, b) => {
    if (a.kind !== b.kind) return a.kind === "event" ? -1 : 1;
    return nameOf(a.station).localeCompare(nameOf(b.station), "th");
  }).map(({ kind, station, record }) => {
    const amount = kind === "event" ? eventAmount(record) : valueAt(record.planned_amount_baht, null);
    const title = kind === "event" ? eventLabel(record) : `แผน/คำขอ · ${eventLabel(record)}`;
    const stage = kind === "event" ? eventStage(record) : "ยังไม่ใช่ผลจัดซื้อ";
    const source = kind === "event" ? firstSourceLink(record) : "";
    const sourceLink = source ? `<a href="${source}" target="_blank" rel="noreferrer">เปิดหลักฐาน ↗</a>` : "";
    return `<li class="year-item year-item-${kind}"><span><i>${stage}</i><b>${nameOf(station)}</b><small>${title}</small>${sourceLink}</span><strong>${amount ? compactMoney(amount) : "—"}</strong></li>`;
  }).join("");
  const totalLabel = focus.eventValue && focus.planValue
    ? `ประกาศผล/สัญญา ${compactMoney(focus.eventValue)} · แผน/คำขอ ${compactMoney(focus.planValue)}`
    : focus.eventValue ? `ประกาศผล/สัญญา ${compactMoney(focus.eventValue)}` : focus.planValue ? `แผน/คำขอ ${compactMoney(focus.planValue)}` : "มูลค่ายังไม่ระบุ";
  const currentNote = isCurrent ? `<div class="year-evidence-split">
    <div class="year-evidence-award"><span>หลักฐานผลที่พบ</span><strong>${focus.eventCount} รายการ · ${compactMoney(focus.eventValue)}</strong><p>ประกาศผู้ชนะงานบำรุงรักษาเรดาร์ S-band สุวรรณภูมิของ TMD — ยังไม่พบเลขที่/วันที่สัญญา และประกาศกำหนดเงื่อนไขเรื่อง พ.ร.บ.งบประมาณกับการจัดสรรเงิน</p></div>
    <div class="year-evidence-plan"><span>แผนและคำของบ</span><strong>${focus.planCount} รายการ · ${compactMoney(focus.planValue)}</strong><p>รายการของกรมฝนหลวงฯ ยังเป็นแผน/ร่าง TOR/คำของบ ไม่ใช่ประกาศผู้ชนะหรือสัญญา</p></div>
  </div><div class="year-current-note"><b>อ่านให้ถูกชั้น:</b> “ประกาศผู้ชนะ” ไม่เท่ากับ “สัญญาที่ลงนามแล้ว” และ “แผน/คำขอ” ยังไม่ใช่ผลจัดซื้อ</div>` : "";
  const sourceLinks = isCurrent ? `<div class="year-sources"><span>เปิดดูงบภายนอก</span><a href="http://budget-explorer.peoplesparty.or.th/" target="_blank" rel="noreferrer">Budget Explorer พรรคประชาชน ↗</a><a href="https://openbudget.wevis.info/?budget_source=2570-draft-1" target="_blank" rel="noreferrer">Thailand Open Budget · ร่าง 2570 ↗</a></div>` : "";
  detail.innerHTML = `<p class="eyebrow">YEAR DETAIL${activeYear === "all" ? " · โฟกัสปีล่าสุด" : ""}</p><h3>ปีงบประมาณ ${focus.year}</h3><span class="year-status">${status}</span><div class="year-detail-stats"><div><strong>${focus.eventCount}</strong><span>ผลจัดซื้อ / สัญญา</span></div><div><strong>${focus.planCount}</strong><span>แผน / คำขอ</span></div><div><strong>${focus.stations.size}</strong><span>สถานี/พื้นที่</span></div></div><p class="year-total">${totalLabel}</p>${currentNote}<ul class="year-item-list">${itemHtml || "<li>ยังไม่มีรายการย่อย</li>"}</ul>${sourceLinks}<p class="year-filter-note">กดปีด้านซ้ายหรือ dropdown เพื่อกรองสถานีและ ledger ให้เหลือเฉพาะปีนี้</p>`;
}

function renderStations() {
  const search = $("#station-search").value.trim().toLowerCase();
  const band = $("#band-filter").value;
  const riskFilter = $("#risk-filter").value;
  const visible = stations.filter((station) => {
    const haystack = JSON.stringify({
      name: nameOf(station),
      aliases: (station.aliases || []).map((alias) => valueAt(alias)),
      agency: agencyOf(station),
      band: bandOf(station),
      oem: valueAt(station.radar?.oem_model),
      id: valueAt(station.station_id),
    }).toLowerCase();
    return (activeAgency === "all" || agencyOf(station) === activeAgency) && stationHasYear(station, activeYear) && (band === "all" || bandKey(station) === band) && (riskFilter === "all" || stationRiskAssessment(station).status === riskFilter) && haystack.includes(search);
  });
  setText("#station-result-count", `${visible.length} / ${stations.length} records`);
  const grid = $("#station-grid");
  if (!visible.length) {
    grid.innerHTML = '<div class="no-results">ไม่พบสถานีตามตัวกรองนี้ — ลองเปลี่ยนคำค้นหรือ band</div>';
    return;
  }
  grid.innerHTML = visible.map((station) => {
    const latest = latestStationRecord(station);
    const officialType = valueAt(station.radar?.official_tmd_type, "");
    const model = valueAt(station.radar?.oem_model, "");
    const band = bandOf(station);
    const risk = stationRiskAssessment(station);
    const badgeHtml = `${band ? `<span class="badge">${band}</span>` : '<span class="badge">band ยังไม่ระบุ</span>'}${officialType ? `<span class="badge">TMD: ${officialType}</span>` : ""}${model ? `<span class="badge badge-warm">${model}</span>` : ""}`;
    const latestAmount = latest?.kind === "event" ? eventAmount(latest.record) : valueAt(latest?.record?.planned_amount_baht, null);
    const latestLabel = latest ? `${latest.year} · ${latest.kind === "event" ? eventLabel(latest.record) : `แผน/คำขอ · ${eventLabel(latest.record)}`}` : "ยังไม่มี event หรือแผน";
    return `<article class="station-card" tabindex="0" role="button" data-station-id="${station.station_id.value}">
      <div class="station-card-top"><span class="station-agency">${agencyLabel(agencyOf(station))}</span>${riskBadge(risk.status)}</div>
      <h3 class="station-name">${nameOf(station)}<small>${valueAt(station.description, "สถานีเรดาร์ / location record")}</small></h3>
      <div class="station-status-line"><span class="station-status ${statusClass(station)}">${statusLabel(station)}</span></div>
      <div class="station-badges">${badgeHtml}</div>
      <div class="station-card-bottom"><span>${latestLabel}</span><b>${latestAmount ? compactMoney(latestAmount) : "เปิดดู →"}</b></div>
    </article>`;
  }).join("");
  $$(".station-card", grid).forEach((card) => {
    card.addEventListener("click", () => openStation(card.dataset.stationId));
    card.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") openStation(card.dataset.stationId); });
  });
}

function renderLedger() {
  const rows = stations.flatMap((station) => eventsOf(station).map((event) => ({ station, event })))
    .filter(({ event }) => activeYear === "all" || String(eventYear(event)) === String(activeYear))
    .sort((a, b) => eventYear(b.event) - eventYear(a.event));
  setText("#ledger-count", `${rows.length} events`);
  const body = $("#ledger-body");
  body.innerHTML = rows.map(({ station, event }) => {
    const contractNo = valueAt(event.contract_number, "");
    const contractDate = valueAt(event.contract_date_be, "");
    const contractText = [contractNo, Array.isArray(contractDate) ? contractDate.join(", ") : contractDate].filter(Boolean).join(" / ") || "ยังไม่ระบุ";
    const seller = valueAt(event.seller, "ยังไม่ระบุ");
    const winner = valueAt(event.contract_winner, eventWinner(event));
    const sellerText = seller === winner ? seller : `${seller} / ${winner}`;
    const bidders = displayBidders(event).length;
    const risk = eventRiskAssessment(station, event);
    return `<tr data-station-id="${station.station_id.value}">
      <td>${nameOf(station)}<br /><span class="bidder-note">${agencyLabel(agencyOf(station))}</span></td>
      <td>${eventYear(event)}</td>
      <td>${eventLabel(event)}<br /><span class="bidder-note">${valueAt(event.radar_band, "—")}</span></td>
      <td class="winner">${sellerText}<br /><span class="bidder-note">${bidders ? `${bidders} bidders เปิดเผย` : "ไม่มี bidder list ใน source"}</span></td>
      <td class="risk-cell">${riskBadge(risk.status)}</td>
      <td class="political-cell">${politicalCell(station, event)}</td>
      <td class="contract-cell">${contractText}</td>
      <td class="money">${eventAmount(event) ? money(eventAmount(event)) : "—"}</td>
    </tr>`;
  }).join("");
  $$("#ledger-body tr").forEach((row) => row.addEventListener("click", () => openStation(row.dataset.stationId)));
}

function renderDialog(station) {
  const radar = station.radar || {};
  const events = eventsOf(station).slice().sort((a, b) => eventYear(b) - eventYear(a));
  const planned = plannedOf(station);
  const flags = station.quality_flags || [];
  const overallRisk = stationRiskAssessment(station);
  const badges = [bandOf(station), valueAt(radar.dual_polarization) === true ? "Dual polarization" : "", valueAt(radar.oem_model, ""), valueAt(radar.official_tmd_type, "")].filter(Boolean);
  const eventHtml = events.length ? events.map((event) => {
    const contractDate = valueAt(event.contract_date_be, "");
    const contractNo = valueAt(event.contract_number, "");
    const bidders = displayBidders(event);
    const source = firstSourceLink(event);
    const eventRisk = eventRiskAssessment(station, event);
    const facts = [
      ["ขั้นของหลักฐาน", eventStage(event)],
      ["ผู้ขาย / ผู้รับสัญญา", valueAt(event.seller, "ยังไม่ระบุ")],
      ["ผู้ชนะ", eventWinner(event)],
      ["วันที่ประกาศผู้ชนะ", valueAt(event.winner_notice_date_be, "")],
      ["เลขสัญญา / วันที่", [contractNo, Array.isArray(contractDate) ? contractDate.join(", ") : contractDate].filter(Boolean).join(" / ") || "ยังไม่ระบุ"],
      ["สถานะสัญญา", valueAt(event.contract_status, "")],
      ["มูลค่า", eventAmount(event) ? money(eventAmount(event)) : "ยังไม่ระบุ"],
      ["รหัสโครงการ", valueAt(event.project_id, "—")],
      ["วิธีจัดซื้อ", valueAt(event.procurement_method, "—")],
    ].filter(([, value]) => value !== "" && value !== null && value !== undefined);
    return `<article class="dialog-event"><div class="dialog-event-head"><span>${eventYear(event)} · ${eventLabel(event)}</span><span>${valueAt(event.radar_band, "")}</span></div><p>${valueAt(event.description, "ไม่มีคำอธิบายเพิ่มเติมใน event")}</p><div class="dialog-facts">${facts.map(([label, value]) => `<div class="dialog-fact"><label>${label}</label><b>${value}</b></div>`).join("")}</div>${riskPanel("", eventRisk)}${politicalDialogBlock(station, event)}${bidders.length ? `<div class="dialog-bidders"><label>disclosed bidders / ผู้ยื่นราคาที่เปิดเผย</label><ul>${bidders.map((bidder) => `<li><span>${bidderName(bidder)}${bidder.result_flag ? ` [${bidder.result_flag}]` : ""}</span><span>${bidderAmount(bidder) ? money(bidderAmount(bidder)) : "—"}</span></li>`).join("")}</ul></div>` : ""}<div class="dialog-source"><a href="${source}" target="_blank" rel="noreferrer">เปิด source ของ event ↗</a></div></article>`;
  }).join("") : '<p class="muted">ยังไม่มี procurement event ที่ผูกกับสถานีนี้</p>';
  const plannedHtml = planned.length ? `<div class="dialog-section-title" style="margin-top:24px">PLANNED / REQUESTED</div>${planned.map((event) => `<article class="dialog-event planned-event"><div class="dialog-event-head"><span>${valueAt(event.fiscal_year_be, valueAt(event.fiscal_years_be, "แผน"))} · ${eventLabel(event)}</span><span>${valueAt(event.radar_band, "")}</span></div><p>${valueAt(event.description, "แผน/คำขอ")}</p><div class="dialog-facts"><div class="dialog-fact"><label>planned amount</label><b>${valueAt(event.planned_amount_baht) ? money(valueAt(event.planned_amount_baht)) : "—"}</b></div><div class="dialog-fact"><label>draft platform</label><b>${valueAt(event.brand_or_platform_in_draft_tor, "ยังไม่ระบุ")}</b></div><div class="dialog-fact"><label>evidence</label><b>${valueAt(event.evidence_status, "—")}</b></div></div></article>`).join("")}` : "";
  const qualityHtml = flags.length ? `<div class="dialog-quality"><b>QUALITY FLAGS</b><ul>${flags.map((flag) => `<li>${valueAt(flag)}</li>`).join("")}</ul></div>` : "";
  $("#dialog-content").innerHTML = `<div class="dialog-inner"><span class="dialog-kicker">${agencyLabel(agencyOf(station))} / ข้อมูลสถานี</span><h2 class="dialog-title">${nameOf(station)}</h2><p class="dialog-subtitle">${valueAt(station.description, "สถานีจากแผนที่หรือบัญชีทางการ")}</p><div class="dialog-overview">${badges.map((badge) => `<span class="badge">${badge}</span>`).join("")}${riskBadge(overallRisk.status)}</div>${riskPanel("", overallRisk)}<div class="dialog-section-title">ลำดับการจัดซื้อ / ${events.length} EVENTS</div>${eventHtml}${plannedHtml}${qualityHtml}</div>`;
}

function openStation(stationId) {
  const station = stations.find((item) => valueAt(item.station_id) === stationId);
  if (!station) return;
  renderDialog(station);
  const dialog = $("#station-dialog");
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
}

function wireControls() {
  $$("[data-filter-agency]").forEach((button) => button.addEventListener("click", () => {
    activeAgency = button.dataset.filterAgency;
    $$("[data-filter-agency]").forEach((item) => item.classList.toggle("active", item === button));
    renderStations();
  }));
  $("#station-search").addEventListener("input", renderStations);
  $("#band-filter").addEventListener("change", renderStations);
  $("#risk-filter").addEventListener("change", renderStations);
  $("#year-filter").addEventListener("change", (event) => selectYear(event.target.value));
  $$('[data-map-agency]').forEach((button) => button.addEventListener("click", () => {
    mapAgencyFilter = button.dataset.mapAgency;
    $$('[data-map-agency]').forEach((item) => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    renderMap();
  }));
  $$('[data-map-band]').forEach((button) => button.addEventListener("click", () => {
    mapBandFilter = button.dataset.mapBand;
    $$('[data-map-band]').forEach((item) => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    renderMap();
  }));
  $("#coverage-toggle").addEventListener("change", renderMap);
  $("#planned-coverage-toggle").addEventListener("change", renderMap);
  $("#coverage-range-toggle").addEventListener("change", (event) => {
    $("#coverage-range").disabled = !event.target.checked;
    setText("#coverage-range-value", event.target.checked ? `${Number($("#coverage-range").value).toLocaleString("th-TH")} กม. · ค่าทดลอง` : "ตามข้อมูลสถานี");
    renderMap();
  });
  $("#coverage-range").addEventListener("input", (event) => {
    setText("#coverage-range-value", `${Number(event.target.value).toLocaleString("th-TH")} กม. · ค่าทดลอง`);
    renderMap();
  });
  $("#map-filter-reset").addEventListener("click", () => {
    mapAgencyFilter = "all";
    mapBandFilter = "all";
    $$('[data-map-agency]').forEach((item) => {
      const active = item.dataset.mapAgency === "all";
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    $$('[data-map-band]').forEach((item) => {
      const active = item.dataset.mapBand === "all";
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    $("#coverage-toggle").checked = true;
    $("#planned-coverage-toggle").checked = false;
    $("#coverage-range-toggle").checked = false;
    $("#coverage-range").value = "240";
    $("#coverage-range").disabled = true;
    setText("#coverage-range-value", "ตามข้อมูลสถานี");
    selectedMapStationId = null;
    renderMapSelected(null);
    renderMap();
  });
  $("#map-open-station").addEventListener("click", () => { if (selectedMapStationId) openStation(selectedMapStationId); });
  $("#dialog-close").addEventListener("click", () => $("#station-dialog").close());
  $("#station-dialog").addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); });
}

async function init() {
  try {
    const [response, politicalResponse, mapResponse, coverageResponse, coverageStationsResponse] = await Promise.all([fetch(DATA_URL), fetch(POLITICAL_DATA_URL), fetch(MAP_DATA_URL), fetch(COVERAGE_DATA_URL), fetch(COVERAGE_STATIONS_URL)]);
    if (!response.ok) throw new Error(`โหลดข้อมูลไม่สำเร็จ (${response.status})`);
    master = await response.json();
    political = politicalResponse.ok ? await politicalResponse.json() : null;
    mapGeo = mapResponse.ok ? await mapResponse.json() : null;
    coverageSummary = coverageResponse.ok ? await coverageResponse.json() : null;
    coverageStations = coverageStationsResponse.ok ? await coverageStationsResponse.json() : [];
    stations = master.stations || [];
    calculateStats();
    renderAwards();
    renderRiskOverview();
    renderMap();
    renderYearView();
    renderStations();
    renderLedger();
    renderPoliticalTimeline();
    wireControls();
  } catch (error) {
    console.error(error);
    setText("#station-result-count", "โหลด station master ไม่สำเร็จ");
    $("#station-grid").innerHTML = `<div class="empty-state">โหลดข้อมูลไม่ได้ — เปิดเว็บไซต์ผ่าน web server และตรวจว่าไฟล์ <code>data/radar_station_master.json</code> อยู่ใน path เดียวกัน</div>`;
  }
}

init();
