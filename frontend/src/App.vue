<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { api } from "./api/client";
import ApprovalQueue from "./components/ApprovalQueue.vue";
import AuditLogPanel from "./components/AuditLogPanel.vue";
import MetricsPanel from "./components/MetricsPanel.vue";
import RagPanel from "./components/RagPanel.vue";
import TaskDetail from "./components/TaskDetail.vue";
import TaskTable from "./components/TaskTable.vue";
import UploadPanel from "./components/UploadPanel.vue";
import type { Approval, AuditLog, DocumentFile, EvaluationSummary, TemplateDefinition, WorkflowTask } from "./types/domain";

const files = ref<DocumentFile[]>([]);
const templates = ref<TemplateDefinition[]>([]);
const tasks = ref<WorkflowTask[]>([]);
const approvals = ref<Approval[]>([]);
const logs = ref<AuditLog[]>([]);
const metrics = ref<EvaluationSummary | null>(null);
const selectedTaskId = ref<string | null>(null);
const selectedTask = ref<WorkflowTask | null>(null);
const loading = ref(false);
const errorMessage = ref("");
const apiKey = ref(window.localStorage.getItem("workflow_api_key") ?? "");
const streamState = ref<"idle" | "connecting" | "live" | "closed" | "fallback">("idle");
let pollTimer: number | undefined;
let taskEventSource: EventSource | undefined;

const agentPipeline = [
  { step: "01", title: "接入", detail: "多格式上传、校验与元数据记录" },
  { step: "02", title: "理解", detail: "解析、OCR 兜底与文档分类" },
  { step: "03", title: "检索", detail: "本地 RAG 分块、索引与引用回答" },
  { step: "04", title: "执行", detail: "结构化抽取、风险规则与模板生成" },
  { step: "05", title: "治理", detail: "人工审批、版本修订与审计日志" },
];

const systemHighlights = [
  "OpenAI-compatible 结构化抽取",
  "规则兜底，离线可演示",
  "Celery 异步任务与重试",
  "审批、审计、评测闭环",
];

const activeTasks = computed(() =>
  tasks.value.filter((task) => !["approved", "completed", "rejected", "failed"].includes(task.status)),
);

const completedCount = computed(() =>
  tasks.value.filter((task) => ["approved", "completed"].includes(task.status)).length,
);

const highRiskCount = computed(
  () =>
    tasks.value.filter((task) =>
      task.anomalies.some((anomaly) => String(anomaly.severity ?? "").toLowerCase().includes("high")),
    ).length,
);

function percent(value: number | null | undefined) {
  if (typeof value !== "number" || Number.isNaN(value)) return "--";
  return `${Math.round(value * 100)}%`;
}

const commandMetrics = computed(() => [
  {
    label: "文档样本",
    value: String(files.value.length),
    caption: "已接入文件",
  },
  {
    label: "任务总量",
    value: String(tasks.value.length),
    caption: `${activeTasks.value.length} 个处理中`,
  },
  {
    label: "成功率",
    value: percent(metrics.value?.success_rate),
    caption: "来自评测接口",
  },
  {
    label: "抽取质量",
    value: percent(metrics.value?.extraction_accuracy_proxy),
    caption: "字段质量代理",
  },
]);

function fulfilledValue<T>(result: PromiseSettledResult<T>): T | null {
  return result.status === "fulfilled" ? result.value : null;
}

const systemState = computed(() => {
  if (errorMessage.value) {
    return {
      label: "后端未连接",
      detail: "请确认 FastAPI 服务运行在 8000 端口",
      tone: "warning",
    };
  }
  if (activeTasks.value.length > 0) {
    return {
      label: "Agent 运行中",
      detail: `${activeTasks.value.length} 个任务正在推进`,
      tone: "active",
    };
  }
  return {
    label: "演示环境在线",
    detail: "可以上传样本或查看已处理结果",
    tone: "ready",
  };
});

const nextAction = computed(() => {
  if (errorMessage.value) return "连接未恢复。系统会继续刷新，你也可以确认后端 8000 是否启动。";
  if (approvals.value.length > 0) return `有 ${approvals.value.length} 个结果待审批，先处理审批队列。`;
  if (activeTasks.value.length > 0) return "任务正在处理。打开任务详情查看 Agent 步骤和抽取结果。";
  if (tasks.value.length > 0) return "可以上传新文件，或用 RAG 检索已处理文档。";
  return "先上传一份合同、发票或表格，系统会自动处理。";
});

async function loadAll() {
  loading.value = true;
  const results = await Promise.allSettled([
    api.listFiles(),
    api.listTemplates(),
    api.listTasks(),
    api.listApprovals(),
    api.listAudit(),
    api.getMetrics(),
  ]);
  const [fileResult, templateResult, taskResult, approvalResult, logResult, metricResult] = results;
  const fileData = fulfilledValue(fileResult);
  const templateData = fulfilledValue(templateResult);
  const taskData = fulfilledValue(taskResult);
  const approvalData = fulfilledValue(approvalResult);
  const logData = fulfilledValue(logResult);
  const metricData = fulfilledValue(metricResult);
  const successCount = results.filter((result) => result.status === "fulfilled").length;

  if (fileData) files.value = fileData;
  if (templateData) templates.value = templateData;
  if (taskData) {
    tasks.value = taskData;
    errorMessage.value = "";
    if (!selectedTaskId.value || !taskData.some((task) => task.id === selectedTaskId.value)) {
      selectedTaskId.value = taskData[0]?.id ?? null;
    }
    await loadSelectedTask();
  }
  if (approvalData) approvals.value = approvalData;
  if (logData) logs.value = logData;
  if (metricData) metrics.value = metricData;

  if (successCount === 0) {
    const firstError = results.find((result) => result.status === "rejected") as PromiseRejectedResult | undefined;
    errorMessage.value =
      firstError?.reason instanceof Error ? firstError.reason.message : "无法连接到后端，正在继续重试。";
  } else if (successCount < results.length && !taskData) {
    errorMessage.value = "部分接口暂不可用，页面会保留最近一次可用数据并继续刷新。";
  } else {
    errorMessage.value = "";
  }
  loading.value = false;
}

async function loadSelectedTask() {
  if (!selectedTaskId.value) {
    selectedTask.value = null;
    return;
  }
  try {
    selectedTask.value = await api.getTask(selectedTaskId.value);
  } catch {
    selectedTask.value = null;
  }
}

function closeTaskStream() {
  if (taskEventSource) {
    taskEventSource.close();
    taskEventSource = undefined;
  }
  streamState.value = selectedTaskId.value ? "fallback" : "idle";
}

function openTaskStream(taskId: string) {
  closeTaskStream();
  if (!window.EventSource) {
    streamState.value = "fallback";
    return;
  }
  streamState.value = "connecting";
  taskEventSource = new EventSource(api.taskEventStreamUrl(taskId));
  taskEventSource.addEventListener("open", () => {
    streamState.value = "live";
  });
  taskEventSource.addEventListener("task_event", () => {
    void loadSelectedTask();
  });
  taskEventSource.addEventListener("done", () => {
    streamState.value = "closed";
    taskEventSource?.close();
    taskEventSource = undefined;
    void loadSelectedTask();
  });
  taskEventSource.addEventListener("error", () => {
    streamState.value = "fallback";
    taskEventSource?.close();
    taskEventSource = undefined;
  });
}

async function selectTask(taskId: string) {
  selectedTaskId.value = taskId;
  await loadSelectedTask();
}

function handleError(message: string) {
  errorMessage.value = `${message}。系统会保留当前页面，你可以稍后重试。`;
}

function saveApiKey() {
  const value = apiKey.value.trim();
  if (value) {
    window.localStorage.setItem("workflow_api_key", value);
  } else {
    window.localStorage.removeItem("workflow_api_key");
  }
  void loadAll();
}

onMounted(() => {
  void loadAll();
  pollTimer = window.setInterval(() => {
    void loadAll();
  }, 4000);
});

watch(selectedTaskId, (taskId) => {
  if (taskId) {
    openTaskStream(taskId);
  } else {
    closeTaskStream();
  }
});

onUnmounted(() => {
  if (pollTimer) window.clearInterval(pollTimer);
  closeTaskStream();
});
</script>

<template>
  <div class="app-shell">
    <aside class="context-rail">
      <div class="brand-visual" aria-hidden="true">
        <div class="visual-node visual-node-primary">AI</div>
        <div class="visual-lane">
          <span>OCR</span>
          <span>RAG</span>
          <span>Eval</span>
        </div>
        <div class="visual-grid">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div class="brand-block">
        <p class="eyebrow">Document Agent</p>
        <h1>企业文档流程自动化</h1>
        <p>一个可本地演示的 AI Agent 工作台，覆盖文档接入、理解、检索、审批、审计和评测。</p>
      </div>

      <div class="state-card" :class="systemState.tone">
        <span>系统状态</span>
        <strong>{{ systemState.label }}</strong>
        <p>{{ systemState.detail }}</p>
      </div>

      <div class="status-stack">
        <div>
          <span>处理中</span>
          <strong>{{ activeTasks.length }}</strong>
        </div>
        <div>
          <span>待审批</span>
          <strong>{{ approvals.length }}</strong>
        </div>
        <div>
          <span>高风险</span>
          <strong>{{ highRiskCount }}</strong>
        </div>
      </div>

      <div class="next-action">
        <span>下一步</span>
        <p>{{ nextAction }}</p>
      </div>

      <details class="soft-disclosure">
        <summary>连接与权限</summary>
        <label class="api-key-field">
          <span>API Key</span>
          <input v-model="apiKey" type="password" placeholder="开启鉴权后填写" @change="saveApiKey" />
        </label>
        <button class="secondary full" :disabled="loading" @click="loadAll">
          {{ loading ? "正在刷新" : "刷新数据" }}
        </button>
      </details>
    </aside>

    <main class="workspace">
      <section class="command-center">
        <div class="command-copy">
          <p class="eyebrow">AI Agent Workbench</p>
          <h2>
            <span class="title-wide">从非结构化文档到可审计结果</span>
            <span class="title-compact">文档 Agent 可审计工作台</span>
          </h2>
          <p>
            后端编排解析、OCR、RAG、结构化抽取、风险审查和模板生成；前端提供任务观测、人工审批、RAG
            问答和质量指标。
          </p>
          <div class="highlight-row">
            <span v-for="highlight in systemHighlights" :key="highlight">{{ highlight }}</span>
          </div>
        </div>
        <div class="command-metrics" aria-label="运行指标">
          <div v-for="metric in commandMetrics" :key="metric.label" class="metric-card">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
            <small>{{ metric.caption }}</small>
          </div>
        </div>
      </section>

      <section class="agent-map" aria-label="Agent 处理链路">
        <div v-for="stage in agentPipeline" :key="stage.step" class="pipeline-stage">
          <span>{{ stage.step }}</span>
          <strong>{{ stage.title }}</strong>
          <p>{{ stage.detail }}</p>
        </div>
      </section>

      <div class="work-header">
        <div>
          <p class="eyebrow">工作流</p>
          <h2>处理一份文档</h2>
        </div>
        <span class="connection-pill" :class="{ warning: errorMessage }">
          {{ errorMessage ? "正在重试" : "系统在线" }}
        </span>
      </div>

      <div v-if="errorMessage" class="alert">
        {{ errorMessage }}
      </div>

      <UploadPanel :files="files" :templates="templates" @refresh="loadAll" @error="handleError" />

      <section class="workflow-grid">
        <TaskTable :tasks="tasks" :selected-task-id="selectedTaskId" @select="selectTask" />
        <TaskDetail :task="selectedTask" :stream-state="streamState" @refresh="loadAll" @error="handleError" />
      </section>

      <section class="assist-grid">
        <ApprovalQueue :approvals="approvals" @refresh="loadAll" @error="handleError" />
        <RagPanel @error="handleError" />
      </section>

      <section class="insight-grid">
        <MetricsPanel :metrics="metrics" />
        <AuditLogPanel :logs="logs" />
      </section>
    </main>
  </div>
</template>
