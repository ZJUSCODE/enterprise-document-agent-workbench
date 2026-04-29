import type {
  Approval,
  AuditLog,
  DocumentFile,
  EvaluationSummary,
  RagAnswer,
  ResultVersion,
  TemplateDefinition,
  WorkflowTask,
} from "../types/domain";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

function authHeaders(): HeadersInit {
  const apiKey = window.localStorage.getItem("workflow_api_key");
  return apiKey ? { "X-API-Key": apiKey } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(typeof body.detail === "string" ? body.detail : response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listFiles: () => request<DocumentFile[]>("/files"),
  uploadFile: async (file: File, actor: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("actor", actor);
    return request<DocumentFile>("/files/upload", { method: "POST", body: form });
  },
  listTemplates: () => request<TemplateDefinition[]>("/templates"),
  createTask: (payload: { file_id: string; template_id: string; submitted_by: string; priority: number }) =>
    request<WorkflowTask>("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  createBatchTasks: (payload: { file_ids: string[]; template_id: string; submitted_by: string; priority: number }) =>
    request<WorkflowTask[]>("/tasks/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  listTasks: () => request<WorkflowTask[]>("/tasks"),
  getTask: (taskId: string) => request<WorkflowTask>(`/tasks/${taskId}`),
  listTaskVersions: (taskId: string) => request<ResultVersion[]>(`/tasks/${taskId}/versions`),
  reviseTask: (
    taskId: string,
    payload: {
      extracted_fields?: Record<string, unknown>;
      summary?: Record<string, unknown>;
      anomalies?: Record<string, unknown>[];
      revised_by: string;
      comment?: string;
    },
  ) =>
    request<WorkflowTask>(`/tasks/${taskId}/result`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  listApprovals: () => request<Approval[]>("/approvals?status=pending"),
  decideApproval: (approvalId: string, payload: { decision: string; reviewer: string; comment?: string }) =>
    request<Approval>(`/approvals/${approvalId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  listAudit: () => request<AuditLog[]>("/audit?limit=80"),
  getMetrics: () => request<EvaluationSummary>("/metrics/evaluation"),
  queryRag: (payload: { question: string; top_k: number; document_type?: string; file_id?: string }) =>
    request<RagAnswer>("/rag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  reindexRag: () =>
    request<{ indexed_tasks: number; indexed_chunks: number }>("/rag/reindex", {
      method: "POST",
    }),
  artifactUrl: (taskId: string, format = "markdown") => `${API_BASE}/tasks/${taskId}/export?format=${format}`,
  taskEventStreamUrl: (taskId: string) => `${API_BASE}/tasks/${taskId}/events/stream`,
};
