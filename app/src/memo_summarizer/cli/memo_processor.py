#!/usr/bin/env python3
"""
Obsidian 메모 자동 처리 시스템
00_INBOX의 메모를 분석하여 01_AGENDAS의 파일들과 병합
"""

import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import time

import schedule
from dotenv import load_dotenv
from anthropic import Anthropic
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 환경 변수 로드
load_dotenv()

class MemoProcessor:
    def __init__(self):
        # 경로 설정
        self.base_path = Path(__file__).parent
        self.inbox_path = self.base_path / "00_INBOX"
        self.archived_path = self.base_path / "00_INBOX" / "_ARCHIVED"
        self.agendas_path = self.base_path / "01_AGENDAS"

        # API 클라이언트 초기화
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        self.anthropic = Anthropic(api_key=api_key)

        # 로깅 설정
        log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('memo_processor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 처리 상태 추적
        self.last_process_time = 0
        self.min_interval = int(os.getenv('MIN_PROCESS_INTERVAL', 10)) * 60  # 초 단위

        self.logger.info("메모 프로세서가 초기화되었습니다.")

    def get_inbox_files(self) -> List[Path]:
        """INBOX 폴더에서 처리할 파일 목록을 가져옵니다."""
        files = []
        for file_path in self.inbox_path.iterdir():
            if (file_path.is_file() and
                file_path.suffix.lower() in ['.md', '.txt'] and
                not file_path.name.startswith('.')):
                files.append(file_path)
        return files

    def get_agenda_files(self) -> Dict[str, str]:
        """AGENDAS 폴더의 파일들과 내용을 가져옵니다."""
        agenda_files = {}
        if not self.agendas_path.exists():
            self.agendas_path.mkdir(exist_ok=True)
            return agenda_files

        for file_path in self.agendas_path.iterdir():
            if (file_path.is_file() and
                file_path.suffix.lower() in ['.md', '.txt'] and
                not file_path.name.startswith('.')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        agenda_files[str(file_path)] = f.read()
                except Exception as e:
                    self.logger.warning(f"파일 읽기 실패 {file_path}: {e}")
        return agenda_files

    def analyze_memo_with_ai(self, memo_content: str, agenda_files: Dict[str, str]) -> Dict:
        """AI를 사용하여 메모를 분석하고 적절한 처리 방법을 결정합니다."""

        # 기존 아젠다 파일 목록 생성
        agenda_list = ""
        for file_path, content in agenda_files.items():
            file_name = Path(file_path).name
            # 내용의 첫 200자만 요약으로 사용
            summary = content[:200].replace('\n', ' ').strip()
            if len(content) > 200:
                summary += "..."
            agenda_list += f"- {file_name}: {summary}\n"

        prompt = f"""
다음 메모를 분석하고, 기존 아젠다 파일들과 어떻게 통합할지 결정해주세요.

=== 새로운 메모 ===
{memo_content}

=== 기존 아젠다 파일들 ===
{agenda_list if agenda_list else "아직 아젠다 파일이 없습니다."}

다음 JSON 형식으로 응답해주세요:
{{
    "action": "merge|create_new",
    "target_file": "병합할 파일명 또는 새로 생성할 파일명",
    "category": "메모의 주요 카테고리 (예: 업무, 개인, 학습, 아이디어 등)",
    "priority": "high|medium|low",
    "merge_position": "top|bottom|specific_section",
    "content_to_add": "실제로 파일에 추가할 내용 (마크다운 형식)",
    "reasoning": "이렇게 결정한 이유"
}}

규칙:
1. 기존 파일과 관련성이 높으면 merge, 새로운 주제면 create_new
2. 파일명은 의미있고 구체적으로 (예: "2024-02-업무계획.md", "개인학습-Python.md")
3. content_to_add는 타임스탬프와 함께 적절히 포맷팅
4. 기존 파일 구조와 일관성 유지
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text

            # JSON 응답 파싱
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("AI 응답에서 JSON을 찾을 수 없습니다.")

        except Exception as e:
            self.logger.error(f"AI 분석 실패: {e}")
            # 기본값 반환
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            return {
                "action": "create_new",
                "target_file": f"메모-{datetime.now().strftime('%Y%m%d')}.md",
                "category": "일반",
                "priority": "medium",
                "merge_position": "bottom",
                "content_to_add": f"## {timestamp}\n\n{memo_content}\n\n---\n",
                "reasoning": "AI 분석 실패로 인한 기본 처리"
            }

    def process_memo(self, memo_file: Path, analysis: Dict) -> bool:
        """분석 결과에 따라 메모를 처리합니다."""
        try:
            target_file_path = self.agendas_path / analysis["target_file"]

            if analysis["action"] == "merge":
                # 기존 파일에 병합
                if target_file_path.exists():
                    with open(target_file_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()

                    if analysis["merge_position"] == "top":
                        new_content = analysis["content_to_add"] + "\n" + existing_content
                    else:  # bottom이 기본
                        new_content = existing_content + "\n" + analysis["content_to_add"]
                else:
                    # 파일이 없으면 새로 생성
                    new_content = analysis["content_to_add"]

            else:  # create_new
                # 새 파일 생성
                new_content = analysis["content_to_add"]

            # 파일 쓰기
            with open(target_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            self.logger.info(f"메모 처리 완료: {memo_file.name} -> {analysis['target_file']}")
            return True

        except Exception as e:
            self.logger.error(f"메모 처리 실패 {memo_file.name}: {e}")
            return False

    def archive_memo(self, memo_file: Path) -> bool:
        """처리된 메모를 아카이브로 이동합니다."""
        try:
            # 아카이브 폴더가 없으면 생성
            self.archived_path.mkdir(exist_ok=True)

            # 파일명에 타임스탬프 추가하여 중복 방지
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = f"{memo_file.stem}_{timestamp}{memo_file.suffix}"
            archived_path = self.archived_path / archived_name

            shutil.move(str(memo_file), str(archived_path))
            self.logger.info(f"메모 아카이브 완료: {memo_file.name} -> {archived_name}")
            return True

        except Exception as e:
            self.logger.error(f"메모 아카이브 실패 {memo_file.name}: {e}")
            return False

    def process_all_memos(self):
        """INBOX의 모든 메모를 처리합니다."""
        # 최소 처리 간격 체크 (0일 때는 체크 안 함)
        current_time = time.time()
        if self.min_interval > 0 and current_time - self.last_process_time < self.min_interval:
            self.logger.info("최소 처리 간격 미달로 건너뜀")
            return

        self.last_process_time = current_time

        self.logger.info("메모 처리 작업 시작")

        # 처리할 파일 목록 가져오기
        memo_files = self.get_inbox_files()
        if not memo_files:
            self.logger.info("처리할 메모가 없습니다.")
            return

        # 기존 아젠다 파일들 가져오기
        agenda_files = self.get_agenda_files()

        processed_count = 0
        for memo_file in memo_files:
            try:
                self.logger.info(f"처리 중: {memo_file.name}")

                # 메모 내용 읽기
                with open(memo_file, 'r', encoding='utf-8') as f:
                    memo_content = f.read().strip()

                if not memo_content:
                    self.logger.warning(f"빈 파일 건너뜀: {memo_file.name}")
                    continue

                # AI로 분석
                analysis = self.analyze_memo_with_ai(memo_content, agenda_files)
                self.logger.info(f"AI 분석 결과: {analysis['reasoning']}")

                # 메모 처리
                if self.process_memo(memo_file, analysis):
                    # 아카이브로 이동
                    if self.archive_memo(memo_file):
                        processed_count += 1
                        # 새로 생성된 파일이 있으면 아젠다 목록 업데이트
                        agenda_files = self.get_agenda_files()

            except Exception as e:
                self.logger.error(f"메모 처리 중 오류 {memo_file.name}: {e}")

        self.logger.info(f"메모 처리 완료: {processed_count}개 파일 처리됨")


class MemoFileHandler(FileSystemEventHandler):
    """파일 시스템 이벤트를 처리하는 핸들러"""

    def __init__(self, processor: MemoProcessor):
        self.processor = processor
        self.logger = logging.getLogger(__name__)

    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if (file_path.suffix.lower() in ['.md', '.txt'] and
                not file_path.name.startswith('.')):
                self.logger.info(f"새 파일 감지: {file_path.name}")
                # 파일 쓰기가 완료될 때까지 잠시 대기
                time.sleep(2)
                self.processor.process_all_memos()


def main():
    """메인 실행 함수"""
    try:
        processor = MemoProcessor()

        # 파일 감시자 설정 (비활성화)
        # event_handler = MemoFileHandler(processor)
        # observer = Observer()
        # observer.schedule(event_handler, str(processor.inbox_path), recursive=False)
        # observer.start()

        # 스케줄 설정
        process_time = os.getenv('PROCESS_TIME', '09:00')
        schedule.every().day.at(process_time).do(processor.process_all_memos)

        # 시작 시 한 번 처리
        processor.process_all_memos()

        print(f"🚀 메모 프로세서가 시작되었습니다!")
        print(f"📁 처리 폴더: {processor.inbox_path}")
        print(f"⏰ 정기 처리 시간: {process_time}")
        print(f"📋 처리 결과는 {processor.agendas_path}에 저장됩니다")
        print(f"📦 처리된 파일은 {processor.archived_path}로 이동됩니다")
        print(f"🔕 파일 감시 기능: 비활성화")
        print("Ctrl+C로 종료할 수 있습니다.\n")

        # 메인 루프
        while True:
            schedule.run_pending()
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n👋 메모 프로세서를 종료합니다...")
        # observer.stop()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        # if 'observer' in locals():
        #     observer.join()
        pass


if __name__ == "__main__":
    main()