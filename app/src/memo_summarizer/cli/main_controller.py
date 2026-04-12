#!/usr/bin/env python3
"""
메인 컨트롤러 (PARA 방법론 적용)
경로 파라미터 기반으로 Obsidian Vault를 처리합니다.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# memo_summarizer 패키지 모듈들 import
from memo_summarizer.utils.file_manager import FileManager
from memo_summarizer.services.memo_analyzer import MemoAnalyzer
from memo_summarizer.utils.markdown_processor import MarkdownProcessor
from memo_summarizer.services.daily_reporter import DailyReporter


class AgentController:
    """메인 에이전트 컨트롤러 (PARA + 경로 파라미터 + Multi-AI 지원)"""

    def __init__(self, vault_path: str, ai_client: str = "auto"):
        """
        Args:
            vault_path: Obsidian Vault의 루트 경로
            ai_client: AI 클라이언트 선택 ("claude", "gemini", "auto")
        """
        self.vault_path = Path(vault_path).resolve()

        print("🤖 PARA 메모 자동화 에이전트를 시작합니다...")
        print(f"🗂️ Vault 경로: {self.vault_path}")

        # 모듈 초기화 (vault_path + ai_client 전달)
        self.file_manager = FileManager(str(self.vault_path))
        self.memo_analyzer = MemoAnalyzer(str(self.vault_path), ai_client)
        self.markdown_processor = MarkdownProcessor()
        self.daily_reporter = DailyReporter(str(self.vault_path))

        # 세션별 총 토큰 사용량 초기화
        self.total_usage = {"input": 0, "output": 0, "total": 0}

        print("✅ 모든 모듈이 초기화되었습니다.")

    def _update_total_usage(self, usage: Dict[str, int]):
        """분석 결과에서 추출한 토큰 사용량을 세션 합계에 더합니다."""
        if not usage:
            return
            
        self.total_usage["input"] += usage.get("input", 0)
        self.total_usage["output"] += usage.get("output", 0)
        self.total_usage["total"] += usage.get("total", 0)

    def process_and_merge(self, file_path: Path, analysis: Dict[str, Any]) -> bool:
        """분석 결과를 PARA 분류에 따라 Projects/Areas 폴더에 병합합니다."""
        try:
            agendas = analysis.get("agendas", [])

            if not agendas:
                print("⚠️ 처리할 주제가 없습니다.")
                return False

            successful_merges = 0

            for agenda in agendas:
                topic = agenda["topic"]
                category = agenda.get("category", "Areas")  # 기본값은 Areas
                tasks = agenda["tasks"]
                summary = agenda["summary"]

                # 분석/파싱 실패한 항목은 건너뛰기
                if topic in ["분석 실패", "파싱 실패", "예기치 못한 오류"]:
                    print(f"⚠️ 실패한 주제 건너뛰기: {topic}")
                    continue

                # PARA 분류에 따른 아젠다 파일 경로 생성
                agenda_file_path = self.file_manager.get_agenda_file_path(topic, category)

                print(f"📝 병합 대상: {category}/{agenda_file_path.name} (주제: {topic})")

                # 파일 존재 여부에 따라 처리
                if agenda_file_path.exists():
                    print(f"🔄 기존 파일과 병합 중...")
                    existing_content = self.file_manager.read_file_content(agenda_file_path)
                    merged_content = self.markdown_processor.merge_with_existing_content(
                        existing_content, topic, tasks, summary
                    )
                else:
                    print(f"📄 새 파일 생성 중...")
                    merged_content = self.markdown_processor.create_new_agenda_file_content(
                        topic, tasks, summary
                    )

                # 안전한 파일 업데이트
                if self.file_manager.safe_update_file(agenda_file_path, merged_content):
                    print(f"✅ 완료: {category} > {topic} - {len(tasks)}개 할일, 요약 1개 추가됨")
                    successful_merges += 1
                else:
                    print(f"❌ 파일 저장 실패: {topic}")

            # 모든 주제 처리 완료 후 원본 파일 아카이브
            if successful_merges > 0:
                if self.file_manager.archive_file(file_path):
                    print(f"📦 총 {successful_merges}개 주제 처리 완료, 원본 파일 아카이브됨")

                    # 일일 보고서 업데이트
                    self.daily_reporter.create_or_update_daily_report(agendas)
                    return True
                else:
                    print(f"⚠️ 병합은 완료되었지만 아카이브에 실패했습니다.")
                    return False
            else:
                print("❌ 처리된 주제가 없어서 아카이브하지 않습니다.")
                return False

        except Exception as e:
            print(f"❌ 병합 처리 실패: {e}")
            return False

    def analyze_all_files(self, date_filter: str = None) -> List[Dict[str, Any]]:
        """모든 .md 파일을 분석합니다."""
        md_files = self.file_manager.get_md_files(date_filter)

        if not md_files:
            if date_filter:
                print(f"📂 {date_filter} 날짜에 해당하는 .md 파일이 없습니다.")
            else:
                print("📂 처리할 .md 파일이 없습니다.")
            return []

        if date_filter:
            print(f"📁 {date_filter} 날짜: {len(md_files)}개의 .md 파일을 발견했습니다.")
        else:
            print(f"📁 {len(md_files)}개의 .md 파일을 발견했습니다 (날짜순 정렬).")

        results = []

        for i, file_path in enumerate(md_files, 1):
            print(f"\n🔍 [{i}/{len(md_files)}] 분석 중: {file_path.name}")

            content = self.file_manager.read_file_content(file_path)
            if not content:
                print("⚠️  빈 파일이거나 읽을 수 없습니다. 건너뜁니다.")
                continue

            analysis = self.memo_analyzer.analyze_memo(content)

            # 토큰 합계 업데이트
            self._update_total_usage(analysis.get("usage"))

            # 파일 정보 추가
            analysis["filename"] = file_path.name
            analysis["filepath"] = str(file_path)

            results.append(analysis)

            agendas = analysis.get("agendas", [])
            print(f"✅ 분석 완료 - {len(agendas)}개 주제 발견")
            for j, agenda in enumerate(agendas, 1):
                category_icon = "🎯" if agenda.get("category") == "Projects" else "🏢"
                print(f"   {j}. {category_icon} {agenda['topic']} ({agenda.get('category', 'Areas')}) - {len(agenda['tasks'])}개 할 일")

        return results

    def analyze_and_merge_all_files(self, date_filter: str = None) -> List[Dict[str, Any]]:
        """모든 .md 파일을 분석하고 PARA 분류에 따라 병합합니다."""
        md_files = self.file_manager.get_md_files(date_filter)

        if not md_files:
            if date_filter:
                print(f"📂 {date_filter} 날짜에 해당하는 .md 파일이 없습니다.")
            else:
                print("📂 처리할 .md 파일이 없습니다.")
            return []

        if date_filter:
            print(f"📁 {date_filter} 날짜: {len(md_files)}개의 .md 파일을 발견했습니다.")
        else:
            print(f"📁 {len(md_files)}개의 .md 파일을 발견했습니다 (날짜순 정렬).")
        print("🚀 PARA 분석 및 병합을 시작합니다...\n")

        results = []
        successful_merges = 0

        for i, file_path in enumerate(md_files, 1):
            print(f"🔍 [{i}/{len(md_files)}] 처리 중: {file_path.name}")

            content = self.file_manager.read_file_content(file_path)
            if not content:
                print("⚠️  빈 파일이거나 읽을 수 없습니다. 건너뜁니다.")
                continue

            # 분석 수행
            analysis = self.memo_analyzer.analyze_memo(content)

            # 토큰 합계 업데이트
            self._update_total_usage(analysis.get("usage"))

            # 파일 정보 추가
            analysis["filename"] = file_path.name
            analysis["filepath"] = str(file_path)

            agendas = analysis.get("agendas", [])
            print(f"✅ 분석 완료 - {len(agendas)}개 주제 발견")
            for j, agenda in enumerate(agendas, 1):
                category_icon = "🎯" if agenda.get("category") == "Projects" else "🏢"
                print(f"   {j}. {category_icon} {agenda['topic']} ({agenda.get('category', 'Areas')}) - {len(agenda['tasks'])}개 할 일")

            # 병합 수행
            if self.process_and_merge(file_path, analysis):
                analysis["merged"] = True
                successful_merges += 1
            else:
                analysis["merged"] = False

            results.append(analysis)
            print("")  # 빈 줄 추가

        print(f"🎉 처리 완료!")
        print(f"   📊 총 {len(results)}개 파일 분석")
        print(f"   ✅ {successful_merges}개 파일 병합 성공")
        
        if self.total_usage["total"] > 0:
            print(f"   📊 세션 총 토큰: 입력 {self.total_usage['input']} / 출력 {self.total_usage['output']} / 총 {self.total_usage['total']}")

        return results

    def print_results(self, results: List[Dict[str, Any]]):
        """분석 결과를 보기 좋게 출력합니다 (PARA 분류 포함)."""
        if not results:
            print("\n📋 분석 결과가 없습니다.")
            return

        # 전체 통계 계산
        total_files = len(results)
        total_agendas = sum(len(result.get("agendas", [])) for result in results)
        total_tasks = sum(len(agenda.get("tasks", []))
                         for result in results
                         for agenda in result.get("agendas", []))

        # PARA 분류별 통계
        projects_count = sum(1 for result in results
                            for agenda in result.get("agendas", [])
                            if agenda.get("category") == "Projects")
        areas_count = sum(1 for result in results
                         for agenda in result.get("agendas", [])
                         if agenda.get("category") == "Areas")

        print(f"\n{'='*60}")
        print(f"📊 PARA 메모 분석 결과")
        print(f"📁 파일: {total_files}개 | 📋 주제: {total_agendas}개 | ✅ 할 일: {total_tasks}개")
        print(f"🎯 Projects: {projects_count}개 | 🏢 Areas: {areas_count}개")
        
        if self.total_usage["total"] > 0:
            print(f"📊 세션 총 토큰: 입력 {self.total_usage['input']} / 출력 {self.total_usage['output']} / 총 {self.total_usage['total']}")
            
        print(f"{'='*60}")

        for i, result in enumerate(results, 1):
            print(f"\n📄 [{i}] {result['filename']}")

            agendas = result.get("agendas", [])
            if not agendas:
                print("   ⚠️ 추출된 주제가 없습니다.")
                continue

            for j, agenda in enumerate(agendas, 1):
                category = agenda.get("category", "Areas")
                category_icon = "🎯" if category == "Projects" else "🏢"

                print(f"\n   {category_icon} 주제 {j}: {agenda['topic']} ({category})")
                print(f"   📝 요약: {agenda['summary']}")

                tasks = agenda.get('tasks', [])
                if tasks:
                    print(f"   ✅ 할 일 목록 ({len(tasks)}개):")
                    for k, task in enumerate(tasks, 1):
                        print(f"      {k}. {task}")
                else:
                    print("   ✅ 할 일: 없음")

            print("-" * 50)


def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱 설정
    parser = argparse.ArgumentParser(
        description="Obsidian 메모 자동화 에이전트",
        epilog="""예시:
  python main_controller.py /path/to/vault                    # 모든 파일 처리
  python main_controller.py /path/to/vault --analysis-only   # 분석만 수행
  python main_controller.py /path/to/vault --date 2026-02-11 # 특정 날짜만""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'vault_path',
        type=str,
        help='Obsidian Vault의 루트 경로 (필수)'
    )

    parser.add_argument(
        '--analysis-only',
        action='store_true',
        help='분석만 수행 (파일 수정하지 않음)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON 형식으로 결과 출력'
    )

    parser.add_argument(
        '-d', '--date',
        type=str,
        metavar='YYYY-MM-DD',
        help='특정 날짜 파일만 처리 (예: 2026-02-11)'
    )

    parser.add_argument(
        '--ai',
        type=str,
        choices=['claude', 'gemini', 'auto'],
        default='auto',
        help='AI 클라이언트 선택 (기본값: auto - 사용 가능한 것 자동 선택)'
    )

    try:
        args = parser.parse_args()

        # Vault 경로 검증
        vault_path = Path(args.vault_path)
        if not vault_path.exists():
            print(f"❌ Vault 경로가 존재하지 않습니다: {vault_path}")
            return 1

        if not vault_path.is_dir():
            print(f"❌ Vault 경로가 디렉토리가 아닙니다: {vault_path}")
            return 1

        # 날짜 형식 검증 (간단한 형식 체크)
        if args.date:
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', args.date):
                print("❌ 날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요. (예: 2026-02-11)")
                return 1

        controller = AgentController(str(vault_path), args.ai)

        if args.analysis_only:
            if args.date:
                print(f"🔍 {args.date} 날짜 파일 분석 전용 모드로 실행합니다...\n")
            else:
                print("🔍 분석 전용 모드로 실행합니다...\n")
            # 분석만 수행
            results = controller.analyze_all_files(args.date)

            # 결과 출력
            controller.print_results(results)

            print(f"\n🎉 분석 완료! 총 {len(results)}개 파일 처리됨")
        else:
            if args.date:
                print(f"🚀 {args.date} 날짜 PARA 메모 분석 및 병합을 시작합니다...\n")
            else:
                print("🚀 PARA 메모 분석 및 병합을 시작합니다...\n")
            # 분석 + 병합 수행
            results = controller.analyze_and_merge_all_files(args.date)

        # JSON 형태로도 출력 (필요한 경우)
        if results and args.json:
            # 모든 파일의 agendas를 하나로 합치기
            all_agendas = []
            for result in results:
                if "agendas" in result:
                    all_agendas.extend(result["agendas"])

            # 원하는 형식으로 출력
            output = {"agendas": all_agendas}
            print(f"\n📋 JSON 형식 결과:")
            print(json.dumps(output, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n👋 분석을 중단합니다...")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())