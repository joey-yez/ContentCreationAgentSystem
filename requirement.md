# AI Agent 内容生产系统（公众号文章生成与发布）PRD

## 1. 项目背景

本项目目标是构建一个基于 AI Agent 的内容生产系统。

用户输入一个主题后，系统能够：

1. 自动研究主题
2. 自动生成文章大纲
3. 在用户确认后生成正文
4. 支持用户反馈与局部修改
5. 最终导出 Markdown 或发布到公众号

项目重点并不是“AI 写文章”，而是：

> 构建一个具备 Runtime、State、Memory、Tool Use、Human-in-the-loop 的 Agent 系统。

---

# 2. 产品目标

## 2.1 核心目标

构建一个：

- Goal-oriented
- Multi-step workflow
- Human-in-the-loop
- Tool-driven
- Stateful
- 可扩展

的 Content Production Agent。

---

## 2.2 非目标（第一阶段不做）

以下内容不属于 MVP：

- 多用户系统
- 权限管理
- SaaS 化
- 自动增长
- SEO 自动优化
- AI 配图
- 多平台分发
- 长期记忆复杂策略
- Multi-agent 协作
- 向量数据库
- 复杂 UI

---

# 3. 用户场景

## 3.1 核心用户

- 技术 PM
- 独立开发者
- AI 创作者
- 技术博主
- 知识型内容生产者

---

## 3.2 用户目标

用户希望：

- 更快生产高质量内容
- 降低写作成本
- 保持结构化表达
- 快速迭代文章
- 保留人工控制能力

---

# 4. 产品核心流程

## 4.1 整体流程

```text
Topic
↓
Research
↓
Outline Generation
↓
User Approval
↓
Draft Generation
↓
Critique
↓
Rewrite
↓
Export Markdown
↓
Publish
```

---

# 5. MVP 功能定义

MVP 只实现以下核心能力。

---

## 5.1 Topic 输入

### 功能

用户输入：

- 文章主题
- 风格（可选）
- 目标读者（可选）
- 文章长度（可选）

---

### 示例

```text
主题：AI Agent 为什么会改变 SaaS
风格：深度分析
目标读者：技术产品经理
长度：3000 字
```

---

## 5.2 Topic Understanding

系统分析：

- 文章类型
- 受众类型
- 内容深度
- 推荐结构
- 推荐写作方式

---

### 输出示例

```json
{
  "topic": "AI Agent 为什么会改变 SaaS",
  "style": "technical_analysis",
  "audience": "technical_pm",
  "estimated_sections": 5,
  "estimated_words": 3000
}
```

---

## 5.3 Outline Generation

系统自动生成：

- 一级标题
- 二级标题
- 每章节摘要

---

### 示例

```markdown
# AI Agent 为什么会改变 SaaS

## 一、传统 SaaS 的问题
- 功能复杂
- Workflow 固化

## 二、Agent 的核心价值
- Goal-driven
- Tool orchestration

## 三、未来的软件形态
- Agent-native software
```

---

## 5.4 User Approval（关键）

用户必须能够：

- 接受大纲
- 修改大纲
- 删除章节
- 增加章节
- 调整顺序

---

### 说明

这是 Human-in-the-loop 的关键节点。

系统不能完全 autonomous。

---

## 5.5 Draft Generation

系统按 section 逐段生成正文。

不能一次性生成整篇文章。

---

### 原因

避免：

- token 爆炸
- 风格漂移
- 上下文丢失
- 长文重复

---

### 生成策略

推荐：

```text
Section by Section
```

每次：

1. 输入当前 section
2. 输入已完成 section summary
3. 生成当前 section
4. 保存结果

---

## 5.6 User Feedback / Rewrite

用户能够：

- 指定 section 修改
- 提供反馈
- 局部重写

---

### 示例

```text
第三部分太浅
增加更多企业案例
```

系统只重写相关 section。

---

## 5.7 Markdown Export

系统能够导出：

```text
output/article.md
```

---

## 5.8 Publish（Phase 2）

后续支持：

- 微信公众号发布
- 草稿箱
- 封面图
- 摘要
- 标签

MVP 不实现。

---

# 6. Agent Runtime 设计

这是项目核心。

---

## 6.1 Runtime Loop

系统本质：

```python
while not task.done():

    context = assemble_context(
        state,
        memory,
        current_step,
        tool_results,
        user_feedback
    )

    response = llm(context)

    action = parse_action(response)

    execute(action)

    update_state()

    update_memory()
```

---

# 7. State Machine 设计

## 7.1 Article State

每篇文章是一个 Task。

---

### 状态定义

```text
CREATED
↓
UNDERSTANDING_TOPIC
↓
RESEARCHING
↓
OUTLINE_GENERATED
↓
WAITING_USER_APPROVAL
↓
DRAFTING
↓
WAITING_REVIEW
↓
REVISING
↓
READY_TO_EXPORT
↓
EXPORTED
↓
PUBLISHED
```

---

## 7.2 状态字段

```json
{
  "task_id": "article_001",
  "phase": "DRAFTING",
  "current_section": 2,
  "completed_sections": [1],
  "pending_sections": [2,3,4],
  "draft_version": 3,
  "last_updated": "2026-05-21"
}
```

---

# 8. Context Engineering

## 8.1 Context 来源

系统需要动态 assemble prompt。

---

### 来源包括

#### 1. System Prompt

定义：

- Agent role
- 输出格式
- 风格要求

---

#### 2. User Input

例如：

- topic
- style
- audience

---

#### 3. Historical Sections

例如：

- 已生成内容 summary
- 当前章节上下文

---

#### 4. Tool Results

例如：

- 搜索结果
- research 内容

---

#### 5. User Feedback

例如：

```text
增加更多案例
语气更专业
```

---

# 9. Memory 设计

MVP 阶段使用轻量方案。

---

## 9.1 Memory 类型

### User Preference Memory

例如：

- 喜欢技术深度
- 偏好 markdown
- 常写 AI 主题

---

## 9.2 MVP 存储方式

推荐：

```text
SQLite + JSON
```

不需要向量数据库。

---

# 10. Tool System

## 10.1 MVP Tools

---

### Research Tool

功能：

- 搜索主题资料
- 提取摘要

---

### Markdown Export Tool

功能：

- 导出 markdown
- 保存 article 文件

---

### File Storage Tool

功能：

- 保存 draft
- 保存 state

---

# 11. 技术架构

## 11.1 推荐技术栈

| 模块 | 技术 |
|---|---|
| Runtime | Python |
| LLM API | OpenAI / Anthropic |
| Storage | SQLite |
| State Store | SQLite |
| CLI | Typer / Click |
| Future UI | FastAPI + Next.js |

---

# 12. 项目目录结构

```text
project/
│
├── runtime/
│   ├── loop.py
│   ├── planner.py
│   ├── context.py
│   └── state_manager.py
│
├── agents/
│   ├── writer_agent.py
│   ├── outline_agent.py
│   └── critic_agent.py
│
├── memory/
│   ├── memory_store.py
│   └── retrieval.py
│
├── tools/
│   ├── research_tool.py
│   ├── markdown_export.py
│   └── file_storage.py
│
├── prompts/
│
├── storage/
│   ├── sqlite.db
│   └── articles/
│
└── main.py
```

---

# 13. CLI 交互设计（MVP）

## 13.1 示例

```bash
python main.py
```

---

### 用户输入

```text
请输入主题：
AI Agent 为什么会改变 SaaS
```

---

### 系统输出

```text
[Generating outline...]
```

---

### 用户确认

```text
Approve outline? (y/n)
```

---

# 14. 开发阶段规划

## Phase 1（核心 MVP）

### 功能

- Topic Input
- Outline Generation
- User Approval
- Draft Generation
- Markdown Export

---

### 不做

- UI
- 发布
- 多用户
- Memory retrieval

---

## Phase 2

加入：

- State persistence
- Resume task
- Research tool
- Rewrite flow

---

## Phase 3

加入：

- Critique loop
- Quality scoring
- Multi-step revision

---

## Phase 4

加入：

- Web UI
- WeChat publish
- Image generation
- SEO optimization
