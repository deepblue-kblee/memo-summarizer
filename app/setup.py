"""Setup script for memo-summarizer package"""

from setuptools import setup, find_packages

setup(
    name="memo-summarizer",
    version="0.1.0",
    description="AI-powered memo processing and organization system",
    author="Harness Engineering",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        # Add dependencies here as needed
    ],
    entry_points={
        "console_scripts": [
            # 기존 스크립트들
            "memo-processor=memo_summarizer.cli.main_controller:main",
            "harness-linter=memo_summarizer.cli.harness_linter:main",
            "memo-analyzer=memo_summarizer.services.memo_analyzer:main",
            "daily-reporter=memo_summarizer.services.daily_reporter:main",

            # Phase 3-A Observability 스크립트들
            "observability-monitor=memo_summarizer.core.observability:main",
            "health-check=memo_summarizer.core.health_check:main",
            "log-analyzer=memo_summarizer.utils.logger:main",
        ],
    },
)