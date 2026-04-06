#!/usr/bin/env python3
"""
Claude Code 설정을 사용한 API 연결 테스트
"""

import json
import os
from pathlib import Path
from openai import OpenAI

def load_claude_code_settings():
    """Claude Code 설정을 로드합니다."""
    settings_path = Path.home() / ".claude" / "settings.json"

    if not settings_path.exists():
        raise FileNotFoundError(f"Claude Code 설정 파일을 찾을 수 없습니다: {settings_path}")

    with open(settings_path, 'r') as f:
        settings = json.load(f)

    return settings.get("env", {})

def test_api_connection():
    """API 연결을 테스트합니다."""
    try:
        print("🔧 Claude Code 설정을 로드하는 중...")

        # 설정 로드
        env_settings = load_claude_code_settings()

        # 필요한 설정값 추출
        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        print(f"📍 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🤖 Model: {model}")

        if not all([base_url, api_key, model]):
            print("❌ 필수 설정값이 누락되었습니다.")
            return False

        # OpenAI 클라이언트 생성
        print("\n🚀 API 클라이언트 초기화 중...")
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        # 테스트 요청
        print("📞 API 호출 테스트 중...")

        test_message = "안녕하세요! API 연결 테스트입니다. 간단히 '연결 성공'이라고 답변해주세요."

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": test_message}
            ],
            max_tokens=50,
            temperature=0.1
        )

        # 응답 확인
        if response and response.choices:
            answer = response.choices[0].message.content
            print(f"✅ API 호출 성공!")
            print(f"📝 응답: {answer}")
            return True
        else:
            print("❌ API 응답이 비어있습니다.")
            return False

    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        print(f"오류 타입: {type(e).__name__}")
        return False

def test_memo_analysis():
    """실제 메모 분석 테스트를 수행합니다."""
    try:
        print("\n🧪 메모 분석 테스트를 시작합니다...")

        # 설정 로드
        env_settings = load_claude_code_settings()
        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        # 클라이언트 생성
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        # 테스트 메모 내용
        test_memo = """
# 프로젝트 아이디어

## 블로그 자동화 도구

- 마크다운으로 작성된 글을 여러 플랫폼에 자동 발행
- 지원 플랫폼: 네이버 블로그, 티스토리, 벨로그, 미디엄
- SEO 최적화 자동 적용
- 우선순위: 중간
- 예상 소요시간: 2주

## 추가 기능
- 예약 발행 기능
- 소셜미디어 연동
"""

        prompt = f"""
다음 메모 내용을 분석하여 주제, 할 일 목록, 요약을 추출해주세요.

메모 내용:
{test_memo}

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

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )

        if response and response.choices:
            answer = response.choices[0].message.content
            print(f"📝 분석 결과:")
            print(answer)

            # JSON 파싱 테스트
            try:
                # JSON 블록 추출
                response_text = answer.strip()
                if "```json" in response_text:
                    start_idx = response_text.find("```json") + 7
                    end_idx = response_text.find("```", start_idx)
                    if end_idx > start_idx:
                        response_text = response_text[start_idx:end_idx].strip()

                result = json.loads(response_text)
                print(f"\n✅ JSON 파싱 성공:")
                print(f"   🏷️  주제: {result.get('topic')}")
                print(f"   📝 할 일: {len(result.get('tasks', []))}개")
                print(f"   📄 요약: {result.get('summary')}")

                return True

            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                return False
        else:
            print("❌ 분석 응답이 비어있습니다.")
            return False

    except Exception as e:
        print(f"❌ 메모 분석 테스트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🧪 Claude Code API 연결 테스트를 시작합니다...\n")

    # 기본 연결 테스트
    if not test_api_connection():
        print("\n❌ 기본 API 연결에 실패했습니다.")
        return 1

    # 메모 분석 테스트
    if not test_memo_analysis():
        print("\n❌ 메모 분석 테스트에 실패했습니다.")
        return 1

    print(f"\n🎉 모든 테스트가 성공했습니다!")
    print(f"agent.py를 Claude Code 설정으로 수정할 준비가 완료되었습니다.")
    return 0

if __name__ == "__main__":
    exit(main())