"""
메인 진입점

LY/GL 현지화 테이블 병합/분할 도구의 진입점입니다.
"""

import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import run_app


def main():
    """앱 실행"""
    try:
        run_app()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
