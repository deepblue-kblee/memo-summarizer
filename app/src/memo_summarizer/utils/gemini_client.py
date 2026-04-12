#!/usr/bin/env python3
"""
Gemini CLI 클라이언트 모듈
Gemini CLI를 통한 AI API 호출을 담당합니다.
"""

import json
import subprocess
from typing import Dict, Any


class GeminiClient:
    """Gemini CLI를 사용한 AI 클라이언트"""

    def __init__(self):
        self._check_gemini_available()
        print("✅ Gemini 클라이언트가 초기화되었습니다.")

    def _check_gemini_available(self):
        """Gemini CLI 사용 가능성을 확인합니다."""
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(f"Gemini 실행 실패: {result.stderr}")

            print(f"✅ Gemini 연결 확인: {result.stdout.strip()}")

        except FileNotFoundError:
            raise RuntimeError("Gemini CLI가 설치되어 있지 않습니다. 'gemini --version'을 실행해보세요.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Gemini 응답 시간 초과")
        except Exception as e:
            raise RuntimeError(f"Gemini 확인 실패: {e}")

    def call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Gemini CLI를 통해 AI API 호출"""
        try:
            # Gemini 명령어 실행 (올바른 인자: -p, -o json)
            result = subprocess.run([
                "gemini",
                "-p", prompt,
                "-o", "json"
            ],
            capture_output=True,  # stdout/stderr 캡처
            text=True,  # 문자열로 반환
            timeout=120  # 2분 타임아웃
            )

            # 실행 성공 확인
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "알 수 없는 오류"
                raise RuntimeError(f"Gemini 실행 실패: {error_msg}")

            # JSON 파싱
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Gemini JSON 응답 파싱 실패: {e}\n응답: {result.stdout[:200]}")

            # 토큰 정보 추출 (stats -> models -> [first_model] -> tokens)
            stats = response_data.get("stats", {})
            models = stats.get("models", {})
            
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            
            if models:
                # 첫 번째 모델의 토큰 정보 사용
                first_model = list(models.values())[0]
                tokens = first_model.get("tokens", {})
                input_tokens = tokens.get("input", 0)
                output_tokens = tokens.get("candidates", 0)
                total_tokens = tokens.get("total", input_tokens + output_tokens)

            return {
                "success": True,
                "content": response_data.get("response", ""),
                "cost": response_data.get("total_cost_usd", 0),  # Gemini CLI는 직접 cost를 안 줄 수도 있음
                "session_id": response_data.get("session_id", ""),
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "raw": response_data
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Gemini 호출 타임아웃 (2분 초과)"}
        except Exception as e:
            return {"success": False, "error": f"Gemini 호출 실패: {e}"}

    # ClaudeClient와의 호환성을 위한 별칭 메서드
    def call_claude_code(self, prompt: str) -> Dict[str, Any]:
        """ClaudeClient와의 호환성을 위한 별칭 메서드"""
        return self.call_gemini(prompt)