<script setup lang="ts">
import type { AuditLog } from "../types/domain";

defineProps<{
  logs: AuditLog[];
}>();

function shortResource(value: string) {
  return value.length > 12 ? `${value.slice(0, 8)}...` : value;
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
</script>

<template>
  <section class="panel audit-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">审计</p>
        <h2>最近操作</h2>
      </div>
    </div>
    <div v-if="logs.length === 0" class="empty-state compact">还没有操作记录。</div>
    <div v-else class="audit-list">
      <div v-for="log in logs" :key="log.id" class="audit-row">
        <div>
          <strong>{{ log.action }}</strong>
          <time>{{ formatTime(log.created_at) }}</time>
        </div>
        <span>{{ log.actor }} · {{ log.resource_type }} · {{ shortResource(log.resource_id) }}</span>
      </div>
    </div>
  </section>
</template>
