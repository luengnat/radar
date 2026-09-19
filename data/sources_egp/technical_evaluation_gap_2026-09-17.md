# FY 2569 S-band technical-evaluation gap

Checked 17 September 2026 through fresh project-specific e-GP browser sessions
and the public getProcureResult response.

The related-documents UI was also checked by project ID. For all four projects,
the modal labelled “ข้อมูลรายชื่อผู้ผ่านการพิจารณาคุณสมบัติและเทคนิค” displayed
only the two passing firms; it did not expose a failed-item checklist, score,
committee report, or written reason. A representative UI capture is archived
at `phitsanulok_technical_passers_modal_2026-09-17.png`.

The portal now exposes the submitted prices and a result flag for all four
projects. It does not expose the written reason behind the N result flag, and
the public “ผู้ผ่านการพิจารณาคุณสมบัติและเทคนิค” view lists only the passing
firms. It does not provide the committee's checklist, failed TOR items,
document deficiencies, or scoring sheet.

| Station | Project ID | Lowest price | Result | Lowest-price bidder |
| --- | --- | ---: | --- | --- |
| Chumphon | 68099138543 | 391,620,000 | N | AsiaMet |
| Bueng Kan | 68099138641 | 375,570,000 | N | Scientific Research |
| Phitsanulok | 68099138724 | 389,480,000 | N | AsiaMet |
| Krabi | 68099247067 | 375,570,000 | N | Scientific Research |

This establishes a repeated outcome, not the reason for the outcome. The
missing primary documents remain:

1. committee qualification/technical-evaluation report for each project;
2. TOR compliance matrix and failed-item explanation for each rejected bidder;
3. bid-opening report and complete submitted-document checklist;
4. any clarification request and bidder response; and
5. committee minutes or approval report connecting the technical result to the
   winner decision.

Source snapshot: [egp_sband_procure_results_api_2026-09-17.json](../egp_sband_procure_results_api_2026-09-17.json).
