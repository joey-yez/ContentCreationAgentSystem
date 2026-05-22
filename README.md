# ContentCreationAgentSystem

一个用于内容创作的智能代理系统，聚焦于"Human-in-the-loop"设计。该项目通过多阶段流程生成文章，包括大纲创建、用户确认、分段草稿生成与最终导出，帮助用户控制结构与风格，避免 token 爆炸和内容漂移。

## 核心特性

- **Human-in-the-loop**：大纲生成后暂停，等待用户确认，确保内容结构可控。
- **分章逐段生成**：文章按章节逐步生成，降低 token 负载，减少风格漂移。
- **Memory 系统**：记录用户初始输入和反馈历史，避免冲突。
- **智能评估**：自动评估大纲和文章质量，提供评分和改进建议。
- **支持多 LLM**：支持 OpenAI 和 DeepSeek 等多种语言模型。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件并配置 API Key
cp .env.example .env
# 编辑 .env 添加你的 API Key
```

### 配置说明

支持两种 LLM 提供商：

**DeepSeek（推荐）**：
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
```

**OpenAI**：
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
```

## 使用方式

### 创建新文章

```bash
python main.py new "AI Agent 为什么会改变 SaaS" --style "深度分析" --audience "技术产品经理" --words 3000 --sections 5
```

参数说明：
- `topic`：文章主题（必需）
- `--style`：写作风格（可选）
- `--audience`：目标读者（可选）
- `--words`：预计字数（可选）
- `--sections`：预计段落数（可选）

### 大纲审查与修订

创建任务后，系统会生成大纲并等待用户确认：

```bash
请选择操作：(a)批准大纲 / (r)修改大纲 / (q)退出
```

选择 `a` 批准大纲，系统会自动评估大纲质量：

```
大纲评估结果
============================================================
评分: 8.5/10
反馈: 大纲结构完整，主题明确，但深度可以进一步加强。

评估维度:
  - 相关性: 9/10
  - 结构完整性: 8/10
  - 深度: 8/10
  - 符合要求: 9/10
```

选择 `r` 可以输入修改意见，系统会重新生成大纲。

### 文章生成

批准大纲后，系统会按章节逐段生成文章：

```bash
进度: 3/5 章节

[已完成] ## 1. AI Agent 的定义与发展
内容预览:
AI Agent 是一种能够自主感知环境、做出决策并执行任务的智能系统...

[待生成] ## 2. AI Agent 在 SaaS 中的应用场景

请选择操作：(c)继续生成 / (r)修改章节 / (e)导出 / (q)退出
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

### 导出文章

```bash
python main.py export <task_id>
```

## 推荐流程

1. 创建新文章任务，设置主题、风格、受众等参数。
2. 生成大纲后，系统暂停并展示评估结果。
3. 用户确认或修改大纲（支持多次修订）。
4. 确认后，按章节逐段生成草稿。
5. 可随时修改特定章节或继续生成。
6. 完成后导出最终文章，查看完整评估报告。

## 评估维度

### 大纲评估
- **相关性**：大纲是否紧扣主题
- **结构完整性**：是否有合理的引言、主体和结论
- **深度**：是否有足够的分析深度
- **符合要求**：是否符合用户指定的风格、字数和段落数

### 文章评估
- **相关性**：内容是否紧扣主题
- **结构完整性**：是否按照大纲完成了所有章节
- **内容深度**：分析是否深入、有说服力
- **风格一致性**：是否符合指定的写作风格
- **目标受众适配**：是否适合目标读者阅读
- **语言质量**：语言表达是否流畅、专业

## 目录结构

```
ContentCreationAgentSystem/
├── main.py              # CLI 入口
├── requirements.txt     # 依赖配置
├── .env.example         # 环境变量示例
├── agents/              # Agent 模块
│   ├── outline_agent.py    # 大纲生成 Agent
│   ├── writer_agent.py     # 文章撰写 Agent
│   └── evaluator_agent.py  # 评估 Agent
├── runtime/             # 运行时模块
│   ├── state_manager.py    # 状态管理
│   ├── context.py          # 上下文组装
│   ├── planner.py          # 任务规划器
│   └── loop.py             # 核心运行循环
├── memory/              # 记忆系统
│   └── memory_store.py     # 用户输入与反馈记录
├── evaluation/          # 评估模块
│   └── __init__.py         # 统计与评估结果
├── tools/               # 工具模块
│   ├── markdown_export.py  # Markdown 导出
│   └── file_storage.py     # 文件存储
├── storage/             # 草稿存储目录
└── output/              # 导出文件目录
```

## 注意事项

- 请先配置 `.env` 中的 API Key。
- 文章生成过程依赖 LLM API，请确保网络与配额正常。
- 支持 DeepSeek 和 OpenAI 两种提供商，可在 `.env` 中切换。

## License

MIT License
