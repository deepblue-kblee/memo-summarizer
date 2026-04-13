"""
에이전트 팀 CLI 인터페이스

사용자가 에이전트 팀과 상호작용할 수 있는 명령줄 도구들을 제공합니다.
"""

import click
import sys
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .agent_team import AgentTeam


console = Console()


@click.group()
def cli():
    """범용 LangGraph 에이전트 개발팀"""
    pass


@cli.command()
@click.argument("request", required=False)
@click.option("--interactive", "-i", is_flag=True, help="대화형 모드로 실행")
@click.option("--db-path", help="SQLite 데이터베이스 파일 경로")
def run(request: Optional[str], interactive: bool, db_path: Optional[str]):
    """
    에이전트 팀 실행

    REQUEST: 처리할 사용자 요청 (대화형 모드가 아닌 경우)
    """
    agent_team = AgentTeam(db_path=db_path)

    if interactive:
        _run_interactive_mode(agent_team)
    elif request:
        _run_single_request(agent_team, request)
    else:
        console.print("[red]ERROR:[/red] 요청을 입력하거나 --interactive 옵션을 사용하세요.")
        console.print("사용법: agent-team run '파일 생성해줘' 또는 agent-team run --interactive")
        sys.exit(1)


@cli.command()
@click.argument("request_id")
@click.option("--db-path", help="SQLite 데이터베이스 파일 경로")
def resume(request_id: str, db_path: Optional[str]):
    """중단된 요청 재개"""
    agent_team = AgentTeam(db_path=db_path)

    console.print(f"[blue]INFO:[/blue] 요청 '{request_id}' 재개 중...")

    try:
        result = agent_team.resume_request(request_id)
        if result:
            console.print("[green]SUCCESS:[/green] 요청이 성공적으로 재개되었습니다.")
            _display_status(result)
        else:
            console.print("[red]ERROR:[/red] 요청을 재개할 수 없습니다.")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("request_id", required=False)
@click.option("--db-path", help="SQLite 데이터베이스 파일 경로")
def status(request_id: Optional[str], db_path: Optional[str]):
    """요청 상태 조회"""
    agent_team = AgentTeam(db_path=db_path)

    if request_id:
        # 특정 요청 상태 조회
        status_info = agent_team.get_status(request_id)
        if status_info:
            _display_status(status_info)
        else:
            console.print(f"[red]ERROR:[/red] 요청 ID '{request_id}'를 찾을 수 없습니다.")
            sys.exit(1)
    else:
        # 최근 요청 목록 조회
        requests = agent_team.list_recent_requests()
        _display_request_list(requests)


@cli.command()
@click.option("--limit", "-l", default=10, help="조회할 요청 수")
@click.option("--db-path", help="SQLite 데이터베이스 파일 경로")
def history(limit: int, db_path: Optional[str]):
    """요청 히스토리 조회"""
    agent_team = AgentTeam(db_path=db_path)

    requests = agent_team.list_recent_requests(limit)
    _display_request_list(requests)


@cli.command()
@click.option("--db-path", help="SQLite 데이터베이스 파일 경로")
def simulate():
    """워크플로우 시뮬레이션 실행"""
    console.print("[blue]INFO:[/blue] 워크플로우 시뮬레이션을 시작합니다...")

    # TODO: simulator.py 구현 후 실제 시뮬레이션 실행
    console.print("[yellow]WARNING:[/yellow] 시뮬레이션 기능은 아직 구현되지 않았습니다.")
    console.print("Phase 3에서 구현 예정입니다.")


def _run_interactive_mode(agent_team: AgentTeam):
    """대화형 모드 실행"""
    console.print(Panel(
        "[bold blue]🚀 에이전트 팀 대화형 모드[/bold blue]\n\n"
        "무엇이든 요청해보세요! 'exit' 또는 'quit'으로 종료합니다.",
        title="Agent Team Interactive Mode"
    ))

    while True:
        try:
            user_input = console.input("\n[bold green]요청:[/bold green] ").strip()

            if user_input.lower() in ['exit', 'quit', '종료']:
                console.print("\n[blue]👋 에이전트 팀을 종료합니다.[/blue]")
                break

            if not user_input:
                continue

            _run_single_request(agent_team, user_input)

        except KeyboardInterrupt:
            console.print("\n\n[blue]👋 에이전트 팀을 종료합니다.[/blue]")
            break
        except Exception as e:
            console.print(f"\n[red]ERROR:[/red] {e}")


def _run_single_request(agent_team: AgentTeam, request: str):
    """단일 요청 실행"""
    console.print(f"\n[blue]🎯 요청 처리 시작:[/blue] {request}")

    try:
        result = agent_team.process_request(request)
        console.print(f"\n[green]✅ 요청 완료![/green] (ID: {result['request_id']})")
        _display_status(result)

    except Exception as e:
        console.print(f"\n[red]💥 요청 처리 실패:[/red] {e}")
        sys.exit(1)


def _display_status(status_info: dict):
    """상태 정보 표시"""
    table = Table(title="요청 상태")

    table.add_column("항목", style="cyan")
    table.add_column("값", style="white")

    for key, value in status_info.items():
        if key == "request_id":
            display_key = "요청 ID"
        elif key == "user_request":
            display_key = "사용자 요청"
        elif key == "status":
            display_key = "상태"
        elif key == "current_node":
            display_key = "현재 노드"
        elif key == "progress":
            display_key = "진행률"
        elif key == "quality_score":
            display_key = "품질 점수"
        elif key == "retry_count":
            display_key = "재시도 횟수"
        elif key == "created_at":
            display_key = "생성 시간"
        elif key == "updated_at":
            display_key = "수정 시간"
        else:
            display_key = key

        table.add_row(display_key, str(value))

    console.print(table)


def _display_request_list(requests: list):
    """요청 목록 표시"""
    if not requests:
        console.print("[yellow]조회된 요청이 없습니다.[/yellow]")
        return

    table = Table(title="요청 히스토리")

    table.add_column("ID", style="cyan")
    table.add_column("요청", style="white")
    table.add_column("상태", style="green")
    table.add_column("생성 시간", style="blue")

    for req in requests:
        table.add_row(
            req["session_id"][:8] + "...",
            req["user_request"],
            req["status"],
            req["created_at"]
        )

    console.print(table)


if __name__ == "__main__":
    cli()