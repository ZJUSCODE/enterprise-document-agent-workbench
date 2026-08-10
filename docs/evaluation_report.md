# Document Extraction Evaluation Report

## Summary

- Case count: 30
- Classification accuracy: 1.000
- Field accuracy: 1.000
- Field precision: 1.000
- Field recall: 1.000
- Field F1: 1.000
- Matched / predicted / expected fields: 85 / 85 / 85

## Field Breakdown

| Field | Precision | Recall | F1 | Matched | Predicted | Expected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| amount | 1.000 | 1.000 | 1.000 | 15 | 15 | 15 |
| date | 1.000 | 1.000 | 1.000 | 10 | 10 | 10 |
| document_no | 1.000 | 1.000 | 1.000 | 18 | 18 | 18 |
| effective_date | 1.000 | 1.000 | 1.000 | 5 | 5 | 5 |
| issuer | 1.000 | 1.000 | 1.000 | 7 | 7 | 7 |
| owner | 1.000 | 1.000 | 1.000 | 10 | 10 | 10 |
| party_a | 1.000 | 1.000 | 1.000 | 5 | 5 | 5 |
| party_b | 1.000 | 1.000 | 1.000 | 5 | 5 | 5 |
| title | 1.000 | 1.000 | 1.000 | 10 | 10 | 10 |

## Case Details

### contract_01_identity

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-001 | DEMO-CT-001 | True | True |
| party_a | 杭州星桥示例科技有限公司 | 杭州星桥示例科技有限公司 | True | True |
| party_b | 苏州云册示例服务有限公司 | 苏州云册示例服务有限公司 | True | True |
| effective_date | 2026年1月15日 | 2026年1月15日 | True | True |

### contract_01_amount

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-001 | DEMO-CT-001 | True | True |
| amount | ¥86,500.00 | ¥86,500.00 | True | True |

### contract_02_identity

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-002 | DEMO-CT-002 | True | True |
| party_a | 宁波远帆示例制造有限公司 | 宁波远帆示例制造有限公司 | True | True |
| party_b | 上海知页示例软件有限公司 | 上海知页示例软件有限公司 | True | True |
| effective_date | 2026/02/03 | 2026/02/03 | True | True |

### contract_02_amount

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-002 | DEMO-CT-002 | True | True |
| amount | ¥120000.00 | ¥120000.00 | True | True |

### contract_03_identity

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-003 | DEMO-CT-003 | True | True |
| party_a | Northlake Example Operations Ltd. | Northlake Example Operations Ltd. | True | True |
| party_b | Cedar Example Automation Ltd. | Cedar Example Automation Ltd. | True | True |
| effective_date | 2026-03-12 | 2026-03-12 | True | True |

### contract_03_amount

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-003 | DEMO-CT-003 | True | True |
| amount | $45,750.00 | $45,750.00 | True | True |

### contract_04_identity

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-004 | DEMO-CT-004 | True | True |
| party_a | 成都青禾示例零售有限公司 | 成都青禾示例零售有限公司 | True | True |
| party_b | 武汉简流示例信息技术有限公司 | 武汉简流示例信息技术有限公司 | True | True |
| effective_date | 2026-04-20 | 2026-04-20 | True | True |

### contract_04_amount

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-004 | DEMO-CT-004 | True | True |
| amount | ¥68,000 | ¥68,000 | True | True |

### contract_05_identity

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-005 | DEMO-CT-005 | True | True |
| party_a | 深圳澄海示例供应链有限公司 | 深圳澄海示例供应链有限公司 | True | True |
| party_b | 广州方舟示例智能科技有限公司 | 广州方舟示例智能科技有限公司 | True | True |
| effective_date | 2026年5月9日 | 2026年5月9日 | True | True |

### contract_05_amount

- Predicted type: `contract`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-CT-005 | DEMO-CT-005 | True | True |
| amount | ¥99,900.50 | ¥99,900.50 | True | True |

### invoice_01_core

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-001 | DEMO-INV-001 | True | True |
| issuer | 北京青岚示例咨询有限公司 | 北京青岚示例咨询有限公司 | True | True |
| date | 2026-01-08 | 2026-01-08 | True | True |
| amount | 18500.00 | 18500.00 | True | True |

### invoice_01_finance

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-001 | DEMO-INV-001 | True | True |
| amount | 18500.00 | 18500.00 | True | True |

### invoice_02_core

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-002 | DEMO-INV-002 | True | True |
| issuer | 南京澜图示例数据有限公司 | 南京澜图示例数据有限公司 | True | True |
| date | 2026/02/18 | 2026/02/18 | True | True |
| amount | 32680.50 | 32680.50 | True | True |

### invoice_02_finance

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| issuer | 南京澜图示例数据有限公司 | 南京澜图示例数据有限公司 | True | True |
| amount | 32680.50 | 32680.50 | True | True |

### invoice_03_core

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-003 | DEMO-INV-003 | True | True |
| issuer | River Example Systems Ltd. | River Example Systems Ltd. | True | True |
| date | 2026-03-22 | 2026-03-22 | True | True |
| amount | 7400.00 | 7400.00 | True | True |

### invoice_03_finance

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-003 | DEMO-INV-003 | True | True |
| amount | 7400.00 | 7400.00 | True | True |

### invoice_04_core

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-004 | DEMO-INV-004 | True | True |
| issuer | 厦门知岸示例软件有限公司 | 厦门知岸示例软件有限公司 | True | True |
| date | 2026-04-11 | 2026-04-11 | True | True |
| amount | 56880.00 | 56880.00 | True | True |

### invoice_04_finance

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| issuer | 厦门知岸示例软件有限公司 | 厦门知岸示例软件有限公司 | True | True |
| amount | 56880.00 | 56880.00 | True | True |

### invoice_05_core

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-005 | DEMO-INV-005 | True | True |
| issuer | 重庆云栈示例科技有限公司 | 重庆云栈示例科技有限公司 | True | True |
| date | 2026年5月16日 | 2026年5月16日 | True | True |
| amount | 12999.90 | 12999.90 | True | True |

### invoice_05_finance

- Predicted type: `invoice`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| document_no | DEMO-INV-005 | DEMO-INV-005 | True | True |
| amount | 12999.90 | 12999.90 | True | True |

### report_01_core

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 一月文档自动化运行报告 | 一月文档自动化运行报告 | True | True |
| owner | analyst.demo01 | analyst.demo01 | True | True |
| date | 2026-01-31 | 2026-01-31 | True | True |

### report_01_owner

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 一月文档自动化运行报告 | 一月文档自动化运行报告 | True | True |
| owner | analyst.demo01 | analyst.demo01 | True | True |

### report_02_core

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 二月合同审查分析报告 | 二月合同审查分析报告 | True | True |
| owner | ops.demo02 | ops.demo02 | True | True |
| date | 2026/02/28 | 2026/02/28 | True | True |

### report_02_owner

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 二月合同审查分析报告 | 二月合同审查分析报告 | True | True |
| owner | ops.demo02 | ops.demo02 | True | True |

### report_03_core

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | March Document Quality Report | March Document Quality Report | True | True |
| owner | qa.demo03 | qa.demo03 | True | True |
| date | 2026-03-31 | 2026-03-31 | True | True |

### report_03_owner

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | March Document Quality Report | March Document Quality Report | True | True |
| owner | qa.demo03 | qa.demo03 | True | True |

### report_04_core

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 四月票据处理月报 | 四月票据处理月报 | True | True |
| owner | finance.demo04 | finance.demo04 | True | True |
| date | 2026-04-30 | 2026-04-30 | True | True |

### report_04_owner

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 四月票据处理月报 | 四月票据处理月报 | True | True |
| owner | finance.demo04 | finance.demo04 | True | True |

### report_05_core

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 五月知识检索评测报告 | 五月知识检索评测报告 | True | True |
| owner | rag.demo05 | rag.demo05 | True | True |
| date | 2026年5月31日 | 2026年5月31日 | True | True |

### report_05_owner

- Predicted type: `report`
- Classification matched: `True`
- Field accuracy: `1.000`
- Field precision / recall / F1: `1.000` / `1.000` / `1.000`

| Field | Expected | Actual | Predicted | Matched |
| --- | --- | --- | --- | --- |
| title | 五月知识检索评测报告 | 五月知识检索评测报告 | True | True |
| owner | rag.demo05 | rag.demo05 | True | True |
