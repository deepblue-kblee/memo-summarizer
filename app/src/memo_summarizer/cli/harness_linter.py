#!/usr/bin/env python3
"""
Harness Engineering Linter
자동화된 기계적 강제 메커니즘으로 에이전트 자율 운영 품질 보장

Core Principles:
1. Document size limits (AGENTS.md < 100 lines)
2. Duplication detection (token-level analysis)
3. Markdown link verification
4. Layer dependency enforcement
5. PARA classification validation
"""

import os
import re
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class HarnessLinter:
    """Harness Engineering 린터 - 품질 및 일관성 자동 검증"""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.violations: List[Dict] = []
        self.warnings: List[Dict] = []

        # 설정값
        self.config = {
            "max_agents_md_lines": 100,
            "max_document_lines": 1000,
            "duplication_threshold": 0.8,  # 80% 유사성
            "layer_dependencies": {
                "types": [],
                "config": ["types"],
                "repo": ["types", "config"],
                "services": ["types", "config", "repo"],
                "runtime": ["types", "config", "repo", "services"],
                "ui": ["types", "config", "repo", "services", "runtime"]
            }
        }

    def run_all_checks(self) -> bool:
        """모든 검증 실행"""
        print("🔍 Harness Engineering 품질 검증 시작...")

        # 1. 문서 크기 검증
        self._validate_document_sizes()

        # 2. 중복 내용 감지
        self._detect_duplication()

        # 3. 마크다운 링크 검증
        self._verify_markdown_links()

        # 4. 계층 의존성 검증 (Python 파일)
        self._enforce_layer_dependencies()

        # 5. PARA 분류 검증
        self._validate_para_classification()

        # 결과 출력
        return self._report_results()

    def _validate_document_sizes(self):
        """문서 크기 제한 검증"""
        print("📏 문서 크기 검증 중...")

        # AGENTS.md 특별 검사
        agents_md = self.repo_root / "AGENTS.md"
        if agents_md.exists():
            lines = len(agents_md.read_text().splitlines())
            if lines > self.config["max_agents_md_lines"]:
                self._add_violation(
                    "document_size",
                    f"AGENTS.md exceeds {self.config['max_agents_md_lines']} lines: {lines}",
                    str(agents_md)
                )

        # 다른 마크다운 파일들
        for md_file in self.repo_root.rglob("*.md"):
            if md_file.name == "AGENTS.md":
                continue

            lines = len(md_file.read_text(encoding='utf-8').splitlines())
            if lines > self.config["max_document_lines"]:
                self._add_warning(
                    "large_document",
                    f"Large document ({lines} lines): consider splitting",
                    str(md_file.relative_to(self.repo_root))
                )

    def _detect_duplication(self):
        """중복 내용 감지 (토큰 레벨)"""
        print("🔍 중복 내용 감지 중...")

        md_files = list(self.repo_root.rglob("*.md"))
        content_hashes = {}

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')

                # 섹션별로 분할하여 해시 생성
                sections = self._extract_sections(content)

                for section_title, section_content in sections.items():
                    if len(section_content.strip()) < 100:  # 너무 짧은 섹션 제외
                        continue

                    # 정규화된 해시 생성
                    normalized_content = self._normalize_text(section_content)
                    content_hash = hashlib.md5(normalized_content.encode()).hexdigest()

                    if content_hash in content_hashes:
                        self._add_violation(
                            "duplication",
                            f"Duplicate section '{section_title}' found",
                            f"{md_file.relative_to(self.repo_root)} <-> {content_hashes[content_hash]}"
                        )
                    else:
                        content_hashes[content_hash] = f"{md_file.relative_to(self.repo_root)}::{section_title}"

            except Exception as e:
                self._add_warning("file_read_error", f"Cannot read file: {e}", str(md_file))

    def _verify_markdown_links(self):
        """마크다운 링크 검증"""
        print("🔗 마크다운 링크 검증 중...")

        for md_file in self.repo_root.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')

                # 내부 링크 추출 [text](path)
                internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

                for link_text, link_path in internal_links:
                    if link_path.startswith(('http://', 'https://', '#')):
                        continue  # 외부 링크 및 앵커 제외

                    # 상대 경로 해석
                    target_path = (md_file.parent / link_path).resolve()

                    if not target_path.exists():
                        self._add_violation(
                            "broken_link",
                            f"Broken internal link: [{link_text}]({link_path})",
                            str(md_file.relative_to(self.repo_root))
                        )

            except Exception as e:
                self._add_warning("link_check_error", f"Cannot check links: {e}", str(md_file))

    def _enforce_layer_dependencies(self):
        """계층 의존성 강제 (Python imports)"""
        print("🏗️ 계층 의존성 검증 중...")

        app_src = self.repo_root / "app" / "src" / "memo_summarizer"
        if not app_src.exists():
            return

        for layer, allowed_deps in self.config["layer_dependencies"].items():
            layer_dir = app_src / layer
            if not layer_dir.exists():
                continue

            for py_file in layer_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')

                    # import 문 추출
                    imports = self._extract_imports(content)

                    for import_stmt in imports:
                        # memo_summarizer.* 패턴의 import만 검사
                        if "memo_summarizer." in import_stmt:
                            imported_layer = self._extract_layer_from_import(import_stmt)

                            if imported_layer and imported_layer not in allowed_deps:
                                self._add_violation(
                                    "layer_violation",
                                    f"Layer '{layer}' cannot import from '{imported_layer}': {import_stmt}",
                                    str(py_file.relative_to(self.repo_root))
                                )

                except Exception as e:
                    self._add_warning("dependency_check_error", f"Cannot check dependencies: {e}", str(py_file))

    def _validate_para_classification(self):
        """PARA 분류 규칙 일관성 검증"""
        print("📂 PARA 분류 규칙 검증 중...")

        rules_file = self.repo_root / "app" / "config" / "rules.json"
        if not rules_file.exists():
            self._add_warning("missing_config", "PARA rules.json not found", str(rules_file))
            return

        try:
            rules = json.loads(rules_file.read_text())

            # para_classification 섹션 확인
            if "para_classification" not in rules:
                self._add_violation("para_config", "Missing para_classification section", str(rules_file))
                return

            para_config = rules["para_classification"]

            # 필수 키 검증
            required_keys = ["projects", "areas"]
            for key in required_keys:
                if key not in para_config:
                    self._add_violation("para_config", f"Missing required key: {key}", str(rules_file))
                elif "keywords" not in para_config[key]:
                    self._add_violation("para_config", f"Missing keywords in {key}", str(rules_file))

            # 키워드 중복 검사
            all_keywords = set()
            for category, config in para_config.items():
                if isinstance(config, dict) and "keywords" in config:
                    for keyword in config["keywords"]:
                        if keyword in all_keywords:
                            self._add_violation("para_config", f"Duplicate keyword: {keyword}", str(rules_file))
                        all_keywords.add(keyword)

        except json.JSONDecodeError as e:
            self._add_violation("para_config", f"Invalid JSON in rules.json: {e}", str(rules_file))

    # 헬퍼 메서드들

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """마크다운에서 섹션 추출"""
        sections = {}
        current_section = ""
        current_content = []

        for line in content.splitlines():
            if line.startswith('#'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)

        # 마지막 섹션
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화 (공백, 특수문자 제거)"""
        # 공백 정규화
        text = re.sub(r'\s+', ' ', text)
        # 특수 문자 제거 (마크다운 문법)
        text = re.sub(r'[*_`#\-\[\](){}]', '', text)
        return text.strip().lower()

    def _extract_imports(self, content: str) -> List[str]:
        """Python 파일에서 import 문 추출"""
        import_pattern = r'^\s*(?:from\s+([a-zA-Z0-9_.]+)\s+import|import\s+([a-zA-Z0-9_.]+))'
        imports = []

        for line in content.splitlines():
            match = re.match(import_pattern, line)
            if match:
                module = match.group(1) or match.group(2)
                imports.append(line.strip())

        return imports

    def _extract_layer_from_import(self, import_stmt: str) -> Optional[str]:
        """import 문에서 계층 추출"""
        patterns = [
            r'memo_summarizer\.(\w+)',
            r'from\s+memo_summarizer\.(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, import_stmt)
            if match:
                return match.group(1)

        return None

    def _add_violation(self, category: str, message: str, file_path: str):
        """위반 사항 추가"""
        self.violations.append({
            "category": category,
            "message": message,
            "file": file_path,
            "severity": "error"
        })

    def _add_warning(self, category: str, message: str, file_path: str):
        """경고 사항 추가"""
        self.warnings.append({
            "category": category,
            "message": message,
            "file": file_path,
            "severity": "warning"
        })

    def _report_results(self) -> bool:
        """검증 결과 보고"""
        print("\n" + "="*60)
        print("🏗️ Harness Engineering 품질 검증 완료")
        print("="*60)

        if not self.violations and not self.warnings:
            print("✅ 모든 검증 통과! Agent-first 환경이 완벽합니다.")
            return True

        # 위반 사항 출력
        if self.violations:
            print(f"\n❌ {len(self.violations)}개의 위반 사항 발견:")
            for v in self.violations:
                print(f"  [{v['category']}] {v['file']}: {v['message']}")

        # 경고 사항 출력
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)}개의 경고 사항:")
            for w in self.warnings:
                print(f"  [{w['category']}] {w['file']}: {w['message']}")

        # 요약
        print(f"\n📊 요약: {len(self.violations)} errors, {len(self.warnings)} warnings")

        return len(self.violations) == 0


def main():
    """CLI 진입점"""
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        print("🔧 자동 수정 모드는 아직 구현되지 않았습니다.")
        return 1

    linter = HarnessLinter()
    success = linter.run_all_checks()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())