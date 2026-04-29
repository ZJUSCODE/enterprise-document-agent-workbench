# Portfolio Case Study: Enterprise Document Agent Workbench

## 一句话定位

这是一个面向企业内部合同、发票、表格和扫描件处理的 AI Agent 工作台。它不是单次聊天式 demo，而是把文档接入、解析、RAG、结构化抽取、风险审查、审批、审计、导出和评测串成一个可运行闭环。

## 适合投递的岗位方向

- AI 应用工程师
- Agent 工作流工程师
- LLM 后端工程师
- 企业级 AI 产品前端 / 全栈工程师
- 文档智能、知识库、审批自动化相关岗位

## 可以重点讲的能力

### 1. Agent 工作流编排

任务从 `queued` 开始，依次经过解析、分类、RAG 索引、结构化抽取、风险审查、模板生成和人工审批。每个步骤都会写入事件和 Agent trace，前端可以回放工具链和耗时。

### 2. LLM 结构化输出工程

后端通过 OpenAI-compatible API 接入模型，优先使用 JSON Schema 约束输出；provider 不支持时回退到 JSON Object；未配置 key 时使用规则抽取兜底，保证演示稳定。

### 3. RAG 闭环

处理任务时自动把文档切块写入本地索引。用户可以在前端提问，系统返回答案、引用片段和命中词。当前实现是带 IDF 权重的轻量词法检索，后续可替换为 pgvector、Milvus、Qdrant 或 Elasticsearch hybrid search。

### 4. Human-in-the-loop

系统不会假设 AI 输出天然可信。高风险或待确认结果进入审批队列，人工可以通过、退修或拒绝；修订会生成新的结果版本，并写入审计日志。

### 5. 质量与可维护性

项目包含在线指标、离线标注集评测脚本、后端测试、前端构建检查和 GitHub Actions CI。评测结果可以用于比较不同 prompt、模型和解析器策略。

## 技术栈

- Frontend: Vue 3, TypeScript, Vite
- Backend: FastAPI, SQLAlchemy, Pydantic
- Async: Celery, Redis, FastAPI BackgroundTasks fallback
- Storage: Local filesystem, MinIO-compatible storage
- Database: SQLite for local demo, PostgreSQL for production
- AI: OpenAI-compatible structured output, DeepSeek/SiliconFlow/OpenAI endpoint support
- Document Processing: PyMuPDF, pypdf, python-docx, openpyxl, pytesseract
- QA: pytest, vue-tsc, Vite build, GitHub Actions

## 3 分钟演示脚本

1. 打开前端，先讲首屏指标和 Agent 链路：接入、理解、检索、执行、治理。
2. 上传 `samples/contract_sample.txt`，选择合同审查模板并开始处理。
3. 打开任务详情，展示字段抽取、风险异常、Agent 工具链、SSE 事件时间线、结果版本和 Markdown / DOCX / PDF 导出入口。
4. 在 RAG 面板提问“这份合同的付款方式和违约责任是什么？”，展示引用片段。
5. 在审批队列通过或退修结果，说明 human-in-the-loop 和审计日志如何保证可控。

## 可以承认的当前边界

- 当前 RAG 是本地轻量检索，不是生产级向量检索；优势是演示稳定、证据可解释，生产可替换为向量库或 hybrid search。
- 离线标注集样本数量较少，适合作为评测框架示例，不代表生产精度。
- 默认鉴权是 API Key 方案，真实企业部署应接 SSO 或网关注入身份。
- 产物导出已支持 Markdown、TXT、DOCX、PDF。PDF 是轻量模板导出，复杂企业版式仍建议接专业模板引擎。

## 下一步路线图

1. 增加更多标注文档，输出字段级 precision、recall、F1。
2. 把本地 RAG 替换为 pgvector 或 Elasticsearch hybrid search。
3. 增加 PDF 导出和可配置企业模板。
4. 增加组织、角色、SSO 和多租户数据隔离。
5. 将 Agent trace 标准化为 OpenTelemetry span 或兼容 LangSmith / Phoenix 的 trace。
