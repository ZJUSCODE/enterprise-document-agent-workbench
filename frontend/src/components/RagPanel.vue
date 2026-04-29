<script setup lang="ts">
import { ref } from "vue";
import { api } from "../api/client";
import type { RagAnswer } from "../types/domain";

const emit = defineEmits<{
  error: [message: string];
}>();

const question = ref("这份合同的付款方式和违约责任是什么？");
const topK = ref(5);
const documentType = ref("");
const result = ref<RagAnswer | null>(null);
const busy = ref(false);

const sampleQuestions = [
  "这份合同的付款方式和违约责任是什么？",
  "有哪些需要人工复核的风险点？",
  "提取发票金额、日期和供应商。",
];

async function ask() {
  if (!question.value.trim()) return;
  busy.value = true;
  try {
    result.value = await api.queryRag({
      question: question.value,
      top_k: topK.value,
      document_type: documentType.value || undefined,
    });
  } catch (error) {
    emit("error", error instanceof Error ? error.message : "检索失败，正在等待下一次请求");
  } finally {
    busy.value = false;
  }
}

function setQuestion(value: string) {
  question.value = value;
}

function formatScore(value: number) {
  return value.toFixed(2);
}

async function reindex() {
  busy.value = true;
  try {
    const payload = await api.reindexRag();
    result.value = {
      question: "重新索引",
      answer: `已索引 ${payload.indexed_tasks} 个任务，生成 ${payload.indexed_chunks} 个片段。`,
      hits: [],
    };
  } catch (error) {
    emit("error", error instanceof Error ? error.message : "重建索引失败，请稍后重试");
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="panel rag-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">RAG</p>
        <h2>向文档提问</h2>
      </div>
      <span class="status-pill">引用片段</span>
    </div>
    <div class="question-chips" aria-label="常用问题">
      <button
        v-for="sample in sampleQuestions"
        :key="sample"
        class="chip-button"
        type="button"
        @click="setQuestion(sample)"
      >
        {{ sample }}
      </button>
    </div>
    <div class="rag-form">
      <label>
        <span>问题</span>
        <input v-model="question" type="text" @keyup.enter="ask" />
      </label>
      <label>
        <span>类型</span>
        <select v-model="documentType">
          <option value="">全部</option>
          <option value="contract">合同</option>
          <option value="invoice">发票</option>
          <option value="spreadsheet">表格</option>
        </select>
      </label>
      <label>
        <span>片段数</span>
        <input v-model.number="topK" min="1" max="20" type="number" />
      </label>
      <button :disabled="busy" @click="ask">{{ busy ? "检索中" : "提问" }}</button>
      <button class="secondary" :disabled="busy" @click="reindex">重建索引</button>
    </div>
    <div v-if="result" class="rag-result">
      <h3>回答</h3>
      <p>{{ result.answer }}</p>
      <h3 v-if="result.hits.length">引用</h3>
      <div v-for="hit in result.hits" :key="hit.chunk_id" class="rag-hit">
        <strong>{{ hit.document_type || "document" }} · score {{ formatScore(hit.score) }}</strong>
        <span>{{ hit.text }}</span>
      </div>
    </div>
  </section>
</template>
