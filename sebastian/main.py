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
    from logging.handlers import TimedRotatingFileHandler
    
    # 로그 디렉토리 생성 (실행 파일 위치/logs/)
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # 로그 파일명: sebastian.log (로테이션 시 sebastian.log.YYYYMM)
    log_file = log_dir / "sebastian.log"

    # 월 단위 로테이션: 매월 1일 자정, 무제한 보관
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',      # 자정마다 체크
        interval=1,           # 1일 간격
        backupCount=0,        # 무제한 보관 (삭제 안 함)
        encoding='utf-8'
    )
    
    # 월 단위 로테이션을 위한 커스텀 설정
    # suffix를 YYYYMM 형식으로 설정
    file_handler.suffix = "%Y%m"
    
    # 월이 바뀔 때만 로테이션되도록 필터 함수 추가
    original_shouldRollover = file_handler.shouldRollover
    
    def monthly_rollover(record):
        """월이 바뀌었을 때만 로테이션"""
        if not hasattr(file_handler, '_last_month'):
            file_handler._last_month = datetime.now().month
        
        current_month = datetime.now().month
        if current_month != file_handler._last_month:
            file_handler._last_month = current_month
            return True
        return False
    
    file_handler.shouldRollover = monthly_rollover

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            file_handler,
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
