# 项目讲解与学习路线

这份文档用于把项目讲清楚：你可以按这里的顺序读代码、跑演示、准备面试回答。

## 一句话讲清楚

这是一个企业文档流程自动化 Agent 工作台。它把合同、发票、报告等非结构化或半结构化文档接入系统，经过解析、OCR 兜底、RAG 索引、结构化抽取、风险审查、人工审批、审计、导出和离线评测，形成一个可观测、可回滚、可评估的 AI 工作流闭环。

## 你要抓住的主线

不要把它讲成“我做了一个文档上传工具”。正确主线是：

1. 企业文档处理需要稳定流程，不只是问一次 LLM。
2. LLM 输出必须结构化、可校验、可降级。
3. RAG 回答必须能追溯到证据片段。
4. 高风险结果不能直接自动通过，需要 human-in-the-loop。
5. AI 系统上线后要有评测和审计，才能持续优化。

## 代码阅读顺序

### 1. 入口和系统装配

- `backend/app/main.py`：FastAPI 应用入口，注册路由和启动初始化。
- `backend/app/api/`：HTTP API 层，负责参数校验、鉴权、响应模型。
- `frontend/src/App.vue`：前端工作台主页面，串起上传、任务、审批、RAG 和指标面板。

读这一层时，你要理解“用户怎么触发流程”和“前端展示了哪些 Agent 状态”。

### 2. 核心 Agent 工作流

- `backend/app/services/workflow.py`：最重要的文件，任务状态机和 Agent 编排都在这里。
- `backend/app/services/agents.py`：记录 Agent trace 和风险审查规则。
- `backend/app/models/task.py`：任务、事件、状态字段的数据模型。

面试重点讲法：

> 任务从 queued 开始，依次进入 parsing、classifying、indexing、extracting、reviewing、generating、waiting_approval。每一步都会写 TaskEvent 和 Agent trace，前端能展示进度、工具调用、输出摘要和耗时。

### 3. 文档解析和结构化抽取

- `backend/app/services/parser.py`：按文件类型解析 TXT、CSV、Excel、Word、PDF 等。
- `backend/app/services/ocr.py`：图片和扫描 PDF 的 OCR 兜底。
- `backend/app/services/extractor.py`：OpenAI-compatible 结构化抽取，失败后规则兜底。

面试重点讲法：

> 配置模型 key 时，系统优先走 JSON Schema structured output；provider 不支持时回退 JSON Object；模型请求失败或没配置 key 时用规则抽取，保证本地演示和现场答辩稳定。

### 4. RAG 检索问答

- `backend/app/services/rag.py`：文档切块、索引、检索、引用答案。
- `backend/app/api/routes_rag.py`：RAG 查询和重建索引接口。
- `scripts/evaluate_rag.py`：RAG 检索评测。

面试重点讲法：

> 当前 RAG 是轻量本地检索，不依赖向量库，适合演示完整闭环。它会对查询词做中文 bigram、英文 token 拆分和 IDF 加权，返回带引用编号和命中词的证据片段。生产环境可以替换为 pgvector、Elasticsearch hybrid search 或 Qdrant。

### 5. 审批、审计和版本

- `backend/app/api/routes_approvals.py`：审批通过、拒绝、退修。
- `backend/app/api/routes_audit.py`：审计日志查询。
- `backend/app/models/result_version.py`：结果版本记录。

面试重点讲法：

> 系统不默认信任 AI 输出。高风险结果进入审批队列；人工修订后会生成新版本，并写入审计日志，保证过程可追踪。

### 6. 评测和 CI

- `scripts/evaluate_dataset.py`：字段抽取评测，输出 precision、recall、F1。
- `scripts/evaluate_rag.py`：RAG 检索评测，输出 hit rate@K、MRR、evidence recall。
- `.github/workflows/ci.yml`：CI 会跑后端测试、抽取评测、RAG 评测和前端构建。

面试重点讲法：

> 我没有只靠主观演示判断效果，而是把抽取和检索拆成两个可离线评测的环节。抽取看字段级 precision/recall/F1，RAG 看 hit@K、MRR 和 evidence recall。

## 本地演示路线

### 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:QUEUE_BACKEND="inline"
$env:STORAGE_BACKEND="local"
uvicorn app.main:app --reload --port 8000
```

### 启动前端

```powershell
cd frontend
npm install
npm run dev
```

### 生成演示数据和评测报告

```powershell
python scripts/seed_demo.py
python scripts/evaluate_dataset.py --labels samples/eval_labels.json --report-output docs/evaluation_report.md
python scripts/evaluate_rag.py --labels samples/rag_eval_labels.json --report-output docs/rag_evaluation_report.md
```

## 3 分钟讲解稿

1. 我做的是企业文档流程自动化 Agent 工作台，不是单点聊天 demo。
2. 用户上传合同、发票或报告后，后端任务会进入解析、分类、RAG 索引、结构化抽取、风险审查、模板生成和人工审批。
3. 每一步都有事件和 Agent trace，所以前端能看到任务进度、工具调用、字段结果、风险异常和耗时。
4. 抽取层支持 OpenAI-compatible structured output，优先 JSON Schema；没模型 key 时也能用规则兜底，保证演示稳定。
5. RAG 层会返回引用片段和命中词，避免只给一个不可追溯的生成答案。
6. 最后通过审批、审计、结果版本和离线评测，把 AI 输出纳入可控流程。

## 常见面试追问

### 这个项目哪里体现 Agent？

Agent 不是只等于聊天机器人。这里的 Agent 体现在任务编排、工具调用和可观测 trace：`document_intake_agent` 负责解析，`router_agent` 负责分类，`rag_index_agent` 负责索引，`extraction_agent` 负责结构化抽取，`risk_review_agent` 负责风险审查，`approval_coordinator_agent` 负责人审流程。

### 为什么不用 LangChain / LangGraph？

当前项目先用显式 Python service 编排，是为了让状态机、数据库事务、审批和审计更清楚。生产里如果工作流分支更复杂，可以把 `workflow.py` 的编排层替换成 LangGraph，但底层解析、抽取、RAG、审批、评测服务仍然可以复用。

### 现在的 RAG 是不是太简单？

是轻量实现，不是生产级向量检索。它的价值是本地稳定、可解释、能跑通 RAG 闭环和评测。生产升级路径是 pgvector / Elasticsearch hybrid search / Qdrant，并保留现有 `RagService.search()` 接口和 `evaluate_rag.py` 评测脚本。

### 怎么保证 LLM 输出可靠？

三层控制：第一，使用 JSON Schema 或 JSON Object 约束结构化输出；第二，抽取结果进入风险审查和人工审批；第三，用离线标注集评测字段 precision、recall、F1，持续比较 prompt、模型和解析器策略。

### 项目的最大边界是什么？

当前样本集还小，RAG 是本地轻量检索，鉴权是 API Key demo 方案。真实生产需要更多标注数据、向量库或 hybrid search、多租户权限、SSO 和更完整的监控。

## 你应该熟背的文件

- `backend/app/services/workflow.py`
- `backend/app/services/extractor.py`
- `backend/app/services/rag.py`
- `backend/app/services/agents.py`
- `scripts/evaluate_dataset.py`
- `scripts/evaluate_rag.py`
- `docs/job-readiness.md`
- `docs/portfolio-case-study.md`
