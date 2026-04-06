#!/usr/bin/env python3
"""
Claude Code의 동작을 역추적하여 직접 구현
"""

import json
import httpx
from pathlib import Path
import os
import asyncio

def load_claude_code_settings():
    """Claude Code 설정을 로드합니다."""
    settings_path = Path.home() / ".claude" / "settings.json"

    if not settings_path.exists():
        raise FileNotFoundError(f"Claude Code 설정 파일을 찾을 수 없습니다: {settings_path}")

    with open(settings_path, 'r') as f:
        settings = json.load(f)

    return settings.get("env", {})

async def test_claude_code_method():
    """Claude Code 방식을 정확히 모방하여 API 호출"""

    try:
        print("🔧 Claude Code 설정 로드...")
        env_settings = load_claude_code_settings()

        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        print(f"📍 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🤖 Model: {model}")

        # Claude Code가 사용할 가능성이 높은 다양한 방식들 시도
        test_configurations = [
            {
                "name": "Anthropic Messages API 스타일",
                "url": f"{base_url.rstrip('/')}/v1/messages",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "claude-code/1.0"
                },
                "payload": {
                    "model": model,
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "API 연결 테스트입니다."}
                    ]
                }
            },
            {
                "name": "OpenAI Chat Completions 스타일",
                "url": f"{base_url.rstrip('/')}/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "claude-code/1.0"
                },
                "payload": {
                    "model": model,
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "API 연결 테스트입니다."}
                    ]
                }
            },
            {
                "name": "AWS 스타일 헤더",
                "url": f"{base_url.rstrip('/')}/v1/chat/completions",
                "headers": {
                    "Authorization": f"AWS4-HMAC-SHA256 {api_key}",
                    "Content-Type": "application/json",
                    "X-Amz-Target": "DynamoDB_20120810.Query",
                    "User-Agent": "claude-code/1.0"
                },
                "payload": {
                    "model": model,
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "API 연결 테스트입니다."}
                    ]
                }
            },
            {
                "name": "세션 토큰 헤더",
                "url": f"{base_url.rstrip('/')}/v1/chat/completions",
                "headers": {
                    "X-Session-Token": api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "claude-code/1.0"
                },
                "payload": {
                    "model": model,
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "API 연결 테스트입니다."}
                    ]
                }
            },
            {
                "name": "LINE 특화 헤더",
                "url": f"{base_url.rstrip('/')}/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-LINE-ChannelSecret": "claude-code",
                    "X-LINE-Signature": api_key,
                    "User-Agent": "claude-code/1.0"
                },
                "payload": {
                    "model": model,
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "API 연결 테스트입니다."}
                    ]
                }
            }
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, config in enumerate(test_configurations, 1):
                print(f"\n🧪 [{i}] {config['name']} 테스트...")
                print(f"    URL: {config['url']}")

                try:
                    response = await client.post(
                        config['url'],
                        headers=config['headers'],
                        json=config['payload']
                    )

                    print(f"    HTTP {response.status_code}")

                    if response.status_code == 200:
                        result = response.json()
                        print(f"    ✅ 성공! 응답: {result}")
                        return config, result
                    elif response.status_code == 401:
                        print(f"    ❌ 인증 실패 (401)")
                    elif response.status_code == 403:
                        print(f"    ❌ 접근 금지 (403): {response.text[:100]}")
                    elif response.status_code == 404:
                        print(f"    ❌ 엔드포인트 없음 (404)")
                    else:
                        print(f"    ❌ 기타 오류: {response.text[:100]}")

                except Exception as e:
                    print(f"    ❌ 요청 실패: {e}")

        return None, None

    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
        return None, None

def test_openai_client_with_custom_settings():
    """OpenAI 클라이언트를 Claude Code 설정으로 사용"""
    try:
        from openai import OpenAI

        print("\n🔧 OpenAI 클라이언트 + Claude Code 설정 테스트...")

        env_settings = load_claude_code_settings()
        base_url = env_settings.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = env_settings.get("AWS_SESSION_TOKEN")
        model = env_settings.get("ANTHROPIC_MODEL")

        # 다양한 OpenAI 클라이언트 설정 시도
        configurations = [
            {
                "name": "기본 설정",
                "client": OpenAI(api_key=api_key, base_url=base_url)
            },
            {
                "name": "추가 헤더",
                "client": OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    default_headers={"User-Agent": "claude-code/1.0"}
                )
            },
            {
                "name": "v1 엔드포인트",
                "client": OpenAI(
                    api_key=api_key,
                    base_url=f"{base_url.rstrip('/')}/v1"
                )
            }
        ]

        for config in configurations:
            try:
                print(f"    🧪 {config['name']} 시도...")

                response = config["client"].chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "API 연결 테스트입니다."}
                    ],
                    max_tokens=50
                )

                if response and response.choices:
                    answer = response.choices[0].message.content
                    print(f"    ✅ 성공! 응답: {answer}")
                    return config, response

            except Exception as e:
                print(f"    ❌ 실패: {e}")

        return None, None

    except ImportError:
        print("OpenAI 라이브러리가 필요합니다.")
        return None, None

async def main():
    """메인 실행 함수"""
    print("🕵️ Claude Code 동작 역추적 분석을 시작합니다...\n")

    # 1. 직접 HTTP 요청으로 다양한 방식 시도
    config, result = await test_claude_code_method()

    if config and result:
        print(f"\n🎉 성공한 설정:")
        print(f"   URL: {config['url']}")
        print(f"   헤더: {config['headers']}")
        return

    # 2. OpenAI 클라이언트 방식 시도
    config, result = test_openai_client_with_custom_settings()

    if config and result:
        print(f"\n🎉 OpenAI 클라이언트 방식으로 성공!")
        return

    print(f"\n❌ 모든 방식이 실패했습니다.")
    print(f"💡 Claude Code가 사용하는 정확한 방식을 찾지 못했습니다.")

if __name__ == "__main__":
    asyncio.run(main())