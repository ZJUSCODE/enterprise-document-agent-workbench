<script setup lang="ts">
import { ref } from "vue";
import { api } from "../api/client";
import type { Approval } from "../types/domain";

defineProps<{
  approvals: Approval[];
}>();

const emit = defineEmits<{
  refresh: [];
  error: [message: string];
}>();

const reviewer = ref("reviewer.demo");
const comment = ref("");
const busyId = ref<string | null>(null);

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

async function decide(approval: Approval, decision: "approved" | "rejected" | "needs_revision") {
  busyId.value = approval.id;
  try {
    await api.decideApproval(approval.id, {
      decision,
      reviewer: reviewer.value,
      comment: comment.value || undefined,
    });
    comment.value = "";
    emit("refresh");
  } catch (error) {
    emit("error", error instanceof Error ? error.message : "审批失败，请检查权限后重试");
  } finally {
    busyId.value = null;
  }
}
</script>

<template>
  <section class="panel approval-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">审批</p>
        <h2>需要确认的结果</h2>
      </div>
      <span class="status-pill">{{ approvals.length }} 待处理</span>
    </div>

    <div v-if="approvals.length === 0" class="empty-state compact">
      当前没有待审批任务。
    </div>

    <div v-else class="approval-list">
      <div class="form-grid single">
        <label>
          <span>审批人</span>
          <input v-model="reviewer" type="text" />
        </label>
        <label>
          <span>意见</span>
          <input v-model="comment" type="text" placeholder="可选" />
        </label>
      </div>

      <div v-for="approval in approvals" :key="approval.id" class="approval-row">
        <div>
          <strong>任务 #{{ shortId(approval.task_id) }}</strong>
          <span>{{ formatTime(approval.created_at) }} 创建 · 等待人工确认</span>
        </div>
        <div class="actions narrow">
          <button :disabled="busyId === approval.id" @click="decide(approval, 'approved')">通过</button>
          <button class="secondary" :disabled="busyId === approval.id" @click="decide(approval, 'needs_revision')">
            退修
          </button>
          <button class="danger" :disabled="busyId === approval.id" @click="decide(approval, 'rejected')">拒绝</button>
        </div>
      </div>
    </div>
  </section>
</template>
