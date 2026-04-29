<script setup lang="ts">
import { computed } from "vue";
import { api } from "../api/client";
import type { WorkflowTask } from "../types/domain";

const props = defineProps<{
  tasks: WorkflowTask[];
  selectedTaskId: string | null;
}>();

const emit = defineEmits<{
  select: [taskId: string];
}>();

const visibleTasks = computed(() => props.tasks.slice(0, 12));

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    queued: "排队中",
    running: "运行中",
    parsing: "解析",
    classifying: "分类",
    indexing: "索引",
    extracting: "抽取",
    reviewing: "审查",
    generating: "生成",
    waiting_approval: "待审批",
    approved: "已通过",
    rejected: "已拒绝",
    failed: "失败",
    needs_revision: "需修订",
    completed: "已完成",
  };
  return labels[status] ?? status;
}

function taskName(task: WorkflowTask) {
  return task.summary?.title ? String(task.summary.title) : task.classified_as || "处理中";
}

function shortId(id: string) {
  return id.slice(0, 8);
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function fieldCount(task: WorkflowTask) {
  return Object.keys(task.extracted_fields ?? {}).length;
}
</script>

<template>
  <section class="panel task-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">队列</p>
        <h2>处理进度</h2>
      </div>
      <span class="status-pill">{{ tasks.length }} 个任务</span>
    </div>

    <div v-if="visibleTasks.length === 0" class="empty-state">
      上传文件后，任务会出现在这里。
    </div>

    <div v-else class="task-list">
      <button
        v-for="task in visibleTasks"
        :key="task.id"
        class="task-row"
        :class="{ active: task.id === selectedTaskId }"
        @click="emit('select', task.id)"
      >
        <span class="task-status-dot" :class="task.status"></span>
        <span class="task-main">
          <strong>{{ taskName(task) }}</strong>
          <small>#{{ shortId(task.id) }} · {{ statusLabel(task.status) }} · {{ task.progress }}%</small>
          <small class="task-footnote">{{ fieldCount(task) }} 字段 · {{ task.anomalies.length }} 异常 · v{{ task.result_version }}</small>
        </span>
        <span class="task-meta">
          <span>P{{ task.priority }}</span>
          <span>{{ formatTime(task.updated_at) }}</span>
        </span>
        <span class="progress-track">
          <span class="progress-bar" :style="{ width: `${task.progress}%` }"></span>
        </span>
        <span class="task-actions">
          <a
            v-if="task.generated_artifact_key"
            :href="api.artifactUrl(task.id, 'markdown')"
            target="_blank"
            rel="noreferrer"
            @click.stop
          >
            MD
          </a>
          <a
            v-if="task.generated_artifact_key"
            :href="api.artifactUrl(task.id, 'docx')"
            target="_blank"
            rel="noreferrer"
            @click.stop
          >
            DOCX
          </a>
          <a
            v-if="task.generated_artifact_key"
            :href="api.artifactUrl(task.id, 'pdf')"
            target="_blank"
            rel="noreferrer"
            @click.stop
          >
            PDF
          </a>
        </span>
      </button>
    </div>
  </section>
</template>
