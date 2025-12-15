#!/usr/bin/env python3
"""
HAES CLI - Hybrid AI Evolution System 대화형 인터페이스

터미널에서 HAES와 대화할 수 있는 CLI
"""

import asyncio
import os
import sys
from pathlib import Path

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import print as rprint

from haes import HybridAISystem, Config
from haes.llm import OpenAIClient


console = Console()


def print_banner():
    """시작 배너 출력"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚀 HAES - Hybrid AI Evolution System                       ║
║                                                               ║
║   63개 AI Research SKILLs + 159개 전문 에이전트              ║
║   GPT-5.1 기반 하이브리드 AI 시스템                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


def print_help():
    """도움말 출력"""
    help_table = Table(title="📚 명령어 도움말", show_header=True)
    help_table.add_column("명령어", style="cyan")
    help_table.add_column("설명", style="white")
    
    help_table.add_row("/help", "도움말 표시")
    help_table.add_row("/stats", "시스템 통계 표시")
    help_table.add_row("/skills", "SKILL 목록 표시")
    help_table.add_row("/history", "대화 히스토리")
    help_table.add_row("/clear", "히스토리 초기화")
    help_table.add_row("/feedback <1-5>", "마지막 응답 평가")
    help_table.add_row("/quit", "종료")
    
    console.print(help_table)


def print_stats(system: HybridAISystem):
    """시스템 통계 출력"""
    stats = system.get_stats()
    
    table = Table(title="📊 시스템 통계", show_header=True)
    table.add_column("항목", style="cyan")
    table.add_column("값", style="green")
    
    table.add_row("인덱싱된 SKILL", str(stats["skill_store"]["total_skills"]))
    table.add_row("로드된 에이전트", str(stats["agent_pool"]["total_agents"]))
    table.add_row("피드백 수", str(stats["feedback"]["total"]))
    table.add_row("학습된 패턴", str(stats["evolution"]["learned_patterns_count"]))
    table.add_row("대화 수", str(stats["history_length"] // 2))
    
    if stats["evolution"]["total_feedbacks"] > 0:
        table.add_row("평균 평점", f"{stats['evolution']['average_score']:.2f}")
    
    console.print(table)


def print_skills(system: HybridAISystem):
    """SKILL 목록 출력"""
    index = system.get_compressed_index()
    console.print(Panel(index, title="📚 SKILL 인덱스", border_style="blue"))


def print_history(system: HybridAISystem):
    """대화 히스토리 출력"""
    if not system.history:
        console.print("[yellow]대화 히스토리가 비어있습니다.[/yellow]")
        return
    
    for i, entry in enumerate(system.history):
        role = entry["role"]
        content = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
        
        if role == "user":
            console.print(f"[cyan]👤 사용자:[/cyan] {content}")
        else:
            mode = entry.get("metadata", {}).get("mode", "unknown")
            console.print(f"[green]🤖 AI ({mode}):[/green] {content}")


async def main():
    """메인 CLI 함수"""
    print_banner()
    
    # 1. OpenAI 클라이언트 초기화
    console.print("\n[yellow]⏳ OpenAI 연결 중...[/yellow]")
    try:
        llm_client = OpenAIClient(
            routing_model=os.getenv("ROUTING_MODEL", "gpt-5-mini"),
            main_model=os.getenv("MAIN_MODEL", "gpt-5.1"),
        )
        console.print(f"[green]✅ 연결 성공![/green] (모델: {llm_client.main_model})")
    except Exception as e:
        console.print(f"[red]❌ OpenAI 연결 실패: {e}[/red]")
        console.print("[yellow]Mock 모드로 실행합니다.[/yellow]")
        llm_client = None
    
    # 2. 시스템 설정
    # 실제 SKILL/Agent 경로 사용
    project_root = Path("/home/cafe99/anti-gravity-project")
    skills_path = project_root / "AI-research-SKILLs"
    agents_path = project_root / ".claude" / "agents"
    
    if not skills_path.exists():
        # 샘플 데이터 사용
        console.print("[yellow]⚠️ 실제 SKILL 경로를 찾을 수 없어 샘플 데이터를 사용합니다.[/yellow]")
        skills_path = Path(__file__).parent / "tests" / "fixtures" / "sample_skills"
        agents_path = Path(__file__).parent / "tests" / "fixtures" / "sample_agents"
    
    config = Config(
        skills_path=skills_path,
        agents_path=agents_path,
        persist_dir=Path(__file__).parent / "cli_vectordb",
    )
    
    # 3. 시스템 초기화
    console.print("\n[yellow]⏳ 시스템 초기화 중...[/yellow]")
    system = HybridAISystem(config=config, llm_client=llm_client)
    stats = system.initialize()
    console.print(f"[green]✅ 초기화 완료![/green] (SKILL: {stats['skills_indexed']}, 에이전트: {stats['agents_loaded']})")
    
    # 도움말 표시
    console.print("\n[dim]'/help'를 입력하면 명령어 목록을 볼 수 있습니다.[/dim]")
    console.print("[dim]종료하려면 '/quit'를 입력하세요.[/dim]\n")
    
    # 4. 대화 루프
    while True:
        try:
            # 사용자 입력
            query = Prompt.ask("\n[bold cyan]👤 질문[/bold cyan]")
            
            if not query.strip():
                continue
            
            # 명령어 처리
            if query.startswith("/"):
                cmd = query.lower().split()[0]
                
                if cmd == "/quit" or cmd == "/exit":
                    console.print("[yellow]👋 안녕히 가세요![/yellow]")
                    break
                
                elif cmd == "/help":
                    print_help()
                    continue
                
                elif cmd == "/stats":
                    print_stats(system)
                    continue
                
                elif cmd == "/skills":
                    print_skills(system)
                    continue
                
                elif cmd == "/history":
                    print_history(system)
                    continue
                
                elif cmd == "/clear":
                    system.history.clear()
                    console.print("[green]✅ 히스토리가 초기화되었습니다.[/green]")
                    continue
                
                elif cmd == "/feedback":
                    parts = query.split()
                    if len(parts) < 2:
                        score = IntPrompt.ask("평점 (1-5)")
                    else:
                        try:
                            score = int(parts[1])
                        except:
                            console.print("[red]올바른 점수를 입력하세요 (1-5)[/red]")
                            continue
                    
                    if 1 <= score <= 5:
                        try:
                            system.feedback(score=score)
                            console.print(f"[green]✅ 피드백 저장: {score}점[/green]")
                        except ValueError as e:
                            console.print(f"[red]{e}[/red]")
                    else:
                        console.print("[red]점수는 1-5 사이여야 합니다.[/red]")
                    continue
                
                else:
                    console.print(f"[red]알 수 없는 명령어: {cmd}[/red]")
                    continue
            
            # 일반 질문 처리
            console.print("\n[yellow]⏳ 처리 중...[/yellow]")
            
            result = await system.chat(query)
            
            # 결과 출력
            mode_icons = {
                "skill_only": "📚",
                "skill_agent": "🤖",
                "parallel": "⚡",
                "multi_agent": "👥",
            }
            icon = mode_icons.get(result.mode, "💬")
            
            # 메타 정보
            meta = f"[dim]모드: {result.mode} | 시간: {result.execution_time:.2f}s"
            if result.skills_used:
                meta += f" | SKILL: {', '.join(result.skills_used)}"
            if result.agents_used:
                meta += f" | 에이전트: {', '.join(result.agents_used)}"
            meta += "[/dim]"
            console.print(meta)
            
            # 응답 출력
            console.print(Panel(
                Markdown(result.response),
                title=f"{icon} AI 응답",
                border_style="green",
            ))
            
            # 피드백 힌트
            console.print("[dim]'/feedback 5' 명령으로 응답을 평가해주세요.[/dim]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 안녕히 가세요![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]오류 발생: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
