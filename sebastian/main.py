"""
Sebastian - 게임 현지화 도구 통합 프로그램

엔트리포인트
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui import MainWindow


def setup_logging():
    """로깅 설정"""
    # 로그 디렉토리 생성 (실행 파일 위치/logs/)
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # 로그 파일명: sebastian_YYYYMMDD.log
    log_file = log_dir / f"sebastian_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 콘솔에도 출력
        ]
    )

    logging.info("=" * 50)
    logging.info("Sebastian 시작")
    logging.info("=" * 50)


def main():
    """메인 함수"""
    setup_logging()

    app = QApplication(sys.argv)

    # 애플리케이션 설정
    app.setApplicationName("Sebastian")
    app.setOrganizationName("Sebastian")

    # 아이콘 설정 (있는 경우)
    try:
        app.setWindowIcon(QIcon("../Sebastian.ico"))
    except:
        pass

    # 전역 폰트 설정
    app.setFont(app.font())

    # 메인 창 표시
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
