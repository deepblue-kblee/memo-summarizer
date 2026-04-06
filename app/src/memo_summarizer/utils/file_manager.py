#!/usr/bin/env python3
"""
파일 관리 모듈
파일 읽기, 쓰기, 아카이브 등의 파일 I/O 작업을 담당합니다.
"""

import os
import shutil
import re
from pathlib import Path
from typing import List
from datetime import datetime


class FileManager:
    """파일 관리 클래스"""

    def __init__(self, base_path: str = None):
        if base_path is None:
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path).resolve()

        self.inbox_path = self.base_path / "00_INBOX"
        self.archived_path = self.base_path / "00_INBOX" / "_ARCHIVED"
        self.agendas_path = self.base_path / "01_AGENDAS"

        # PARA 방법론 디렉토리
        self.projects_path = self.agendas_path / "Projects"
        self.areas_path = self.agendas_path / "Areas"

        # PARA 디렉토리 생성
        self.projects_path.mkdir(parents=True, exist_ok=True)
        self.areas_path.mkdir(parents=True, exist_ok=True)

        print("📁 파일 관리자가 초기화되었습니다.")

    def get_md_files(self, date_filter: str = None) -> List[Path]:
        """00_INBOX 폴더에서 .md 파일 목록을 가져옵니다. (_ARCHIVED 제외)

        Args:
            date_filter: YYYY-MM-DD 형식의 날짜. 해당 날짜로 시작하는 파일만 선택
        """
        md_files = []

        if not self.inbox_path.exists():
            print(f"❌ INBOX 폴더가 존재하지 않습니다: {self.inbox_path}")
            return md_files

        for file_path in self.inbox_path.iterdir():
            # _ARCHIVED 폴더는 제외
            if file_path.name == "_ARCHIVED":
                continue

            # .md 파일만 선택
            if (file_path.is_file() and
                file_path.suffix.lower() == '.md' and
                not file_path.name.startswith('.')):

                # 날짜 필터 적용
                if date_filter:
                    if not file_path.name.startswith(date_filter):
                        continue

                md_files.append(file_path)

        # 파일명 기준 날짜순 정렬 (날짜 형식이 YYYY-MM-DD로 시작하므로 문자열 정렬로 충분)
        return sorted(md_files, key=lambda x: x.name)

    def read_file_content(self, file_path: Path) -> str:
        """파일 내용을 읽어옵니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return content
        except Exception as e:
            print(f"❌ 파일 읽기 실패 {file_path.name}: {e}")
            return ""

    def write_file(self, file_path: Path, content: str) -> bool:
        """파일에 내용을 씁니다."""
        try:
            # 디렉토리가 없으면 생성
            file_path.parent.mkdir(exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"❌ 파일 쓰기 실패 {file_path.name}: {e}")
            return False

    def archive_file(self, file_path: Path) -> bool:
        """파일을 아카이브로 이동합니다 (원본 파일명 유지)."""
        try:
            # 아카이브 폴더가 없으면 생성
            self.archived_path.mkdir(exist_ok=True)

            # 원본 파일명으로 아카이브 경로 생성
            archived_file_path = self.archived_path / file_path.name

            # 동일한 이름의 파일이 이미 있으면 순번 추가
            counter = 1
            while archived_file_path.exists():
                name_part = file_path.stem
                extension = file_path.suffix
                archived_name = f"{name_part}_{counter:03d}{extension}"
                archived_file_path = self.archived_path / archived_name
                counter += 1

            shutil.move(str(file_path), str(archived_file_path))
            print(f"📦 아카이브 완료: {file_path.name} -> {archived_file_path.name}")
            return True

        except Exception as e:
            print(f"❌ 아카이브 실패 {file_path.name}: {e}")
            return False

    def safe_update_file(self, file_path: Path, new_content: str) -> bool:
        """안전한 파일 업데이트 (Rename before Delete 패턴)."""
        try:
            # 디렉토리가 없으면 생성
            file_path.parent.mkdir(exist_ok=True)

            # 기존 파일이 존재하는 경우 안전한 업데이트 프로세스
            if file_path.exists():
                # 1. 기존 파일을 임시 이름으로 변경
                temp_file_path = file_path.parent / f"_{file_path.name}"

                # 임시 파일명이 이미 존재하면 다른 이름 사용
                counter = 1
                while temp_file_path.exists():
                    temp_file_path = file_path.parent / f"_{file_path.stem}_{counter}{file_path.suffix}"
                    counter += 1

                print(f"🔒 기존 파일 임시 백업: {file_path.name} -> {temp_file_path.name}")
                shutil.move(str(file_path), str(temp_file_path))

                try:
                    # 2. 새 파일 작성
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    # 3. 새 파일 작성 성공 후 임시 파일 삭제
                    temp_file_path.unlink()
                    print(f"✅ 파일 업데이트 완료: {file_path.name}")
                    return True

                except Exception as write_error:
                    # 새 파일 작성 실패시 원본 파일 복구
                    if temp_file_path.exists():
                        shutil.move(str(temp_file_path), str(file_path))
                        print(f"🔄 원본 파일 복구 완료: {file_path.name}")
                    raise write_error

            else:
                # 새 파일인 경우 직접 생성
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"📄 새 파일 생성: {file_path.name}")
                return True

        except Exception as e:
            print(f"❌ 파일 업데이트 실패 {file_path.name}: {e}")
            return False

    def sanitize_filename(self, topic: str) -> str:
        """주제를 파일명에 적합하게 변환합니다."""
        # 파일명에 사용할 수 없는 문자 제거/변환
        sanitized = re.sub(r'[<>:"/\\|?*]', '', topic)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized

    def get_agenda_file_path(self, topic: str, category: str = "Areas") -> Path:
        """주제와 분류를 기반으로 아젠다 파일 경로를 생성합니다.

        Args:
            topic: 주제명
            category: 디렉토리 분류 ("Projects" 또는 "Areas", 기본값: "Areas")
        """
        filename = f"{self.sanitize_filename(topic)}.md"

        if category == "Projects":
            return self.projects_path / filename
        else:
            return self.areas_path / filename