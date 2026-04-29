# RAG Retrieval Evaluation Report

## Summary

- Case count: 5
- Top K: 3
- Hit rate@K: 1.000
- MRR: 1.000
- Evidence recall: 1.000

## Case Details

### contract_payment_and_liability

- Question: 这份合同的服务内容和违约责任是什么？
- Expected terms: 实施服务, 整改
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 1.592 | samples/contract_sample.txt | 合同, 服务 | 合同编号: CT-2026-0417 甲方: 上海示例科技有限公司 乙方: 北京流程自动化服务有限公司 生效日期: 2026年4月17日 总金额: ¥128,000.00  双方约定乙方为甲方提供企业文档流程自动化 Agent 工作台实施服务，包括文档解析、字段抽取、模板生成、审批队列和审计日志。 服务周期为 90 天。乙方应在项目上线后提供 30 天稳定期 |

### contract_support_period

- Question: 项目上线后提供多久稳定期支持？
- Expected terms: 30 天稳定期支持
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 3.893 | samples/contract_sample.txt | 项目, 目上, 上线, 线后, 后提, 提供, 稳定, 定期, 期支, 支持 | 合同编号: CT-2026-0417 甲方: 上海示例科技有限公司 乙方: 北京流程自动化服务有限公司 生效日期: 2026年4月17日 总金额: ¥128,000.00  双方约定乙方为甲方提供企业文档流程自动化 Agent 工作台实施服务，包括文档解析、字段抽取、模板生成、审批队列和审计日志。 服务周期为 90 天。乙方应在项目上线后提供 30 天稳定期 |

### invoice_amount

- Question: 这张发票的价税合计是多少？
- Expected terms: 128000.00
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 2.465 | samples/invoice_sample.csv | 发票, 价税, 税合, 合计 | 发票号码 \| 开票方 \| 购买方 \| 开票日期 \| 价税合计 INV-2026-0008 \| 北京流程自动化服务有限公司 \| 上海示例科技有限公司 \| 2026-04-17 \| 128000.00 |

### report_monthly_volume

- Question: 本月系统处理了多少份文档？
- Expected terms: 128 份
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 3.171 | samples/report_sample.txt | 本月, 月系, 系统, 统处, 处理, 文档 | 标题: 企业文档流程自动化月度运行报告 负责人: ops.demo 日期: 2026-04-18  本月系统处理合同、发票和表格类文档共 128 份，平均处理时长 18 秒。 主要结论: Agent 工作流可以稳定完成解析、RAG 索引、字段抽取、风险审查和人工审批流转。 后续计划: 增加更多标注样本，评估字段级准确率、召回率和人工修正成本。 |

### report_next_plan

- Question: 后续计划要评估哪些质量指标？
- Expected terms: 字段级准确率, 召回率, 人工修正成本
- Hit: `True`
- Rank: `1`
- Evidence recall: `1.000`

| Rank | Score | File | Matched Query Terms | Preview |
| ---: | ---: | --- | --- | --- |
| 1 | 2.096 | samples/report_sample.txt | 后续, 续计, 计划, 评估 | 标题: 企业文档流程自动化月度运行报告 负责人: ops.demo 日期: 2026-04-18  本月系统处理合同、发票和表格类文档共 128 份，平均处理时长 18 秒。 主要结论: Agent 工作流可以稳定完成解析、RAG 索引、字段抽取、风险审查和人工审批流转。 后续计划: 增加更多标注样本，评估字段级准确率、召回率和人工修正成本。 |
