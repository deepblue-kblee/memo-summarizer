#!/usr/bin/env python3
"""
메모 분석 모듈
Claude Code CLI를 사용하여 메모 내용을 분석하고 다중 주제를 추출합니다.
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from claude_client import ClaudeClient
from gemini_client import GeminiClient


class MemoAnalyzer:
    """메모 분석 클래스"""

    def __init__(self, vault_path: str = None, ai_client: str = "auto"):
        """
        Args:
            vault_path: Vault 경로 (선택사항)
            ai_client: AI 클라이언트 선택 ("claude", "gemini", "auto")
        """
        self.ai_client = self._initialize_ai_client(ai_client)

        # 로그 디렉토리 설정 (agent 패키지 기준으로 상대 경로 사용)
        # 현재 스크립트의 상위 디렉토리(.agent)에서 logs 폴더 설정
        current_file_dir = Path(__file__).parent  # .agent/bin
        agent_dir = current_file_dir.parent       # .agent
        self.log_dir = agent_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # 오늘 날짜로 로그 파일 경로 생성
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"memo_analyzer_{today}.log"

        print("🔍 메모 분석기가 초기화되었습니다.")
        print(f"📋 로그 파일: {self.log_file}")

    def _initialize_ai_client(self, ai_client: str):
        """AI 클라이언트를 초기화합니다."""
        if ai_client == "claude":
            print("🔵 Claude 클라이언트를 사용합니다.")
            return ClaudeClient()
        elif ai_client == "gemini":
            print("🟡 Gemini 클라이언트를 사용합니다.")
            return GeminiClient()
        elif ai_client == "auto":
            # 자동 선택: claude -> gemini 순으로 시도
            print("🤖 사용 가능한 AI 클라이언트를 자동으로 선택합니다...")
            try:
                print("   🔵 Claude 시도 중...")
                return ClaudeClient()
            except Exception as e:
                print(f"   ⚠️ Claude 실패: {e}")
                try:
                    print("   🟡 Gemini 시도 중...")
                    return GeminiClient()
                except Exception as e2:
                    print(f"   ❌ Gemini도 실패: {e2}")
                    raise RuntimeError("사용 가능한 AI 클라이언트가 없습니다. claude 또는 gemini CLI를 설치하고 인증해주세요.")
        else:
            raise ValueError(f"지원하지 않는 AI 클라이언트: {ai_client}. 'claude', 'gemini', 'auto' 중 하나를 선택해주세요.")

    def _log_to_file(self, message: str):
        """로그 파일에 메시지를 추가 (append) 방식으로 기록합니다."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"⚠️ 로그 기록 실패: {e}")

    def _extract_json_from_response(self, response_text: str) -> str:
        """정규표현식을 사용하여 응답에서 가장 바깥쪽의 JSON 객체를 추출합니다."""
        # 먼저 기존 방식으로 코드 블록 처리
        if "```json" in response_text:
            start_idx = response_text.find("```json") + 7
            end_idx = response_text.find("```", start_idx)
            if end_idx > start_idx:
                response_text = response_text[start_idx:end_idx].strip()
        elif "```" in response_text:
            start_idx = response_text.find("```") + 3
            end_idx = response_text.find("```", start_idx)
            if end_idx > start_idx:
                response_text = response_text[start_idx:end_idx].strip()

        # 정규표현식으로 가장 바깥쪽 JSON 객체 추출
        # 중괄호로 시작해서 끝나는 부분을 찾되, 중첩된 중괄호도 올바르게 처리
        pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
        matches = re.findall(pattern, response_text, re.DOTALL)

        if matches:
            # 가장 긴 매치를 선택 (일반적으로 가장 바깥쪽 객체)
            json_candidate = max(matches, key=len)
            return json_candidate.strip()

        # 매치가 없으면 원본 반환
        return response_text.strip()

    def analyze_memo(self, content: str) -> Dict[str, Any]:
        """Claude Code CLI를 사용하여 메모를 분석합니다 (다중 주제 지원)."""

        prompt = f"""
다음 메모 내용을 분석하여 독립적인 업무/의사결정 관련 주제들을 모두 추출해주세요.

메모 내용:
{content}

**CRITICAL REQUIREMENT - STRICTLY JSON OUTPUT ONLY:**
- No conversational filler, strictly JSON output
- Do not include any explanations, comments, or additional text
- Output ONLY the JSON data structure below
- No markdown formatting, just pure JSON

REQUIRED JSON FORMAT:
{{
    "agendas": [
        {{
            "topic": "주제1",
            "category": "Projects",
            "tasks": ["할일1", "할일2"],
            "summary": "주제1의 핵심 내용 요약"
        }},
        {{
            "topic": "주제2",
            "category": "Areas",
            "tasks": ["할일3"],
            "summary": "주제2의 핵심 내용 요약"
        }}
    ]
}}

**PARA 분류 기준 (category 필드 - 매우 중요!):**
- **"Projects"**: 명확한 마감이나 완료 목표가 있는 프로젝트성 주제
  * 키워드: 마감, 출시, 완료, 구현, 개발, 프로젝트, 런칭, 배포, 제작, 설계
  * 예시: "새로운 기능 개발", "시스템 마이그레이션", "제품 출시", "웹사이트 리뉴얼"
- **"Areas"**: 지속적인 관리와 업데이트가 필요한 책임 영역 (기본값)
  * 키워드: 관리, 운영, 유지보수, 정기, 지속, 모니터링, 개선, 1on1, 팀운영
  * 예시: "팀 관리", "정기 미팅", "성과 관리", "고객 지원", "일상 업무"

분석 규칙:
1. 메모에서 독립적인 업무/프로젝트/의사결정 관련 주제들을 모두 찾아 분리
2. 단순 인사치레, 개인적 낙서, 의미 없는 메모는 제외하고 실제 '업무'나 '의사결정'과 관련된 내용만 포함
3. topic은 파일명으로 사용 가능한 간결한 형태로 작성 (예: "믹스패널", "조직개편", "프로젝트A")
4. category는 위 PARA 기준에 따라 "Projects" 또는 "Areas"로 분류 (불확실하면 "Areas")
5. tasks는 해당 주제에서 추출할 수 있는 구체적인 행동 항목들 (없으면 빈 배열 [])
6. summary는 해당 주제의 핵심 내용을 2-3 문장으로 요약
7. 주제가 없으면 agendas를 빈 배열 []로 설정

**FINAL WARNING: RESPOND WITH ONLY THE JSON OBJECT - NO OTHER TEXT WHATSOEVER**
"""

        # Claude Code CLI 호출
        try:
            response = self.ai_client.call_claude_code(prompt)
        except Exception as e:
            error_msg = f"Claude Code CLI 호출 중 예외 발생: {str(e)}"
            print(f"❌ {error_msg}")
            self._log_to_file(f"ERROR - API_CALL_EXCEPTION: {error_msg}")
            return {
                "agendas": [{
                    "topic": "분석 실패",
                    "tasks": [],
                    "summary": error_msg
                }]
            }

        if not response["success"]:
            error_msg = f"Claude Code 호출 실패: {response['error']}"
            print(f"❌ {error_msg}")
            self._log_to_file(f"ERROR - API_CALL_FAILED: {error_msg}")
            return {
                "agendas": [{
                    "topic": "분석 실패",
                    "tasks": [],
                    "summary": error_msg
                }]
            }

        # 원본 응답을 로그에 기록 및 터미널 출력
        raw_response = response.get("content", "").strip()
        print(f"📥 API 원본 응답:\n{raw_response}")
        self._log_to_file(f"SUCCESS - RAW_RESPONSE: {raw_response}")

        try:
            # 정규표현식을 사용한 JSON 추출
            extracted_json = self._extract_json_from_response(raw_response)
            print(f"🔍 추출된 JSON:\n{extracted_json}")
            self._log_to_file(f"SUCCESS - EXTRACTED_JSON: {extracted_json}")

            # JSON 파싱
            try:
                result = json.loads(extracted_json)
            except json.JSONDecodeError as json_error:
                # JSON 파싱 실패 시 추가 정제 시도
                print(f"⚠️ 1차 JSON 파싱 실패, 추가 정제 시도: {json_error}")

                # 줄바꿈 및 특수 문자 정리
                cleaned_json = extracted_json.replace('\n', '').replace('\r', '').replace('\t', ' ')
                cleaned_json = re.sub(r'\s+', ' ', cleaned_json)  # 연속된 공백 제거

                print(f"🧹 정제된 JSON:\n{cleaned_json}")
                self._log_to_file(f"WARNING - CLEANED_JSON_RETRY: {cleaned_json}")

                try:
                    result = json.loads(cleaned_json)
                    print("✅ 2차 파싱 성공!")
                except json.JSONDecodeError as second_error:
                    raise json.JSONDecodeError(
                        f"1차 오류: {json_error}, 2차 오류: {second_error}",
                        cleaned_json, 0
                    )

            # 필수 필드 검증
            if "agendas" not in result or not isinstance(result["agendas"], list):
                raise ValueError("agendas 필드가 누락되었거나 잘못된 형식입니다.")

            # 각 아젠다 항목 검증 및 정제
            for i, agenda in enumerate(result["agendas"]):
                if not isinstance(agenda, dict):
                    raise ValueError(f"아젠다 항목 {i}가 딕셔너리가 아닙니다.")

                # 필수 필드 확인
                required_fields = ["topic", "tasks", "summary"]
                missing_fields = [field for field in required_fields if field not in agenda]
                if missing_fields:
                    raise ValueError(f"아젠다 항목 {i}에 필수 필드가 누락되었습니다: {missing_fields}")

                # tasks가 리스트인지 확인 및 정제
                if not isinstance(agenda["tasks"], list):
                    print(f"⚠️ 아젠다 {i}의 tasks가 리스트가 아님, 빈 리스트로 변경")
                    agenda["tasks"] = []

            # 비용 정보 로그 (있는 경우)
            if response.get("cost", 0) > 0:
                cost_msg = f"API 비용: ${response['cost']:.6f}"
                print(f"💰 {cost_msg}")
                self._log_to_file(f"INFO - COST: {cost_msg}")

            print("✅ JSON 파싱 및 검증 완료")
            self._log_to_file(f"SUCCESS - PARSING_COMPLETE: {len(result['agendas'])} agendas found")
            return result

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            error_msg = f"응답 파싱 오류: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"📋 원본 응답 내용 (처음 500자):\n{raw_response[:500]}")

            # 상세한 오류 로그 기록
            self._log_to_file(f"ERROR - PARSING_FAILED: {error_msg}")
            self._log_to_file(f"ERROR - RAW_RESPONSE_ON_FAILURE: {raw_response}")

            print("⚠️ 이 파일의 처리를 건너뜁니다.")
            return {
                "agendas": [{
                    "topic": "파싱 실패",
                    "tasks": [],
                    "summary": f"응답 파싱 중 오류가 발생했습니다: {str(e)}"
                }]
            }

        except Exception as unexpected_error:
            error_msg = f"예기치 못한 오류: {str(unexpected_error)}"
            print(f"❌ {error_msg}")
            self._log_to_file(f"ERROR - UNEXPECTED: {error_msg}")
            self._log_to_file(f"ERROR - RAW_RESPONSE_ON_UNEXPECTED: {raw_response}")

            print("⚠️ 이 파일의 처리를 건너뜁니다.")
            return {
                "agendas": [{
                    "topic": "예기치 못한 오류",
                    "tasks": [],
                    "summary": error_msg
                }]
            }