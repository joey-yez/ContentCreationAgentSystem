#!/usr/bin/env python3

import typer
from runtime.loop import RuntimeLoop
from tools.markdown_export import MarkdownExportTool

app = typer.Typer()
runtime = RuntimeLoop()
export_tool = MarkdownExportTool()

@app.command()
def new(topic: str, style: str = None, audience: str = None, words: int = None, sections: int = None):
    task_id = runtime.create_task(topic, style, audience, words, sections)
    typer.echo(f"创建任务成功！Task ID: {task_id}")
    
    result = runtime.run(task_id)
    if result.get("status") == "waiting_user_input":
        state = result.get("state")
        show_outline(state)
        
        while True:
            action = typer.prompt("请选择操作：(a)批准大纲 / (r)修改大纲 / (q)退出", default="a")
            if action.lower() == "a":
                runtime.approve_outline(task_id)
                draft(task_id)
                break
            elif action.lower() == "r":
                feedback = typer.prompt("请输入对大纲的修改意见")
                revise_result = runtime.revise_outline(task_id, feedback)
                if revise_result.get("error"):
                    typer.echo(f"错误: {revise_result['error']}")
                else:
                    typer.echo(f"\n大纲已修改，第 {revise_result['revision_count']} 次修订")
                    state = runtime.get_state(task_id).dict()
                    show_outline(state)
            elif action.lower() == "q":
                break
            else:
                typer.echo("无效选项，请选择 a/r/q")

@app.command()
def draft(task_id: str):
    while True:
        result = runtime.run(task_id)
        if result.get("status") == "completed":
            typer.echo(f"文章生成完成！")
            break
        elif result.get("status") == "waiting_user_input":
            state = result.get("state")
            show_progress(state)
            
            action = typer.prompt("请选择操作：(c)继续生成 / (r)修改章节 / (e)导出 / (q)退出", default="c")
            if action.lower() == "c":
                continue
            elif action.lower() == "r":
                section_id = typer.prompt("请输入要修改的章节编号")
                feedback = typer.prompt("请输入修改意见")
                try:
                    runtime.request_revision(task_id, int(section_id), feedback)
                    typer.echo("章节已修改")
                except ValueError:
                    typer.echo("无效的章节编号")
            elif action.lower() == "e":
                export(task_id)
                break
            elif action.lower() == "q":
                break

@app.command()
def revise_outline_cmd(task_id: str, feedback: str):
    result = runtime.revise_outline(task_id, feedback)
    if result.get("error"):
        typer.echo(f"错误: {result['error']}")
    else:
        typer.echo(f"大纲已修改，第 {result['revision_count']} 次修订")
        state = runtime.get_state(task_id).dict()
        show_outline(state)

@app.command()
def export(task_id: str):
    state = runtime.get_state(task_id)
    if not state:
        typer.echo("任务不存在")
        return
    
    sections_data = [
        {"title": s.title, "content": s.content or ""}
        for s in state.sections
    ]
    
    title = state.metadata.get("title", state.topic)
    export_path = export_tool.export(title, sections_data, task_id)
    typer.echo(f"文章已导出到: {export_path}")

@app.command()
def show(task_id: str):
    state = runtime.get_state(task_id)
    if not state:
        typer.echo("任务不存在")
        return
    
    show_progress(state.dict())

@app.command()
def show_memory(task_id: str):
    memory = runtime.get_memory(task_id)
    if not memory:
        typer.echo("Memory not found")
        return
    
    typer.echo("\n" + "="*60)
    typer.echo("Memory 信息")
    typer.echo("="*60)
    
    initial = memory.get_initial_input()
    typer.echo("\n【初始输入】")
    typer.echo(f"- 主题: {initial.get('topic')}")
    typer.echo(f"- 风格: {initial.get('style', '未指定')}")
    typer.echo(f"- 受众: {initial.get('audience', '未指定')}")
    typer.echo(f"- 预计字数: {initial.get('estimated_words', '未指定')}")
    typer.echo(f"- 预计段落数: {initial.get('estimated_sections', '未指定')}")
    
    feedback_history = memory.get_all_feedback()
    typer.echo("\n【反馈历史】")
    for i, feedback in enumerate(feedback_history, 1):
        typer.echo(f"{i}. [{feedback['phase']}] {feedback['feedback']}")
    
    typer.echo(f"\n【修订次数】: {memory.memory['revision_count']}")
    typer.echo("\n" + "="*60)

def show_outline(state: dict):
    typer.echo("\n" + "="*60)
    typer.echo(f"文章标题: {state.get('metadata', {}).get('title', state.get('topic', ''))}")
    typer.echo("="*60)
    
    sections = state.get("sections", [])
    for section in sections:
        typer.echo(f"\n## {section.get('id')}. {section.get('title', '')}")
        if section.get('summary'):
            typer.echo(f"  摘要: {section.get('summary')}")
    
    typer.echo("\n" + "="*60)

def show_progress(state: dict):
    typer.echo("\n" + "="*60)
    typer.echo(f"任务状态: {state.get('phase', '')}")
    typer.echo(f"文章标题: {state.get('metadata', {}).get('title', state.get('topic', ''))}")
    typer.echo(f"当前版本: v{state.get('draft_version', 1)}")
    typer.echo("="*60)
    
    sections = state.get("sections", [])
    completed_count = sum(1 for s in sections if s.get('completed'))
    total_count = len(sections)
    
    typer.echo(f"\n进度: {completed_count}/{total_count} 章节")
    
    for section in sections:
        status = "[已完成]" if section.get('completed') else "[待生成]"
        typer.echo(f"\n{status} ## {section.get('id')}. {section.get('title', '')}")
        if section.get('content'):
            preview = section['content'][:100] + "..." if len(section['content']) > 100 else section['content']
            typer.echo(f"内容预览:\n{preview}")
    
    typer.echo("\n" + "="*60)

if __name__ == "__main__":
    app()
