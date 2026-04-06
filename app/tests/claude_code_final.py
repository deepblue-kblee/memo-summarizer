#!/usr/bin/env python3
"""
Claude Code 완전 복제 - 모든 환경변수와 설정 적용
"""

import json
import httpx
import os
from pathlib import Path
import asyncio

def load_claude_code_settings():
    """Claude Code 설정을 로드하고 환경변수로 설정합니다."""
    settings_path = Path.home() / ".claude" / "settings.json"

    if not settings_path.exists():
        raise FileNotFoundError(f"Claude Code 설정 파일을 찾을 수 없습니다: {settings_path}")

    with open(settings_path, 'r') as f:
        settings = json.load(f)

    env_settings = settings.get("env", {})

    # Claude Code가 사용하는 모든 환경변수 설정
    claude_env = {
        # 기본 Anthropic/AWS 설정
        "CLAUDE_CODE_USE_BEDROCK": env_settings.get("CLAUDE_CODE_USE_BEDROCK", "1"),
        "ANTHROPIC_MODEL": env_settings.get("ANTHROPIC_MODEL"),
        "ANTHROPIC_BEDROCK_BASE_URL": env_settings.get("ANTHROPIC_BEDROCK_BASE_URL"),
        "AWS_REGION": env_settings.get("AWS_REGION", "us-east-1"),
        "AWS_ACCESS_KEY_ID": env_settings.get("AWS_ACCESS_KEY_ID", "anything_is_fine"),
        "AWS_SECRET_ACCESS_KEY": env_settings.get("AWS_SECRET_ACCESS_KEY", "anything_is_fine"),
        "AWS_SESSION_TOKEN": env_settings.get("AWS_SESSION_TOKEN"),

        # Claude Code 특화 환경변수
        "CLAUDE_CODE_ENTRYPOINT": "cli",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": env_settings.get("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "1"),
        "CLAUDECODE": "1",
        "DISABLE_NON_ESSENTIAL_MODEL_CALLS": env_settings.get("DISABLE_NON_ESSENTIAL_MODEL_CALLS", "1"),
        "API_TIMEOUT_MS": env_settings.get("API_TIMEOUT_MS", "1800000")
    }

    # 환경변수 설정
    for key, value in claude_env.items():
        if value:
            os.environ[key] = str(value)

    return claude_env

async def test_with_claude_code_env():
    """Claude Code 환경변수를 모두 적용하여 API 호출"""

    try:
        print("🔧 Claude Code 환경 완전 복제...")

        claude_env = load_claude_code_settings()

        base_url = claude_env.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = claude_env.get("AWS_SESSION_TOKEN")
        model = claude_env.get("ANTHROPIC_MODEL")

        print(f"📍 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🤖 Model: {model}")

        # Claude Code가 사용할 가능성이 높은 특별한 헤더들
        special_headers_combinations = [
            {
                "name": "Claude Code 식별 헤더",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "claude-code/1.0",
                    "X-Claude-Code": "1",
                    "X-Bedrock-Mode": "1",
                    "X-Entrypoint": "cli"
                }
            },
            {
                "name": "AWS 시그니처 스타일",
                "headers": {
                    "Authorization": f"AWS4-HMAC-SHA256 Credential={claude_env.get('AWS_ACCESS_KEY_ID')}/{claude_env.get('AWS_REGION')}/bedrock/aws4_request",
                    "Content-Type": "application/json",
                    "X-Amz-Date": "20240211T000000Z",
                    "X-Amz-Security-Token": api_key,
                    "User-Agent": "claude-code/1.0"
                }
            },
            {
                "name": "세션 토큰 + Claude Code 헤더",
                "headers": {
                    "X-Session-Token": api_key,
                    "X-AWS-Session-Token": api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "claude-code/1.0",
                    "X-Claude-Code-Entrypoint": "cli",
                    "X-Bedrock-Use": "1"
                }
            },
            {
                "name": "LINE Proxy 특화",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "claude-code/1.0",
                    "X-Line-Proxy-Client": "claude-code",
                    "X-Client-Type": "claude-code-cli",
                    "Referer": "https://claude.ai"
                }
            }
        ]

        # 가능한 엔드포인트들
        endpoints = [
            f"{base_url.rstrip('/')}/v1/chat/completions",
            f"{base_url.rstrip('/')}/v1/messages",
            f"{base_url.rstrip('/')}/chat/completions",
            f"{base_url.rstrip('/')}/messages",
            f"{base_url.rstrip('/')}/bedrock/chat/completions",
            f"{base_url.rstrip('/')}/anthropic/v1/messages"
        ]

        payload = {
            "model": model,
            "max_tokens": 100,
            "messages": [
                {"role": "user", "content": "API 연결 테스트입니다. '연결 성공'이라고 답변해주세요."}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in endpoints:
                print(f"\n📞 엔드포인트 테스트: {endpoint}")

                for header_config in special_headers_combinations:
                    try:
                        print(f"    🧪 {header_config['name']} 시도...")

                        response = await client.post(
                            endpoint,
                            headers=header_config['headers'],
                            json=payload
                        )

                        print(f"        HTTP {response.status_code}")

                        if response.status_code == 200:
                            result = response.json()
                            print(f"        ✅ 성공!")
                            print(f"        📝 응답: {result}")
                            return {
                                "endpoint": endpoint,
                                "headers": header_config['headers'],
                                "response": result
                            }
                        elif response.status_code in [401, 403]:
                            error_msg = response.text[:100] if response.text else "오류 메시지 없음"
                            print(f"        ❌ 인증/권한 오류: {error_msg}")
                        else:
                            print(f"        ❌ 기타 오류 ({response.status_code})")

                    except Exception as e:
                        print(f"        ❌ 요청 실패: {e}")

        return None

    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def test_openai_with_full_env():
    """OpenAI 클라이언트에 모든 환경변수 적용"""
    try:
        from openai import OpenAI

        print("\n🔧 OpenAI 클라이언트 + 완전한 Claude Code 환경...")

        claude_env = load_claude_code_settings()

        base_url = claude_env.get("ANTHROPIC_BEDROCK_BASE_URL")
        api_key = claude_env.get("AWS_SESSION_TOKEN")
        model = claude_env.get("ANTHROPIC_MODEL")

        # 다양한 OpenAI 클라이언트 설정
        configurations = [
            {
                "name": "Claude Code 헤더 포함",
                "client": OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    default_headers={
                        "User-Agent": "claude-code/1.0",
                        "X-Claude-Code": "1",
                        "X-Bedrock-Mode": "1"
                    }
                )
            },
            {
                "name": "AWS 환경 변수 기반",
                "client": OpenAI(
                    api_key=api_key,
                    base_url=f"{base_url.rstrip('/')}/v1",
                    default_headers={
                        "User-Agent": "claude-code/1.0",
                        "X-AWS-Region": claude_env.get("AWS_REGION"),
                        "X-Session-Token": api_key
                    }
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
                    return config

            except Exception as e:
                print(f"    ❌ 실패: {e}")

        return None

    except ImportError:
        print("OpenAI 라이브러리가 필요합니다.")
        return None

async def main():
    """메인 실행 함수"""
    print("🕵️ Claude Code 완전 복제 분석을 시작합니다...\n")

    # 1. 직접 HTTP 요청 + 모든 환경변수
    result = await test_with_claude_code_env()

    if result:
        print(f"\n🎉 성공한 설정을 찾았습니다!")
        print(f"   엔드포인트: {result['endpoint']}")
        print(f"   헤더: {result['headers']}")
        return result

    # 2. OpenAI 클라이언트 + 환경변수
    config = test_openai_with_full_env()

    if config:
        print(f"\n🎉 OpenAI 클라이언트 방식으로 성공!")
        return config

    print(f"\n❌ 모든 시도가 실패했습니다.")
    print(f"💡 Claude Code가 사용하는 방식이 매우 특별한 것 같습니다.")

if __name__ == "__main__":
    result = asyncio.run(main())

    if result:
        print(f"\n📋 성공한 설정으로 agent.py를 수정할 수 있습니다!")
    else:
        print(f"\n🤔 Claude Code subprocess 방식이 가장 안전할 것 같습니다.")