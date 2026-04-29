# API 摘要

## 文件

- `POST /api/files/upload`
- `GET /api/files`
- `GET /api/files/{file_id}`

## 任务

- `POST /api/tasks`
- `POST /api/tasks/batch`
- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/events`
- `GET /api/tasks/{task_id}/events/stream`
- `GET /api/tasks/{task_id}/versions`
- `PATCH /api/tasks/{task_id}/result`
- `GET /api/tasks/{task_id}/export?format=markdown`
- `GET /api/tasks/{task_id}/export?format=docx`
- `GET /api/tasks/{task_id}/export?format=txt`
- `GET /api/tasks/{task_id}/export?format=pdf`

`/events/stream` 使用 Server-Sent Events。事件类型：

- `task_event`：任务状态、进度和消息增量
- `done`：任务进入 `approved`、`completed`、`rejected` 或 `failed` 等终态后关闭流

## 审批

- `GET /api/approvals?status=pending`
- `POST /api/approvals/{approval_id}/decision`

`decision` 支持：

- `approved`
- `rejected`
- `needs_revision`

## 审计和评测

- `GET /api/audit`
- `GET /api/metrics/evaluation`

## RAG

- `POST /api/rag/query`
- `POST /api/rag/reindex`

Query body:

```json
{
  "question": "合同付款方式是什么？",
  "top_k": 5,
  "document_type": "contract"
}
```

## 鉴权

默认 `API_AUTH_ENABLED=false`，方便本地演示。启用后，写操作需要请求头：

```text
X-API-Key: <token>
```

`API_KEYS` 格式：

```text
token:actor:role1|role2
```

内置角色：

- `admin`
- `operator`
- `reviewer`
- `viewer`

## 模板

- `GET /api/templates`
- `GET /api/templates/{template_id}`
