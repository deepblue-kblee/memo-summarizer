#!/usr/bin/env python3
"""
Claude Code CLI 클라이언트 모듈
Claude Code CLI를 통한 AI API 호출을 담당합니다.
"""

import json
import subprocess
from typing import Dict, Any


class ClaudeClient:
    """Claude Code CLI를 사용한 AI 클라이언트"""

    def __init__(self):
        self._check_claude_code_available()
        print("✅ Claude Code 클라이언트가 초기화되었습니다.")

    def _check_claude_code_available(self):
        """Claude Code CLI 사용 가능성을 확인합니다."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude Code 실행 실패: {result.stderr}")

            print(f"✅ Claude Code 연결 확인: {result.stdout.strip()}")

        except FileNotFoundError:
            raise RuntimeError("Claude Code가 설치되어 있지 않습니다. 'claude --version'을 실행해보세요.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code 응답 시간 초과")
        except Exception as e:
            raise RuntimeError(f"Claude Code 확인 실패: {e}")

    def call_claude_code(self, prompt: str) -> Dict[str, Any]:
        """Claude Code CLI를 통해 AI API 호출"""
        try:
            # Claude Code 명령어 실행
            result = subprocess.run([
                "claude",
                "--print",  # 응답 출력하고 종료
                "--output-format", "json",  # JSON 형식으로 출력
                prompt
            ],
            capture_output=True,  # stdout/stderr 캡처
            text=True,  # 문자열로 반환
            timeout=120  # 2분 타임아웃
            )

            # 실행 성공 확인
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "알 수 없는 오류"
                raise RuntimeError(f"Claude Code 실행 실패: {error_msg}")

            # JSON 파싱
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Claude Code JSON 응답 파싱 실패: {e}\n응답: {result.stdout[:200]}")

            return {
                "success": True,
                "content": response_data.get("result", ""),
                "cost": response_data.get("total_cost_usd", 0),
                "session_id": response_data.get("session_id", ""),
                "raw": response_data
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Claude Code 호출 타임아웃 (2분 초과)"}
        except Exception as e:
            return {"success": False, "error": f"Claude Code 호출 실패: {e}"}