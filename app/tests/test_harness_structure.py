"""
Harness Engineering 구조적 테스트

이 모듈은 프로젝트의 구조적 무결성을 검증합니다.
- 문서 크기 제한 준수
- 계층 경계 위반 방지
- PARA 분류 규칙 일관성
- 중복 내용 방지
- 디렉토리 구조 무결성
"""

import os
import unittest
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestHarnessStructure(unittest.TestCase):
    """Harness Engineering 구조적 테스트"""

    def test_agents_md_size_limit(self):
        """AGENTS.md가 100줄 초과하면 실패"""
        agents_md = PROJECT_ROOT / "AGENTS.md"

        assert agents_md.exists(), "AGENTS.md 파일이 존재하지 않습니다"

        with open(agents_md, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        line_count = len(lines)
        assert line_count <= 100, f"AGENTS.md가 {line_count}줄로 100줄 제한을 초과했습니다"

    def test_no_duplication_in_docs(self):
        """문서 간 중복 내용 검사"""
        # 주요 문서들 스캔
        doc_patterns = [
            ".ai-docs/**/*.md",
            "docs/**/*.md",
            "*.md"
        ]

        doc_files = []
        for pattern in doc_patterns:
            doc_files.extend(PROJECT_ROOT.rglob(pattern))

        # 섹션 헤더 추출 (중복 가능성이 높은 부분)
        section_map = defaultdict(list)

        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 마크다운 헤더 추출 (##, ###)
                headers = re.findall(r'^#{2,3}\s+(.+)$', content, re.MULTILINE)

                for header in headers:
                    # 일반적인 헤더는 무시 (목차, 개요 등)
                    if header.lower() not in ['목차', '개요', 'overview', 'table of contents']:
                        section_map[header].append(doc_file.name)

            except (UnicodeDecodeError, PermissionError):
                continue

        # 중복 섹션 찾기
        duplicated_sections = {
            section: files for section, files in section_map.items()
            if len(files) > 1
        }

        # 허용된 중복들 (예외 처리)
        allowed_duplications = {
            "설치", "Installation", "사용법", "Usage",
            "예제", "Examples", "설정", "Configuration"
        }

        critical_duplications = {
            section: files for section, files in duplicated_sections.items()
            if section not in allowed_duplications and len(files) > 2  # 3개 이상 파일에 중복
        }

        assert not critical_duplications, (
            f"심각한 중복 섹션 발견: {critical_duplications}\n"
            "문서 구조를 정리해주세요."
        )

    def test_layer_boundary_violations(self):
        """계층 경계 위반 검사 (memo_summarizer.types → services 금지 등)"""

        app_src = PROJECT_ROOT / "app" / "src" / "memo_summarizer"
        if not app_src.exists():
            self.skipTest("app/src/memo_summarizer 디렉토리가 없습니다")

        # 계층별 임포트 규칙 정의
        layer_rules = {
            'types': [],  # types는 다른 계층을 임포트하지 않음
            'utils': ['types'],  # utils는 types만 임포트 가능
            'core': ['types', 'utils'],  # core는 types, utils 임포트 가능
            'services': ['types', 'utils', 'core'],  # services는 types, utils, core 임포트 가능
            'cli': ['types', 'utils', 'core', 'services']  # cli는 모든 계층 임포트 가능
        }

        violations = []

        for layer, allowed_imports in layer_rules.items():
            layer_dir = app_src / layer
            if not layer_dir.exists():
                continue

            for py_file in layer_dir.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # memo_summarizer 내부 임포트 찾기
                    imports = re.findall(
                        r'from\s+memo_summarizer\.(\w+)', content
                    )

                    for imported_layer in imports:
                        if imported_layer not in allowed_imports:
                            violations.append(
                                f"{layer}/{py_file.name}: 금지된 임포트 memo_summarizer.{imported_layer}"
                            )

                except (UnicodeDecodeError, PermissionError):
                    continue

        assert not violations, (
            f"계층 경계 위반 발견:\n" + "\n".join(violations) +
            "\n계층별 임포트 규칙을 준수해주세요."
        )

    def test_para_rules_consistency(self):
        """PARA 분류 규칙 일관성 검사"""

        # rules.json 파일들 찾기
        rules_files = [
            PROJECT_ROOT / "app" / "config" / "rules.json",
            PROJECT_ROOT / ".agent" / "config" / "rules.json"
        ]

        existing_rules = []
        for rules_file in rules_files:
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                existing_rules.append((rules_file.name, rules))

        assert existing_rules, "PARA 규칙 파일이 없습니다"

        # 여러 rules.json이 있으면 일관성 검사
        if len(existing_rules) > 1:
            base_name, base_rules = existing_rules[0]

            for rules_name, rules in existing_rules[1:]:
                # para_classification 구조 일관성 검사
                if "para_classification" in base_rules and "para_classification" in rules:
                    base_projects = set(base_rules["para_classification"].get("projects", {}).get("keywords", []))
                    current_projects = set(rules["para_classification"].get("projects", {}).get("keywords", []))

                    # 80% 이상 겹쳐야 함
                    if base_projects and current_projects:
                        intersection = base_projects & current_projects
                        union = base_projects | current_projects
                        similarity = len(intersection) / len(union)

                        assert similarity >= 0.8, (
                            f"PARA 규칙 불일치: {base_name} vs {rules_name}\n"
                            f"유사도: {similarity:.2%} (80% 미만)\n"
                            f"차이점: {base_projects ^ current_projects}"
                        )

    def test_app_structure_integrity(self):
        """app/ 디렉토리 구조 무결성 검증"""

        app_dir = PROJECT_ROOT / "app"
        assert app_dir.exists(), "app/ 디렉토리가 없습니다"

        # 필수 디렉토리 구조
        required_structure = {
            "src": {"memo_summarizer": ["cli", "services", "core", "utils", "types"]},
            "tests": [],
            "config": [],
            "scripts": [],
            "logs": [],
            "build": []
        }

        missing_dirs = []

        for dir_name, subdirs in required_structure.items():
            dir_path = app_dir / dir_name

            if not dir_path.exists():
                missing_dirs.append(f"app/{dir_name}")
                continue

            if isinstance(subdirs, dict):
                for subdir_name, subsubdirs in subdirs.items():
                    subdir_path = dir_path / subdir_name
                    if not subdir_path.exists():
                        missing_dirs.append(f"app/{dir_name}/{subdir_name}")
                        continue

                    for subsubdir in subsubdirs:
                        subsubdir_path = subdir_path / subsubdir
                        if not subsubdir_path.exists():
                            missing_dirs.append(f"app/{dir_name}/{subdir_name}/{subsubdir}")

        assert not missing_dirs, (
            f"필수 디렉토리 구조가 없습니다:\n" +
            "\n".join(missing_dirs) +
            "\nModern Python 프로젝트 구조를 유지해주세요."
        )

        # __init__.py 파일 존재 확인
        memo_summarizer_dir = app_dir / "src" / "memo_summarizer"
        if memo_summarizer_dir.exists():
            required_init_files = [
                memo_summarizer_dir / "__init__.py",
                memo_summarizer_dir / "cli" / "__init__.py",
                memo_summarizer_dir / "services" / "__init__.py",
                memo_summarizer_dir / "core" / "__init__.py",
                memo_summarizer_dir / "utils" / "__init__.py",
                memo_summarizer_dir / "types" / "__init__.py"
            ]

            missing_init = [
                str(init_file.relative_to(PROJECT_ROOT))
                for init_file in required_init_files
                if init_file.parent.exists() and not init_file.exists()
            ]

            assert not missing_init, (
                f"__init__.py 파일이 없습니다:\n" + "\n".join(missing_init) +
                "\nPython 패키지 구조를 유지해주세요."
            )


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    unittest.main(verbosity=2)