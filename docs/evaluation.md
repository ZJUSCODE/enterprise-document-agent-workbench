# 评测设计

当前项目提供四层评测：

1. 在线流程指标：从数据库实时汇总任务成功率、审批率、人工接管率、平均处理时长、异常分布。
2. 抽取准确率代理：按必填字段覆盖率计算，用于没有标注集时的早期质量监控。
3. 离线标注集评测：基于 `samples/eval_labels.json` 计算文档分类准确率、字段 exact-match precision、recall、F1 和字段明细。
4. RAG 检索评测：基于 `samples/rag_eval_labels.json` 临时索引样本文档，计算 hit rate@K、MRR 和 evidence recall。

生产环境建议增加标注集：

- 每类文档保留 30-100 份代表性样本。
- 标注字段值、表格行列和异常类型。
- 对每次 Prompt、模型或解析器变更跑离线评测。
- 输出字段级 precision、recall、F1，以及人工修正耗时。

运行当前指标：

```powershell
python scripts/evaluate.py
```

运行离线标注集评测：

```powershell
python scripts/evaluate_dataset.py --labels samples/eval_labels.json --report-output docs/evaluation_report.md
```

当前示例标注集覆盖合同、发票和报告三类文档。输出包括文档分类准确率、字段级 precision / recall / F1，以及每个字段的 expected / actual / predicted / matched 明细。

字段指标定义：

- Precision = 正确抽取字段数 / 已抽取字段数，用于衡量抽取结果是否乱填。
- Recall = 正确抽取字段数 / 标注字段数，用于衡量必填信息是否漏掉。
- F1 = precision 和 recall 的调和平均，用于比较不同 prompt、模型和解析器策略。

运行 RAG 检索评测：

```powershell
python scripts/evaluate_rag.py --labels samples/rag_eval_labels.json --report-output docs/rag_evaluation_report.md
```

RAG 指标定义：

- Hit rate@K = Top K 检索片段中是否有一个片段覆盖该问题的全部期望证据词。
- MRR = 正确证据首次出现排名的倒数平均值，用于衡量好证据是否排在前面。
- Evidence recall = Top K 片段整体覆盖了多少期望证据词，用于衡量答案生成前的上下文是否足够。
