# OCR, RAG, and Agent Toolchain

## OCR

系统会在两类场景尝试 OCR：

- 上传图片文件：`png`、`jpg`、`jpeg`、`tif`、`tiff`、`bmp`、`webp`
- PDF 文本解析结果过短时，自动把前几页渲染成图片后做 OCR

相关配置：

```text
OCR_ENABLED=true
OCR_LANGUAGES=chi_sim+eng
OCR_MIN_TEXT_LENGTH=40
OCR_MAX_PDF_PAGES=5
```

Python 依赖在 `backend/requirements.txt` 中，Dockerfile 已安装 Tesseract 和中英文语言包。本地非 Docker 运行时，需要额外安装 Tesseract 可执行程序。

## RAG

任务处理完成解析和分类后，会把文档正文切成 chunks 并写入 `rag_chunks` 表。当前实现是本地轻量 hybrid lexical 检索：查询会拆分英文 token、中文 bigram 和中文单字，按语料内 IDF 对低频关键词加权，并在返回片段里带上命中词和引用编号。优点是无需向量库也能演示完整 RAG 闭环，且查询结果可解释。

接口：

```text
POST /api/rag/query
POST /api/rag/reindex
```

`/api/rag/query` 在配置 LLM key 时会尝试基于检索片段生成回答；没有 key 时返回 extractive answer 和 `[1]`、`[2]` 形式的引用片段，便于面试演示“答案来自证据”。

后续可以把 `RagService.search()` 替换为 pgvector、Milvus、Qdrant 或 Elasticsearch hybrid search。

## Agent 工具链

当前任务流水线会记录一组可观测的 Agent steps：

- `document_intake_agent`：解析 PDF、Word、Excel、CSV、图片或 OCR 文本
- `router_agent`：文档分类和任务路由
- `rag_index_agent`：切块并写入本地 RAG 索引
- `extraction_agent`：LLM structured output 或规则兜底抽取
- `risk_review_agent`：合同风险规则审查
- `template_agent`：模板填充和产物生成
- `approval_coordinator_agent`：创建人工审批任务
- `human_revision_agent`：人工修订后生成新版本

这些步骤会写入 `workflow_tasks.summary.agent_trace.steps`，前端任务详情会展示 Agent、工具、输出摘要和耗时。
