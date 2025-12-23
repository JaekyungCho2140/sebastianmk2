"""
Sebastian - 게임 현지화 도구 통합 프로그램

엔트리포인트
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui import MainWindow


def main():
    """메인 함수"""
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
