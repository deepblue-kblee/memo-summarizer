#!/usr/bin/env python3
"""
Claude Code 설정을 사용한 API 연결 테스트 (Anthropic 라이브러리 방식)
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic

def load_claude_code_settings():
    """Claude Code 설정을 로드합니다."""
    settings_path = Path.home() / ".claude" / "settings.json"

    if not settings_path.exists():
        raise FileNotFoundError(f"Claude Code 설정 파일을 찾을 수 없습니다: {settings_path}")

    with open(settings_path, 'r') as f:
        settings = json.load(f)

    return settings.get("env", {})

def test_anthropic_with_custom_base():
    """Anthropic 라이브러리에 커스텀 base_url 사용"""
    try:
        print("🔧 Anthropic 라이브러리 + 커스텀 base_url 테스트...")

        # 설정 로드
        env_settings = load_claude_code_settings()
        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        print(f"📍 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🤖 Model: {model}")

        # Anthropic 클라이언트 생성 (커스텀 base_url)
        client = Anthropic(
            api_key=api_key,
            base_url=base_url
        )

        # 테스트 요청
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "API 연결 테스트입니다. '연결 성공'이라고 답변해주세요."}
            ]
        )

        if response and response.content:
            answer = response.content[0].text
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

def test_direct_http_request():
    """직접 HTTP 요청으로 테스트"""
    try:
        import httpx

        print("\n🔧 직접 HTTP 요청 테스트...")

        # 설정 로드
        env_settings = load_claude_code_settings()
        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        # URL 생성 (여러 가능한 엔드포인트 시도)
        possible_endpoints = [
            f"{base_url.rstrip('/')}/v1/messages",
            f"{base_url.rstrip('/')}/v1/chat/completions",
            f"{base_url.rstrip('/')}/messages",
            f"{base_url.rstrip('/')}/chat/completions"
        ]

        for endpoint in possible_endpoints:
            print(f"📞 시도 중: {endpoint}")

            # Anthropic API 형태 요청
            anthropic_payload = {
                "model": model,
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": "API 연결 테스트입니다."}
                ]
            }

            # OpenAI API 형태 요청
            openai_payload = {
                "model": model,
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": "API 연결 테스트입니다."}
                ]
            }

            for payload_type, payload in [("Anthropic", anthropic_payload), ("OpenAI", openai_payload)]:
                try:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"  # Anthropic API 버전
                    }

                    with httpx.Client(timeout=30.0) as client:
                        response = client.post(
                            endpoint,
                            headers=headers,
                            json=payload
                        )

                        print(f"   {payload_type} 형태: HTTP {response.status_code}")

                        if response.status_code == 200:
                            result = response.json()
                            print(f"   ✅ 성공! 응답: {result}")
                            return True
                        else:
                            print(f"   응답: {response.text[:200]}")

                except Exception as e:
                    print(f"   ❌ {payload_type} 형태 실패: {e}")

        return False

    except Exception as e:
        print(f"❌ HTTP 요청 테스트 실패: {e}")
        return False

def test_with_different_auth():
    """다른 인증 헤더 방식으로 테스트"""
    try:
        import httpx

        print("\n🔧 다양한 인증 방식 테스트...")

        # 설정 로드
        env_settings = load_claude_code_settings()
        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        endpoint = f"{base_url.rstrip('/')}/v1/chat/completions"

        # 다양한 헤더 방식 시도
        auth_methods = [
            {"Authorization": f"Bearer {api_key}"},
            {"x-api-key": api_key},
            {"api-key": api_key},
            {"x-auth-token": api_key},
            {"session-token": api_key},
        ]

        payload = {
            "model": model,
            "max_tokens": 50,
            "messages": [
                {"role": "user", "content": "테스트"}
            ]
        }

        for i, auth_header in enumerate(auth_methods, 1):
            try:
                print(f"📞 [{i}] 인증 방식 테스트: {list(auth_header.keys())[0]}")

                headers = {
                    **auth_header,
                    "Content-Type": "application/json"
                }

                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        endpoint,
                        headers=headers,
                        json=payload
                    )

                    print(f"   HTTP {response.status_code}")

                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ 성공! {list(auth_header.keys())[0]} 방식 작동")
                        return True, auth_header
                    else:
                        error_text = response.text[:200] if response.text else "응답 없음"
                        print(f"   응답: {error_text}")

            except Exception as e:
                print(f"   ❌ 실패: {e}")

        return False, None

    except Exception as e:
        print(f"❌ 인증 방식 테스트 실패: {e}")
        return False, None

def main():
    """메인 실행 함수"""
    print("🧪 Claude Code API 연결 테스트 (v2)를 시작합니다...\n")

    # 1. Anthropic 라이브러리 + 커스텀 base_url
    if test_anthropic_with_custom_base():
        print("\n🎉 Anthropic 라이브러리 방식으로 성공!")
        return 0

    # 2. 직접 HTTP 요청
    if test_direct_http_request():
        print("\n🎉 직접 HTTP 요청 방식으로 성공!")
        return 0

    # 3. 다른 인증 방식들
    success, auth_method = test_with_different_auth()
    if success:
        print(f"\n🎉 다른 인증 방식으로 성공! 사용된 헤더: {auth_method}")
        return 0

    print(f"\n❌ 모든 테스트가 실패했습니다.")
    print(f"💡 다른 방법을 시도해보거나 설정을 다시 확인해주세요.")
    return 1

if __name__ == "__main__":
    exit(main())