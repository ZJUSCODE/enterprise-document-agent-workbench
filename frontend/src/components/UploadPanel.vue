<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { api } from "../api/client";
import type { DocumentFile, TemplateDefinition } from "../types/domain";

const props = defineProps<{
  files: DocumentFile[];
  templates: TemplateDefinition[];
}>();

const emit = defineEmits<{
  refresh: [];
  error: [message: string];
}>();

const selectedFiles = ref<File[]>([]);
const selectedTemplate = ref("contract_review");
const actor = ref("ops.demo");
const priority = ref(5);
const selectedExistingIds = ref<string[]>([]);
const busy = ref(false);
const lastMessage = ref("");

watch(
  () => props.templates,
  (templates) => {
    if (!templates.some((template) => template.id === selectedTemplate.value)) {
      selectedTemplate.value = templates[0]?.id ?? "contract_review";
    }
  },
  { immediate: true },
);

const canUpload = computed(() => selectedFiles.value.length > 0 && selectedTemplate.value && !busy.value);
const canBatch = computed(() => selectedExistingIds.value.length > 0 && selectedTemplate.value && !busy.value);
const selectedTemplateInfo = computed(() => props.templates.find((template) => template.id === selectedTemplate.value));

const fileSummary = computed(() => {
  if (selectedFiles.value.length === 0) return "拖入或选择合同、发票、表格、扫描件";
  if (selectedFiles.value.length === 1) return selectedFiles.value[0].name;
  return `${selectedFiles.value.length} 个文件已准备好`;
});

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  selectedFiles.value = Array.from(input.files ?? []);
  lastMessage.value = selectedFiles.value.length ? "文件已选择，点击开始处理即可。" : "";
}

async function uploadAndCreate() {
  if (!canUpload.value) return;
  busy.value = true;
  lastMessage.value = "正在上传并创建处理任务。";
  try {
    const uploaded: DocumentFile[] = [];
    for (const file of selectedFiles.value) {
      uploaded.push(await api.uploadFile(file, actor.value));
    }
    await api.createBatchTasks({
      file_ids: uploaded.map((file) => file.id),
      template_id: selectedTemplate.value,
      submitted_by: actor.value,
      priority: priority.value,
    });
    selectedFiles.value = [];
    lastMessage.value = "任务已创建。系统会自动解析、抽取、索引并送审。";
    emit("refresh");
  } catch (error) {
    emit("error", error instanceof Error ? error.message : "上传失败，请确认后端服务可用后重试");
  } finally {
    busy.value = false;
  }
}

async function createBatchFromExisting() {
  if (!canBatch.value) return;
  busy.value = true;
  lastMessage.value = "正在为已有文件创建批处理任务。";
  try {
    await api.createBatchTasks({
      file_ids: selectedExistingIds.value,
      template_id: selectedTemplate.value,
      submitted_by: actor.value,
      priority: priority.value,
    });
    selectedExistingIds.value = [];
    lastMessage.value = "批处理任务已创建。";
    emit("refresh");
  } catch (error) {
    emit("error", error instanceof Error ? error.message : "批处理失败，请稍后重试");
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="primary-panel upload-panel">
    <div class="panel-header compact">
      <div>
        <p class="eyebrow">开始</p>
        <h2>把文档交给 Agent</h2>
      </div>
      <span class="status-pill">端到端处理</span>
    </div>

    <div class="upload-layout">
      <label class="drop-zone">
        <input
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.xlsm,.csv,.txt,.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp"
          @change="onFileChange"
        />
        <span class="drop-icon">+</span>
        <span>
          <strong>{{ fileSummary }}</strong>
          <small>PDF、Word、Excel、CSV、TXT、图片 OCR</small>
        </span>
      </label>

      <div class="intake-steps" aria-label="处理链路">
        <div>
          <span>01</span>
          <strong>解析</strong>
          <small>正文、表格、元数据</small>
        </div>
        <div>
          <span>02</span>
          <strong>抽取</strong>
          <small>Schema 约束输出</small>
        </div>
        <div>
          <span>03</span>
          <strong>治理</strong>
          <small>送审、版本、导出</small>
        </div>
      </div>
    </div>

    <div class="quick-row">
      <label>
        <span>输出模板</span>
        <select v-model="selectedTemplate">
          <option v-for="template in templates" :key="template.id" :value="template.id">
            {{ template.name }}
          </option>
        </select>
      </label>
      <button class="primary-action" :disabled="!canUpload" @click="uploadAndCreate">
        {{ busy ? "处理中" : "开始处理" }}
      </button>
    </div>
    <p v-if="selectedTemplateInfo" class="template-note">
      {{ selectedTemplateInfo.description }} · 输出 {{ selectedTemplateInfo.output_format.toUpperCase() }}
    </p>

    <p v-if="lastMessage" class="guidance">{{ lastMessage }}</p>

    <details class="soft-disclosure">
      <summary>高级选项</summary>
      <div class="form-grid">
        <label>
          <span>处理人</span>
          <input v-model="actor" type="text" />
        </label>
        <label>
          <span>优先级</span>
          <input v-model.number="priority" min="1" max="9" type="number" />
        </label>
      </div>
    </details>

    <details class="soft-disclosure existing-files">
      <summary>从已有文件重新处理</summary>
      <div class="file-pick-list">
        <label v-for="file in files.slice(0, 8)" :key="file.id" class="check-row">
          <input v-model="selectedExistingIds" type="checkbox" :value="file.id" />
          <span>{{ file.original_filename }}</span>
          <small>{{ file.status }}</small>
        </label>
      </div>
      <button class="secondary" :disabled="!canBatch" @click="createBatchFromExisting">创建批处理</button>
    </details>
  </section>
</template>
