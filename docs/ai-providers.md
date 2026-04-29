# AI Provider 配置

系统通过 `AI_PROVIDER` 选择模型供应商：

- `siliconflow`
- `deepseek`
- `openai`

## SiliconFlow

```text
AI_PROVIDER=siliconflow
SILICONFLOW_API_KEY=...
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3.2
```

## DeepSeek

```text
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## OpenAI-compatible

```text
AI_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

## 安全约束

- API key 只放在后端 `.env` 或部署平台 secret 中。
- 前端只配置 `VITE_API_BASE_URL`，不要配置模型 API key。
- 日志中不要打印 API key、完整请求头或含企业敏感内容的原文。
- 已经公开发送过的 key，建议在供应商控制台轮换。
