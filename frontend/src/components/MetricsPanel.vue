<script setup lang="ts">
import { computed } from "vue";
import type { EvaluationSummary } from "../types/domain";

const props = defineProps<{
  metrics: EvaluationSummary | null;
}>();

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

const statusEntries = computed(() => Object.entries(props.metrics?.status_breakdown ?? {}).slice(0, 6));
const anomalyEntries = computed(() => Object.entries(props.metrics?.anomaly_breakdown ?? {}).slice(0, 6));
</script>

<template>
  <section class="panel metrics-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">评测</p>
        <h2>质量指标</h2>
      </div>
    </div>
    <div v-if="!metrics" class="empty-state compact">暂无指标，完成一个任务后会自动更新。</div>
    <div v-else class="metrics-layout">
      <div class="metric-grid">
        <div class="metric">
          <span>任务总量</span>
          <strong>{{ metrics.total_tasks }}</strong>
        </div>
        <div class="metric">
          <span>成功率</span>
          <strong>{{ percent(metrics.success_rate) }}</strong>
        </div>
        <div class="metric">
          <span>人工接管</span>
          <strong>{{ percent(metrics.manual_takeover_rate) }}</strong>
        </div>
        <div class="metric">
          <span>抽取质量</span>
          <strong>{{ percent(metrics.extraction_accuracy_proxy) }}</strong>
        </div>
        <div class="metric">
          <span>平均耗时</span>
          <strong>{{ metrics.average_duration_seconds }}s</strong>
        </div>
      </div>
      <div class="breakdown-grid">
        <div>
          <h3>状态分布</h3>
          <div v-if="statusEntries.length === 0" class="quiet-line">暂无状态样本。</div>
          <div v-for="[status, count] in statusEntries" :key="status" class="breakdown-row">
            <span>{{ status }}</span>
            <strong>{{ count }}</strong>
          </div>
        </div>
        <div>
          <h3>异常分布</h3>
          <div v-if="anomalyEntries.length === 0" class="quiet-line">暂无异常样本。</div>
          <div v-for="[status, count] in anomalyEntries" :key="status" class="breakdown-row">
            <span>{{ status }}</span>
            <strong>{{ count }}</strong>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
