# 🌿 CrossBorder-AI 智能运营中枢 (春木出海 AI 中枢)

> 专为美国大健康（食品补充剂）跨境电商打造的 AI Agent 与 RAG 合规工作台。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![Ollama](https://img.shields.io/badge/Ollama-qwen2.5:3b-green.svg)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## 💡 项目背景与痛点 (Business Context)

针对**美国大健康（膳食补充剂）跨境电商**（如 Amazon、TikTok Shop）的实际业务场景，本系统从0到1解决了两大核心痛点：

1. **FDA 合规风险极高**：运营人员稍有不慎使用“治愈、治疗”等违规词汇，极易导致亚马逊封店或 FDA 警告。大模型直接生成内容存在严重“幻觉”风险。
2. **多平台内容产出效率低**：TikTok 短视频脚本、Amazon Listing 撰写耗时耗力，难以规模化。

本项目通过 **Agent 智能体 + RAG 检索增强生成 + Human-in-the-loop（人工审核）** 架构，实现了从“意图识别 -> 知识库检索 -> 合规内容生成 -> 人工审核”的完整业务闭环。

---

## 🚀 核心功能 (Key Features)

- [x] **RAG 合规知识库**：内置 FDA 膳食补充剂指南与 TikTok 爆款 SOP，强制约束大模型输出边界，杜绝幻觉。
- [x] **意图路由（Intent Routing）**：精准区分“合规问答”与“内容生成”任务，按需检索知识库，降低算力消耗与响应延迟。
- [x] **流式输出（Streaming）**：基于 Python 生成器（`yield`）与 Ollama 实现逐字生成，前端打字机效果，极大降低感知等待时间。
- [x] **高级感 SaaS 界面**：注入自定义 CSS，实现暗黑玻璃拟态（Glassmorphism）风格，打破传统 AI 聊天框的枯燥感。
- [x] **Human-in-the-loop 人工审核区**：AI 生成草稿后不会直接发布，必须由运营主管在右侧面板进行“通过/驳回”操作，完美平衡效率与合规。
- [x] **本地大模型部署**：采用 Ollama + `qwen2.5:3b`，零 API 成本，保证企业核心选品与合规数据隐私。

---

## 🛠️ 技术栈 (Tech Stack)

| 层面 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **大模型 (LLM)** | Ollama (qwen2.5:3b) | 本地部署，支持流式输出，数据不出本地 |
| **RAG / 向量库** | ChromaDB | 轻量级本地向量数据库，用于存储合规与 SOP 文档 |
| **前端 UI** | Streamlit + 自定义 CSS | 极速构建 MVP，通过 CSS 注入实现玻璃拟态高级感 |
| **后端逻辑** | Python (Requests, Generator) | 处理 HTTP 流式请求、意图路由与 Prompt 拼接 |
| **开发工具 (Coding Agent)** | Cursor, GitHub Copilot | 辅助生成 CSS 样式与调试流式解析代码，提升开发效率 |

---

## 🏗️ 系统架构 (Architecture)

```text
[用户输入] 
   │
   ▼
[意图路由 (Intent Routing)] ──(判定为合规提问)──> [ChromaDB RAG 检索] 
   │                                                       │
   │◄──────────────────────────────────────────────────────┘
   ▼
[Prompt 工程拼接 (System Prompt + Context + User Query)]
   │
   ▼
[Ollama 本地模型 (qwen2.5:3b)] ──(Stream=True)──> [Python Generator (yield)]
   │
   ▼
[Streamlit st.write_stream (打字机效果)]
   │
   ▼
[人工审核面板 (Human-in-the-loop)] ──(通过)──> [发布至 Amazon/TikTok]
                                      └─(驳回)──> [重新生成]
<img width="1910" height="974" alt="image" src="https://github.com/user-attachments/assets/831285f5-47b5-44a2-80d9-f00b731f374f" />
