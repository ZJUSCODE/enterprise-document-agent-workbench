<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { api } from "../api/client";
import type { ResultVersion, WorkflowTask } from "../types/domain";

const props = defineProps<{
  task: WorkflowTask | null;
  streamState: "idle" | "connecting" | "live" | "closed" | "fallback";
}>();

const emit = defineEmits<{
  refresh: [];
  error: [message: string];
}>();

interface AgentStep {
  agent: string;
  tool: string;
  input_summary: string;
  output_summary: string;
  status: string;
  duration_ms: number;
}

const revisedBy = ref("reviewer.demo");
const revisionComment = ref("");
const fieldsText = ref("{}");
const anomaliesText = ref("[]");
const savingRevision = ref(false);
const versions = ref<ResultVersion[]>([]);
const loadingVersions = ref(false);

const fields = computed(() => Object.entries(props.task?.extracted_fields ?? {}));
const anomalies = computed(() => props.task?.anomalies ?? []);
const events = computed(() => props.task?.events ?? []);
const keyPoints = computed(() => (props.task?.summary?.key_points as string[] | undefined) ?? []);
const riskReview = computed(() => props.task?.summary?.risk_review as Record<string, unknown> | undefined);
const agentSteps = computed(() => {
  const trace = props.task?.summary?.agent_trace as { steps?: AgentStep[] } | undefined;
  return trace?.steps ?? [];
});
const taskSnapshot = computed(() => {
  if (!props.task) return [];
  return [
    { label: "任务 ID", value: props.task.id.slice(0, 8) },
    { label: "文档类型", value: props.task.classified_as ?? "待分类" },
    { label: "结果版本", value: `v${props.task.result_version}` },
    { label: "重试次数", value: `${props.task.retry_count}/${props.task.max_retries}` },
  ];
});

const exportLinks = computed(() => {
  if (!props.task?.generated_artifact_key) return [];
  return [
    { label: "Markdown", href: api.artifactUrl(props.task.id, "markdown") },
    { label: "DOCX", href: api.artifactUrl(props.task.id, "docx") },
    { label: "PDF", href: api.artifactUrl(props.task.id, "pdf") },
    { label: "TXT", href: api.artifactUrl(props.task.id, "txt") },
  ];
});

const streamLabel = computed(() => {
  const labels = {
    idle: "未连接",
    connecting: "连接中",
    live: "SSE 实时",
    closed: "流已完成",
    fallback: "轮询兜底",
  };
  return labels[props.streamState];
});

watch(
  () => props.task,
  (task) => {
    fieldsText.value = JSON.stringify(task?.extracted_fields ?? {}, null, 2);
    anomaliesText.value = JSON.stringify(task?.anomalies ?? [], null, 2);
  },
  { immediate: true },
);

watch(
  () => props.task?.id,
  async (taskId) => {
    versions.value = [];
    if (!taskId) return;
    loadingVersions.value = true;
    try {
      versions.value = await api.listTaskVersions(taskId);
    } catch {
      versions.value = [];
    } finally {
      loadingVersions.value = false;
    }
  },
  { immediate: true },
);

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function saveRevision() {
  if (!props.task) return;
  savingRevision.value = true;
  try {
    const extractedFields = JSON.parse(fieldsText.value) as Record<string, unknown>;
    const anomalies = JSON.parse(anomaliesText.value) as Record<string, unknown>[];
    await api.reviseTask(props.task.id, {
      extracted_fields: extractedFields,
      anomalies,
      revised_by: revisedBy.value,
      comment: revisionComment.value || undefined,
    });
    revisionComment.value = "";
    emit("refresh");
  } catch (error) {
    emit("error", error instanceof Error ? error.message : "保存失败，请检查 JSON 格式");
  } finally {
    savingRevision.value = false;
  }
}
</script>

<template>
  <section class="panel detail-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">结果</p>
        <h2>{{ task ? "抽取与审查" : "等待任务" }}</h2>
      </div>
      <div v-if="task" class="detail-status-group">
        <span class="status-pill" :class="task.status">{{ task.status }}</span>
        <span class="stream-pill" :class="streamState">{{ streamLabel }}</span>
      </div>
    </div>

    <div v-if="!task" class="empty-state">
      选择一个任务后，这里会展示摘要、字段、风险和 Agent 步骤。
    </div>

    <div v-else class="detail-flow">
      <div class="task-snapshot">
        <div v-for="item in taskSnapshot" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>

      <section class="export-band">
        <div>
          <span>产物导出</span>
          <strong>{{ exportLinks.length ? "结果已生成" : "等待生成" }}</strong>
        </div>
        <div class="export-links">
          <a v-for="link in exportLinks" :key="link.label" :href="link.href" target="_blank" rel="noreferrer">
            {{ link.label }}
          </a>
        </div>
      </section>

      <section class="summary-band">
        <span>摘要</span>
        <p>{{ formatValue(task.summary.brief) }}</p>
        <ul v-if="keyPoints.length">
          <li v-for="point in keyPoints.slice(0, 3)" :key="point">{{ point }}</li>
        </ul>
      </section>

      <section class="detail-section">
        <div class="section-title">
          <h3>关键字段</h3>
          <span>{{ fields.length }} 项</span>
        </div>
        <dl class="field-list">
          <template v-for="[key, value] in fields" :key="key">
            <dt>{{ key }}</dt>
            <dd>{{ formatValue(value) }}</dd>
          </template>
        </dl>
      </section>

      <section class="detail-section">
        <div class="section-title">
          <h3>风险与异常</h3>
          <span>{{ anomalies.length }} 条</span>
        </div>
        <p v-if="riskReview" class="risk-line">
          风险等级：{{ riskReview.risk_level ?? "low" }} · 命中 {{ riskReview.risk_count ?? 0 }} 条规则
        </p>
        <div v-if="anomalies.length === 0" class="quiet-line">当前没有需要处理的异常。</div>
        <div v-for="anomaly in anomalies" v-else :key="JSON.stringify(anomaly)" class="anomaly-row">
          <strong>{{ anomaly.severity ?? "info" }}</strong>
          <span>{{ anomaly.message ?? anomaly.code }}</span>
        </div>
      </section>

      <details class="soft-disclosure" open>
        <summary>Agent 工具链</summary>
        <div v-if="agentSteps.length === 0" class="quiet-line">任务完成后会显示每一步工具调用。</div>
        <div v-for="step in agentSteps" :key="`${step.agent}-${step.tool}-${step.duration_ms}`" class="agent-step">
          <div>
            <strong>{{ step.agent }}</strong>
            <span class="status-pill">{{ step.status }}</span>
          </div>
          <p>{{ step.tool }} · {{ step.output_summary }}</p>
          <span>{{ step.input_summary }} · {{ step.duration_ms }}ms</span>
        </div>
      </details>

      <details class="soft-disclosure" open>
        <summary>事件时间线</summary>
        <div v-if="events.length === 0" class="quiet-line">暂无任务事件。</div>
        <div v-for="event in events" :key="event.id" class="event-row">
          <span class="event-progress">{{ event.progress }}%</span>
          <div>
            <strong>{{ event.message }}</strong>
            <span>{{ event.status }} · {{ event.level }} · {{ formatTime(event.created_at) }}</span>
          </div>
        </div>
      </details>

      <details class="soft-disclosure">
        <summary>版本历史</summary>
        <div v-if="loadingVersions" class="quiet-line">正在加载版本。</div>
        <div v-else-if="versions.length === 0" class="quiet-line">暂无结果版本。</div>
        <template v-else>
          <div v-for="version in versions" :key="version.id" class="version-row">
            <div>
              <strong>v{{ version.version }}</strong>
              <span>{{ version.created_by }} · {{ formatTime(version.created_at) }}</span>
            </div>
            <span>{{ Object.keys(version.extracted_fields).length }} 字段 · {{ version.anomalies.length }} 异常</span>
          </div>
        </template>
      </details>

      <details class="soft-disclosure">
        <summary>人工修订</summary>
        <div class="form-grid single">
          <label>
            <span>修订人</span>
            <input v-model="revisedBy" type="text" />
          </label>
          <label>
            <span>修订说明</span>
            <input v-model="revisionComment" type="text" placeholder="例如：补齐金额字段" />
          </label>
        </div>
        <div class="revision-grid">
          <label>
            <span>字段 JSON</span>
            <textarea v-model="fieldsText" rows="10"></textarea>
          </label>
          <label>
            <span>异常 JSON</span>
            <textarea v-model="anomaliesText" rows="10"></textarea>
          </label>
        </div>
        <button :disabled="savingRevision" @click="saveRevision">
          {{ savingRevision ? "正在保存" : "保存修订并重新送审" }}
        </button>
      </details>
    </div>
  </section>
</template>
