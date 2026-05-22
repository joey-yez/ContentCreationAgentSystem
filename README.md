# Content Creation Agent System

一个基于 LLM 的智能内容创作代理系统，支持文章大纲生成、内容撰写、用户反馈迭代和质量评估。

## 功能特性

- **智能大纲生成**：基于主题自动生成结构化大纲，支持用户反馈修订
- **章节内容撰写**：按章节逐段生成文章，支持基于反馈的局部重写
- **Memory 系统**：记录用户初始输入和反馈历史，避免要求冲突
- **评估系统**：自动评估大纲和文章质量，统计 LLM 调用耗时和 Token 使用量
- **Human-in-the-loop**：大纲生成后暂停等待用户确认，确保内容控制权
- **多 LLM 支持**：支持 OpenAI 和 DeepSeek 等多个 LLM 提供商

## 项目结构

```
ContentCreationAgentSystem/
├── agents/                    # 代理模块
│   ├── outline_agent.py       # 大纲生成 Agent
│   ├── writer_agent.py        # 文章撰写 Agent
│   ├── evaluator_agent.py     # 评估 Agent
│   └── feedback_analyzer.py   # 反馈分析 Agent
├── runtime/                   # 运行时模块
│   ├── loop.py                # 核心运行时循环
│   ├── state_manager.py       # 状态管理与状态机
│   ├── planner.py             # 任务规划器
│   └── context.py             # 上下文组装器
├── memory/                    # 记忆系统
│   └── memory_store.py        # 存储用户输入和反馈历史
├── evaluation/                # 评估系统
│   └── __init__.py            # 统计生成次数、耗时、Token 使用量
├── tools/                     # 工具模块
│   ├── markdown_export.py     # Markdown 导出工具
│   └── file_storage.py        # 文件存储工具
├── llm_client.py              # LLM 客户端封装
├── main.py                    # CLI 入口
├── requirements.txt           # 依赖配置
└── .env                       # 环境变量配置
```

## 核心模块介绍

### Agents 层

#### OutlineAgent
负责生成和修订文章大纲：
- 基于主题、风格、受众生成结构化大纲
- 支持根据用户反馈重新生成大纲
- 输出包含标题、章节摘要的结构化数据

#### WriterAgent
负责撰写文章章节内容：
- 按章节逐段生成文章内容
- 保持与上下文的连贯性
- 支持基于用户反馈的局部重写
- 自动处理 LLM 返回的 JSON 格式问题

#### EvaluatorAgent
负责评估内容质量：
- **大纲评估**：相关性、结构完整性、深度、符合要求
- **文章评估**：相关性、结构完整性、内容深度、风格一致性、目标受众适配、语言质量

#### FeedbackAnalyzer
负责分析用户反馈并更新 Memory：
- 使用 LLM 分析用户反馈意图
- 自动检测需求变更（受众、段落数、字数等）
- 更新 Memory 中的用户要求

### Runtime 层

#### RuntimeLoop
核心执行循环，协调各组件工作：
- 管理状态机转换
- 调用相应的 Agent 处理各阶段任务
- 返回任务状态给 CLI

#### StateManager
管理文章状态机：
- 支持状态持久化存储
- 提供状态查询和更新接口
- 状态流转：CREATED → UNDERSTANDING_TOPIC → OUTLINE_GENERATED → WAITING_USER_APPROVAL → DRAFTING → WAITING_REVIEW → READY_TO_EXPORT → EXPORTED

#### Planner
任务规划器：
- 定义各阶段的步骤
- 判断是否需要用户输入
- 判断是否到达最终阶段

### Memory 系统

MemoryStore 记录用户交互历史：
- 存储初始输入（主题、风格、受众、字数、段落数）
- 记录每次用户反馈
- 支持更新用户要求
- 提供当前要求查询接口

### Evaluation 系统

统计任务执行数据：
- 大纲生成次数
- 文章章节生成次数
- 修订次数
- LLM 调用耗时
- Token 使用量（Prompt/Completion/Total）
- 大纲和文章评估结果

## 安装与配置

### 依赖安装

```bash
pip install -r requirements.txt
```

### 环境配置

创建 `.env` 文件：

```env
# 选择 LLM 提供商：openai 或 deepseek
LLM_PROVIDER=deepseek

# DeepSeek 配置（选择 deepseek 时使用）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat

# OpenAI 配置（选择 openai 时使用）
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
```

## 使用方式

### 创建新文章

```bash
python main.py new "文章主题" --style "写作风格" --audience "目标读者" --words 3000 --sections 5
```

### 生成草稿

```bash
python main.py draft <task_id>
```

### 导出文章

```bash
python main.py export <task_id>
```

### 查看任务状态

```bash
python main.py show <task_id>
```

### 查看评估报告

```bash
python main.py show-evaluation <task_id>
```

### 查看记忆信息

```bash
python main.py show-memory <task_id>
```

## 使用流程

1. **创建任务**：指定主题、风格、受众、字数和段落数
2. **生成大纲**：系统自动生成文章大纲
3. **大纲审查**：用户可批准、修改或退出
   - 修改时系统会分析反馈并更新 Memory
4. **生成草稿**：按章节逐段生成文章内容
5. **文章审阅**：用户可继续生成、修改章节或导出
6. **导出文章**：保存为 Markdown 文件

## 评估维度

### 大纲评估
| 维度 | 说明 |
|---|---|
| 相关性 | 大纲是否紧扣主题 |
| 结构完整性 | 是否有合理的引言、主体和结论 |
| 深度 | 是否有足够的分析深度 |
| 符合要求 | 是否符合用户指定的风格、字数和段落数 |

### 文章评估
| 维度 | 说明 |
|---|---|
| 相关性 | 内容是否紧扣主题 |
| 结构完整性 | 是否按照大纲完成了所有章节 |
| 内容深度 | 分析是否深入、有说服力 |
| 风格一致性 | 是否符合指定的写作风格 |
| 目标受众适配 | 是否适合目标读者阅读 |
| 语言质量 | 语言表达是否流畅、专业 |

## 输出示例

### 进度显示
```
已完成章节: 1/5 - AI Agent 的定义与发展
已完成章节: 2/5 - AI Agent 在 SaaS 中的应用场景
已完成章节: 3/5 - 核心技术架构
```

### 评估报告
```
┌─────────────────────────────────────────────────────┐
│              Task Evaluation Summary                │
├─────────────────────────────────────────────────────┤
│ Task ID: article_abc12345
├─────────────────────────────────────────────────────┤
│ Generation Counts:
│   - Outline Generations: 2
│   - Article Sections: 5
│   - Revisions: 1
├─────────────────────────────────────────────────────┤
│ LLM Token Usage:
│   - Prompt Tokens: 8,520
│   - Completion Tokens: 12,345
│   - Total Tokens: 20,865
├─────────────────────────────────────────────────────┤
│ Outline Evaluation:
│   - Score: 8.5/10
│   - Feedback: 大纲结构完整...
├─────────────────────────────────────────────────────┤
│ Article Evaluation:
│   - Score: 9.0/10
│   - Feedback: 文章内容详实...
└─────────────────────────────────────────────────────┘
```

## 技术栈

- Python 3.11+
- Typer (CLI 框架)
- Pydantic (数据验证)
- python-dotenv (环境变量)
- OpenAI/DeepSeek API
