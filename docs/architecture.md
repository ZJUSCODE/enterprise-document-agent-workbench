# 架构说明

## 服务分层

- API 层：负责请求校验、响应序列化和错误码。
- Service 层：承载业务流程，包括解析、分类、抽取、模板生成、评测和审计。
- OCR 层：图片和扫描 PDF 的可选 OCR 兜底。
- RAG 层：文档切块、索引和检索问答。
- Agent 工具链：记录每个工具调用式 Agent 步骤，形成可观测 trace。
- Worker 层：承载异步任务。`QUEUE_BACKEND=celery` 时进入 Redis/Celery；`inline` 时由 FastAPI BackgroundTasks 执行。
- Storage 层：支持本地文件夹和 MinIO，两者都使用统一 storage key。
- DB 层：使用 SQLAlchemy ORM，生产推荐 PostgreSQL，本地可用 SQLite。

## 任务状态机

```text
queued -> running -> parsing -> classifying -> extracting -> generating -> waiting_approval
waiting_approval -> approved
waiting_approval -> rejected
waiting_approval -> needs_revision
* -> failed
```

增强版流程：

```text
queued -> running -> parsing -> classifying -> indexing -> extracting -> reviewing -> generating -> waiting_approval
```

每次状态变化都会写入 `task_events`，用于进度轮询、SSE 推送和审计回放。前端任务详情优先接入 `/events/stream`，连接失败时保留轮询兜底。

## 数据对象

- `document_files`：上传文件元数据、存储键、解析器和解析警告。
- `workflow_tasks`：流程任务、状态、进度、抽取结果、异常字段和导出产物。
- `approvals`：人工审批记录。
- `audit_logs`：操作日志。
- `result_versions`：每次生成结果的版本记录。
- `template_definitions`：模板定义。
- `rag_chunks`：RAG 检索片段。

## 产物导出

模板引擎先生成 Markdown 文本，再按请求格式导出：

- Markdown：保留原始模板产物。
- DOCX：使用 `python-docx` 生成可编辑文档。
- PDF：使用 ReportLab 生成轻量可交付 PDF，支持中文字体。
- TXT：用于纯文本系统集成或调试。

## 安全模型

默认关闭 API Key 鉴权，方便本地展示。生产部署时设置：

```text
API_AUTH_ENABLED=true
API_KEYS=token:actor:admin|operator|reviewer|viewer
```

后端根据角色控制写操作：

- `operator`：上传文件、创建任务。
- `reviewer`：审批和修订结果。
- `admin`：拥有全部角色权限。
