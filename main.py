#!/usr/bin/env python3

import typer
from runtime.loop import RuntimeLoop
from tools.markdown_export import MarkdownExportTool

app = typer.Typer()
runtime = RuntimeLoop()
export_tool = MarkdownExportTool()

@app.command()
def new(topic: str, style: str = None, audience: str = None, words: int = None):
    task_id = runtime.create_task(topic, style, audience, words)
    typer.echo(f"创建任务成功！Task ID: {task_id}")
    
    result = runtime.run(task_id)
    if result.get("status") == "waiting_user_input":
        state = result.get("state")
        show_outline(state)
        
        approval = typer.prompt("请确认大纲是否满意？(y/n)", default="n")
        if approval.lower() == "y":
            runtime.approve_outline(task_id)
            draft(task_id)
        else:
            typer.echo("请修改大纲后重新确认")

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
