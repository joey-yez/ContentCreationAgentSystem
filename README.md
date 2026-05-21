# ContentCreationAgentSystem

一个用于内容创作的智能代理系统，聚焦于“Human-in-the-loop”设计。该项目通过多阶段流程生成文章，包括大纲创建、用户确认、分段草稿生成与最终导出，帮助用户控制结构与风格，避免 token 爆炸和内容漂移。

## 核心特性

- Human-in-the-loop：大纲生成后暂停，等待用户确认，确保内容结构可控。
- 分章逐段生成：文章按章节逐步生成，降低 token 负载，减少风格漂移。
- 支持任务跟踪：可查看任务状态、继续草稿生成、导出文章。

## 使用方式

```bash
# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件并配置 OpenAI API Key
cp .env.example .env
# 编辑 .env 添加你的 API Key

# 创建新文章任务
python main.py new "AI Agent 为什么会改变 SaaS" --style "深度分析" --audience "技术产品经理" --words 3000

# 查看任务状态
python main.py show <task_id>

# 继续草稿生成
python main.py draft <task_id>

# 导出文章
python main.py export <task_id>
```

## 推荐流程

1. 先创建新文章任务。
2. 生成大纲后，系统暂停并等待用户确认结构。
3. 确认后，按章节逐段生成草稿，避免一次性生成大量内容。
4. 完成后导出最终文章。

## 适用场景

- 需要对文章结构有严格控制的技术创作流程。
- 希望分段生成内容，减少 OpenAI token 费用与上下文漂移。
- 注重“大纲先行、用户确认、逐段写作”的协作式内容创作。

## 目录结构（简要）

- `main.py`：入口脚本，支持任务创建、查看、继续生成、导出。
- `agents/`：包含写作与大纲代理逻辑。
- `runtime/`：上下文管理、任务调度、状态管理。
- `storage/`：文章存储与导出功能。
- `tools/`：辅助功能，如文件存储、Markdown 导出。

## 注意事项

- 请先配置 `.env` 中的 `OPENAI_API_KEY`。
- 文章生成过程依赖 OpenAI API，请确保网络与配额正常。
