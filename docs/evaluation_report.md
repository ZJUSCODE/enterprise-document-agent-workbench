# Document Extraction Evaluation Report

## Summary

- Case count: 3
- Classification accuracy: 1.000
- Field accuracy: 1.000
- Field precision: 1.000
- Field recall: 1.000
- Field F1: 1.000
- Matched / predicted / expected fields: 12 / 12 / 12

## Field Breakdown

| Field | Precision | Recall | F1 | Matched | Predicted | Expected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| amount | 1.000 | 1.000 | 1.000 | 2 | 2 | 2 |
| date | 1.000 | 1.000 | 1.000 | 2 | 2 | 2 |
| document_no | 1.000 | 1.000 | 1.000 | 2 | 2 | 2 |
| effective_date | 1.000 | 1.000 | 1.000 | 1 | 1 | 1 |
| issuer | 1.000 | 1.000 | 1.000 | 1 | 1 | 1 |
| owner | 1.000 | 1.000 | 1.000 | 1 | 1 | 1 |
| party_a | 1.000 | 1.000 | 1.000 | 1 | 1 | 1 |
| party_b | 1.000 | 1.000 | 1.000 | 1 | 1 | 1 |
| title | 1.000 | 1.000 | 1.000 | 1 | 1 | 1 |

## Case Details

### contract_sample

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | CT-2026-0417 | CT-2026-0417 | True | True |
| party_a | 上海示例科技有限公司 | 上海示例科技有限公司 | True | True |
| party_b | 北京流程自动化服务有限公司 | 北京流程自动化服务有限公司 | True | True |
| effective_date | 2026年4月17日 | 2026年4月17日 | True | True |
| amount | ¥128,000.00 | ¥128,000.00 | True | True |

### invoice_sample

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | INV-2026-0008 | INV-2026-0008 | True | True |
| issuer | 北京流程自动化服务有限公司 | 北京流程自动化服务有限公司 | True | True |
| date | 2026-04-17 | 2026-04-17 | True | True |
| amount | 128000.00 | 128000.00 | True | True |

### report_sample

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 企业文档流程自动化月度运行报告 | 企业文档流程自动化月度运行报告 | True | True |
| owner | ops.demo | ops.demo | True | True |
| date | 2026-04-18 | 2026-04-18 | True | True |
