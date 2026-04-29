# AI / Agent 岗位求职就绪度

## 结论

这个项目已经够用来投 AI 应用工程、Agent 工作流、LLM 后端和企业级 AI 全栈岗位。它的优势是有完整业务闭环，而不是只做一个聊天窗口：文档上传、解析、OCR、RAG、结构化抽取、风险审查、人工审批、审计、导出和离线评测都能串起来演示。

更适合投递的岗位关键词：

- AI Application Engineer
- Agent Workflow Engineer
- LLM Backend Engineer
- RAG / Knowledge Application Engineer
- Enterprise AI Full-stack Engineer
- Document AI / Intelligent Process Automation Engineer

## 面试官会认可的证据

| 能力 | 项目证据 | 讲法 |
| --- | --- | --- |
| Agent 编排 | `backend/app/services/workflow.py` | 任务状态机把解析、分类、索引、抽取、审查、生成、审批串成可恢复流程。 |
| 工具调用可观测 | `backend/app/services/agents.py` | 每个 Agent step 记录工具名、输入摘要、输出摘要和耗时，前端可回放 trace。 |
| 结构化 LLM 输出 | `backend/app/services/extractor.py` | OpenAI-compatible API 优先使用 JSON Schema，失败后降级到 JSON Object，再失败用规则兜底。 |
| RAG 闭环 | `backend/app/services/rag.py` | 任务处理时自动切块索引，查询时返回带引用编号和命中词的证据片段。 |
| Human-in-the-loop | `backend/app/api/routes_approvals.py` | 高风险结果进入审批队列，修订会生成结果版本并写审计日志。 |
| 工程化 | `.github/workflows/ci.yml` | CI 覆盖后端测试、离线评测和前端构建。 |
| 可演示性 | `samples/`, `scripts/seed_demo.py` | 无模型 key 也能稳定跑通，适合现场演示。 |

## 3 分钟项目讲法

1. 先定义问题：企业文档处理不是单次问答，而是需要可追踪、可审批、可导出的流程。
2. 展示工作台首屏：任务指标、Agent 链路、审批和评测入口。
3. 上传 `samples/contract_sample.txt`，说明任务如何进入解析、RAG 索引、结构化抽取和风险审查。
4. 打开任务详情，讲 Agent trace、字段、异常、结果版本和 SSE 事件。
5. 用 RAG 问“付款方式和违约责任是什么”，强调回答基于引用片段，不是纯生成。
6. 最后讲边界：当前 RAG 是本地轻量检索，生产可以替换 pgvector / Elasticsearch hybrid search；样本集较小，但评测框架已打通。

## 简历写法

可直接放在项目经历里：

> 企业文档流程自动化 Agent 工作台：基于 FastAPI、Vue 3、Celery、SQLAlchemy 构建端到端 AI 文档处理系统，支持多格式上传、OCR 兜底、RAG 索引问答、OpenAI-compatible 结构化抽取、风险审查、人工审批、审计日志、结果版本和 Markdown/DOCX/PDF 导出。实现可观测 Agent trace、SSE 任务事件流、离线标注集评测与 GitHub Actions CI；未配置模型 key 时提供规则抽取兜底，保证本地演示稳定。

## 还需要注意

- 发布到 GitHub 前要确认不是只上传压缩包：需要初始化 git、保留清晰 commit，并避免提交 `storage/`、`node_modules/`、日志和真实 key。
- README 顶部要放截图、演示路径和评测结果，不要只写安装说明。
- 面试时主动承认当前样本集规模小、RAG 是轻量本地实现；重点强调接口边界已经为生产级向量库和更多标注数据预留。
