# RAG Retrieval Evaluation Report

## Summary

- Case count: 20
- Positive / negative cases: 17 / 3
- Top K: 3
- Hit rate@K: 1.000
- MRR: 1.000
- Evidence recall: 1.000
- Negative abstention rate: 1.000

## Case Details

### contract_01_scope

- Question: 试点服务具体包含哪些文档能力？
- Expected terms: 文档分类, 字段抽取
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 0.962 | samples/benchmark/contract_01.txt | 试点, 服务, 文档 | 合同编号: DEMO-CT-001 甲方: 杭州星桥示例科技有限公司 乙方: 苏州云册示例服务有限公司 生效日期: 2026年1月15日 总金额: ¥86,500.00 服务内容: 乙方提供文档分类与字段抽取试点。 验收要求: 上线后十个工作日内完成问题整改。 |

### contract_01_remediation

- Question: 验收发现问题后多久完成整改？
- Expected terms: 十个工作日, 整改
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.188 | samples/benchmark/contract_01.txt | 验收, 问题, 完成, 整改 | 合同编号: DEMO-CT-001 甲方: 杭州星桥示例科技有限公司 乙方: 苏州云册示例服务有限公司 生效日期: 2026年1月15日 总金额: ¥86,500.00 服务内容: 乙方提供文档分类与字段抽取试点。 验收要求: 上线后十个工作日内完成问题整改。 |

### contract_02_scope

- Question: 协议覆盖哪些扫描件处理步骤？
- Expected terms: 扫描件 OCR, 索引构建, 审批记录
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 0.909 | samples/benchmark/contract_02.txt | 协议, 扫描, 描件 | 服务协议 合同编号：DEMO-CT-002 甲方：宁波远帆示例制造有限公司 乙方：上海知页示例软件有限公司 生效日期：2026/02/03 金额：¥120000.00 项目范围包括扫描件 OCR、索引构建和审批记录。乙方应在五个工作日内修复阻断问题。 |

### contract_03_service

- Question: What workflow functions are included in the agreement?
- Expected terms: invoice intake, exception review, auditable export
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.360 | samples/benchmark/contract_03.txt | in, the, agreement | Document Processing Agreement Number: DEMO-CT-003 Party A: Northlake Example Operations Ltd. Party B: Cedar Example Automation Ltd. Effective date: 2026-03-12 Amount: $45,750.00 Th |

### contract_04_duration

- Question: 这项服务持续多长时间？
- Expected terms: 六个月
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 0.297 | samples/benchmark/contract_04.txt | 服务 | 合同编号: DEMO-CT-004 甲方: 成都青禾示例零售有限公司 乙方: 武汉简流示例信息技术有限公司 生效日期: 2026-04-20 总金额: ¥68,000 服务周期为六个月，覆盖合同归档、风险条款标注与人工复核。发生数据缺失时应在三个工作日内补齐。 |

### contract_05_review

- Question: 双方每月复盘哪些质量成本指标？
- Expected terms: 召回率, 人工修正成本
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.789 | samples/benchmark/contract_05.txt | 双方, 方每, 每月, 月复, 复盘, 成本 | 智能文档试点合同 合同编号：DEMO-CT-005 甲方：深圳澄海示例供应链有限公司 乙方：广州方舟示例智能科技有限公司 生效日期：2026年5月9日 金额：¥99,900.50 乙方负责报告解析、证据检索和审批工作台配置。双方每月复盘召回率与人工修正成本。 |

### invoice_01_purpose

- Question: 第一张票据对应什么服务？
- Expected terms: 流程咨询服务
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 0.321 | samples/benchmark/invoice_01.csv | 服务 | 发票号码 \| 开票方 \| 购买方 \| 开票日期 \| 价税合计 \| 备注 DEMO-INV-001 \| 北京青岚示例咨询有限公司 \| 天津维度示例贸易有限公司 \| 2026-01-08 \| 18500.00 \| 流程咨询服务 |

### invoice_02_amount

- Question: OCR 服务票据的金额是多少？
- Expected terms: 32680.50
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.141 | samples/benchmark/invoice_02.csv | ocr, 服务, 金额 | 发票号码 \| 供应商 \| 购买方 \| 日期 \| 金额 \| 项目 DEMO-INV-002 \| 南京澜图示例数据有限公司 \| 合肥长亭示例运营有限公司 \| 2026/02/18 \| 32680.50 \| OCR处理服务 |

### invoice_03_supplier

- Question: Who issued the document indexing invoice?
- Expected terms: River Example Systems Ltd.
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 2.887 | samples/benchmark/invoice_03.csv | document, indexing, invoice | invoice number \| issuer \| buyer \| date \| total \| description DEMO-INV-003 \| River Example Systems Ltd. \| Pine Example Services Ltd. \| 2026-03-22 \| 7400.00 \| document indexing servi |

### invoice_04_buyer

- Question: 审批工作台实施由哪家公司购买？
- Expected terms: 福州合页示例物流有限公司
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 2.636 | samples/benchmark/invoice_04.csv | 审批, 批工, 工作, 作台, 台实, 实施, 公司, 购买 | 单据编号 \| 开票方 \| 购买方 \| 开票日期 \| 价税合计 \| 说明 DEMO-INV-004 \| 厦门知岸示例软件有限公司 \| 福州合页示例物流有限公司 \| 2026-04-11 \| 56880.00 \| 审批工作台实施 |

### invoice_05_service

- Question: 五月票据购买的是什么服务？
- Expected terms: RAG评测服务
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 0.652 | samples/benchmark/invoice_05.csv | 购买, 服务 | 发票号码 \| 供应商 \| 购买方 \| 日期 \| 金额 \| 说明 DEMO-INV-005 \| 重庆云栈示例科技有限公司 \| 昆明原点示例商贸有限公司 \| 2026年5月16日 \| 12999.90 \| RAG评测服务 |

### report_01_volume

- Question: 一月共处理多少文档并有多少进入审批？
- Expected terms: 240 份, 18 份
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.732 | samples/benchmark/report_01.txt | 一月, 处理, 文档, 进入, 审批 | 标题: 一月文档自动化运行报告 负责人: analyst.demo01 日期: 2026-01-31 主要结论: 本月处理 240 份文档，其中 18 份进入人工审批。 改进计划: 增加发票异常字段的复核样本。 |

### report_02_latency

- Question: 二月合同平均处理时长是多少？
- Expected terms: 42 秒
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 2.736 | samples/benchmark/report_02.txt | 二月, 月合, 合同, 平均, 均处, 处理, 理时, 时长 | 标题：二月合同审查分析报告 负责人：ops.demo02 日期：2026/02/28 主要结论：合同任务共 96 份，平均处理时长为 42 秒，人工接管 7 份。 后续计划：补充付款条款和违约责任的标注规范。 |

### report_03_exceptions

- Question: How many exceptions were routed to reviewers in March?
- Expected terms: 12 exceptions
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 3.224 | samples/benchmark/report_03.txt | exceptions, routed, to, reviewers, march | Title: March Document Quality Report Owner: qa.demo03 Date: 2026-03-31 Summary: The workflow processed 180 files and routed 12 exceptions to reviewers. Next action: Measure field r |

### report_04_ocr_plan

- Question: 四月针对图片模糊问题准备怎样改进？
- Expected terms: 低清晰度扫描件, 单独评测 OCR
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.593 | samples/benchmark/report_04.txt | 四月, 图片, 片模, 模糊, 改进 | 标题: 四月票据处理月报 负责人: finance.demo04 日期: 2026-04-30 分析结论: 价税合计字段召回率为 92%，有 9 份票据因图片模糊转人工复核。 改进计划: 收集低清晰度扫描件并单独评测 OCR。 |

### report_05_metrics

- Question: 五月报告记录了哪些检索结果？
- Expected terms: Top 3 命中 103 次, 负查询正确拒答 14 次
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.351 | samples/benchmark/report_05.txt | 五月, 报告, 记录, 检索 | 标题：五月知识检索评测报告 负责人：rag.demo05 日期：2026年5月31日 主要结论：完成 120 次检索测试，Top 3 命中 103 次，负查询正确拒答 14 次。 后续计划：增加跨段证据问题并记录人工修正成本。 |

### report_05_next

- Question: 下一阶段要增加什么问题并记录什么成本？
- Expected terms: 跨段证据问题, 人工修正成本
- Expected retrieval: `True`
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.911 | samples/benchmark/report_05.txt | 增加, 问题, 题并, 并记, 记录, 成本 | 标题：五月知识检索评测报告 负责人：rag.demo05 日期：2026年5月31日 主要结论：完成 120 次检索测试，Top 3 命中 103 次，负查询正确拒答 14 次。 后续计划：增加跨段证据问题并记录人工修正成本。 |

### negative_contract_satellite

- Question: 卫星轨道倾角和推进器参数是多少？
- Expected terms:
- Expected retrieval: `False`
- Hit: `True`
- Rank: `None`
- Evidence recall: `0.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |

### negative_invoice_menu

- Question: 员工食堂周五菜单有哪些菜？
- Expected terms:
- Expected retrieval: `False`
- Hit: `True`
- Rank: `None`
- Evidence recall: `0.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |

### negative_report_quantum

- Question: 量子计算机的制冷温度是多少？
- Expected terms:
- Expected retrieval: `False`
- Hit: `True`
- Rank: `None`
- Evidence recall: `0.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
