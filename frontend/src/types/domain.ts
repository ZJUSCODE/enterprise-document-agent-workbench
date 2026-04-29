export interface DocumentFile {
  id: string;
  original_filename: string;
  content_type: string | null;
  size_bytes: number;
  checksum_sha256: string;
  storage_key: string;
  status: string;
  parser_name: string | null;
  parse_warnings: Record<string, unknown>[];
  metadata_json: Record<string, unknown>;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateDefinition {
  id: string;
  name: string;
  description: string;
  document_type: string;
  output_format: string;
  body: string;
  version: string;
  created_at: string;
  updated_at: string;
}

export interface TaskEvent {
  id: string;
  task_id: string;
  status: string;
  progress: number;
  level: string;
  message: string;
  created_at: string;
}

export interface Approval {
  id: string;
  task_id: string;
  status: string;
  reviewer: string | null;
  comment: string | null;
  created_at: string;
  decided_at: string | null;
}

export interface WorkflowTask {
  id: string;
  file_id: string;
  template_id: string;
  task_type: string;
  status: string;
  progress: number;
  retry_count: number;
  max_retries: number;
  priority: number;
  submitted_by: string;
  classified_as: string | null;
  extracted_fields: Record<string, unknown>;
  table_data: Record<string, unknown>[];
  summary: Record<string, unknown>;
  anomalies: Record<string, unknown>[];
  generated_artifact_key: string | null;
  error_message: string | null;
  result_version: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  events?: TaskEvent[];
  approvals?: Approval[];
}

export interface ResultVersion {
  id: string;
  task_id: string;
  version: number;
  artifact_key: string | null;
  extracted_fields: Record<string, unknown>;
  summary: Record<string, unknown>;
  anomalies: Record<string, unknown>[];
  created_by: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  actor: string;
  action: string;
  resource_type: string;
  resource_id: string;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface EvaluationSummary {
  total_tasks: number;
  success_rate: number;
  approval_rate: number;
  manual_takeover_rate: number;
  average_duration_seconds: number;
  extraction_accuracy_proxy: number;
  status_breakdown: Record<string, number>;
  anomaly_breakdown: Record<string, number>;
}

export interface RagHit {
  chunk_id: string;
  file_id: string;
  task_id: string | null;
  document_type: string | null;
  score: number;
  text: string;
  metadata: Record<string, unknown>;
}

export interface RagAnswer {
  question: string;
  answer: string;
  hits: RagHit[];
}
