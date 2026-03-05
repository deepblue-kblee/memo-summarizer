#!/usr/bin/env python3
"""
Claude Code 기반 API 호출 예시
"""

import subprocess
import json
from typing import Dict, Any

def call_claude_code(prompt: str) -> Dict[str, Any]:
    """Claude Code CLI를 통해 API 호출"""
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
        timeout=60  # 60초 타임아웃
        )

        # 실행 성공 확인
        if result.returncode != 0:
            raise RuntimeError(f"Claude Code 실행 실패: {result.stderr}")

        # JSON 파싱
        response_data = json.loads(result.stdout)

        return {
            "success": True,
            "content": response_data.get("result", ""),
            "cost": response_data.get("total_cost_usd", 0),
            "session_id": response_data.get("session_id", ""),
            "raw": response_data
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Claude Code 호출 타임아웃"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON 파싱 실패: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Claude Code 호출 실패: {e}"}

def analyze_memo_with_claude_code(memo_content: str) -> Dict[str, Any]:
    """Claude Code를 사용하여 메모 분석"""
    prompt = f"""
다음 메모 내용을 분석하여 주제, 할 일 목록, 요약을 추출해주세요.

메모 내용:
{memo_content}

다음 JSON 형식으로 정확히 응답해주세요:
{{
    "topic": "메모의 주요 주제 (간결하게)",
    "tasks": ["할일1", "할일2", "할일3"],
    "summary": "메모의 핵심 내용 요약 (2-3 문장)"
}}

규칙:
1. topic은 메모의 핵심 주제를 간결하게 표현
2. tasks는 메모에서 추출할 수 있는 구체적인 행동 항목들의 배열
3. summary는 메모의 핵심 내용을 2-3 문장으로 요약
4. 반드시 유효한 JSON 형식으로만 응답
"""

    # Claude Code 호출
    response = call_claude_code(prompt)

    if not response["success"]:
        return {
            "topic": "분석 실패",
            "tasks": [],
            "summary": f"분석 오류: {response['error']}"
        }

    try:
        # AI 응답에서 JSON 추출
        content = response["content"]

        # JSON 블록 찾기
        if "```json" in content:
            start_idx = content.find("```json") + 7
            end_idx = content.find("```", start_idx)
            if end_idx > start_idx:
                content = content[start_idx:end_idx].strip()

        # JSON 파싱
        result = json.loads(content)

        # 필수 필드 검증
        if not all(key in result for key in ["topic", "tasks", "summary"]):
            raise ValueError("필수 필드가 누락되었습니다.")

        return result

    except (json.JSONDecodeError, ValueError) as e:
        return {
            "topic": "파싱 실패",
            "tasks": [],
            "summary": f"응답 파싱 오류: {e}"
        }

# 테스트 실행
if __name__ == "__main__":
    test_memo = """
# 프로젝트 아이디어

## 블로그 자동화 도구
- 마크다운을 여러 플랫폼에 자동 발행
- SEO 최적화 자동 적용
- 우선순위: 높음
- 예상 기간: 2주
"""

    print("🧪 Claude Code 기반 메모 분석 테스트...")

    result = analyze_memo_with_claude_code(test_memo)

    print(f"🏷️  주제: {result['topic']}")
    print(f"📝 할 일: {result['tasks']}")
    print(f"📄 요약: {result['summary']}")