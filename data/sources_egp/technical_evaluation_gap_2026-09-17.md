# FY 2569 S-band technical-evaluation gap

Initial check: 17 September 2026 through fresh project-specific e-GP browser
sessions and the public getProcureResult response. Rechecked 23 September 2026
through the current e-GP All Web public UI and its project-detail/related-document
endpoints.

The current portal is dated “23 กันยายน 2569” and now uses the
`egp-oann10-service` route. The older `egp-atpj27-service/getProcureResult`
URL recorded in the earlier snapshot returned 404 during the recheck; this is
an endpoint change, not evidence that the project record disappeared.

The related-documents UI was also checked by project ID. For all four projects,
the current modal labelled “ข้อมูลรายชื่อผู้ผ่านการพิจารณาคุณสมบัติและเทคนิค”
still displays only the two passing firms; it does not expose a failed-item
checklist, score, committee report, or written reason. The fresh recheck found
no new technical-evaluation document. A representative UI capture from the
earlier check is archived at `phitsanulok_technical_passers_modal_2026-09-17.png`.

The earlier project-specific result snapshot exposes the submitted prices and
the N result flag for all four projects. The current public technical-passers
view still does not expose the written reason behind the N result flag, and
lists only the passing firms. It does not provide the committee's checklist,
failed TOR items, document deficiencies, or scoring sheet.

| Station | Project ID | Lowest price | Result | Lowest-price bidder | Current technical passers |
| --- | --- | ---: | --- | --- | --- |
| Chumphon | 68099138543 | 391,620,000 | N | AsiaMet | Genomatch; Marwin |
| Bueng Kan | 68099138641 | 375,570,000 | N | Scientific Research | Genomatch; Marwin |
| Phitsanulok | 68099138724 | 389,480,000 | N | AsiaMet | Genomatch; Marwin |
| Krabi | 68099247067 | 375,570,000 | N | Scientific Research | Genomatch; Marwin |

This establishes a repeated outcome, not the reason for the outcome. The
missing primary documents remain:

1. committee qualification/technical-evaluation report for each project;
2. TOR compliance matrix and failed-item explanation for each rejected bidder;
3. bid-opening report and complete submitted-document checklist;
4. any clarification request and bidder response; and
5. committee minutes or approval report connecting the technical result to the
   winner decision.

Source snapshots: [egp_sband_procure_results_api_2026-09-17.json](../egp_sband_procure_results_api_2026-09-17.json) and [technical_evaluation_recheck_2026-09-23.json](technical_evaluation_recheck_2026-09-23.json).
