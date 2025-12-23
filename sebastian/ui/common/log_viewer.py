"""
LogViewer - 로그 표시 위젯

wireframe 스펙:
- 접힘: 32px (헤더만)
- 펼침: 200px (헤더 32 + 탭 32 + 콘텐츠 136)
- 애니메이션: 0.3s ease-in-out
- 최대 줄 수: 1000줄
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from .colors import *


class LogViewer(QWidget):
    """로그 표시 위젯 (접기/펼치기 가능)"""

    MAX_LINES = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더 (32px)
        header_widget = QWidget()
        header_widget.setFixedHeight(32)
        header_widget.setStyleSheet(f"background-color: {BG_SECONDARY};")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 0, 16, 0)

        # 접기/펼치기 버튼
        self.toggle_btn = QPushButton("▼ 로그")
        self.toggle_btn.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        self.toggle_btn.setFlat(True)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: {TEXT_PRIMARY};
                text-align: left;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {INFO};
            }}
        """)
        self.toggle_btn.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.toggle_btn)

        header_layout.addStretch()

        # 지우기 버튼
        clear_btn = QPushButton("지우기")
        clear_btn.setFont(QFont("Pretendard", 11))
        clear_btn.setFlat(True)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: {TEXT_SECONDARY};
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
            }}
        """)
        clear_btn.clicked.connect(self.clear_all)
        header_layout.addWidget(clear_btn)

        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)

        # 콘텐츠 영역 (탭 + 로그)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 탭 위젯 (32px)
        self.tab_widget = QTabWidget()
        self.tab_widget.setFixedHeight(168)  # 탭바 32 + 콘텐츠 136
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {BG_PRIMARY};
            }}
            QTabBar::tab {{
                background-color: {BG_SECONDARY};
                color: {TEXT_SECONDARY};
                padding: 8px 16px;
                border: none;
                font-family: "Pretendard";
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background-color: {BG_PRIMARY};
                color: {TEXT_PRIMARY};
            }}
            QTabBar::tab:hover {{
                background-color: {BG_TERTIARY};
            }}
        """)

        # 로그 탭
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(self.MAX_LINES)
        self.log_text.setFont(QFont("JetBrains Mono", 11))
        self.log_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #FAFAFA;
                border: none;
                color: {TEXT_PRIMARY};
                padding: 8px;
            }}
        """)
        self.tab_widget.addTab(self.log_text, "로그")

        # 에러 탭
        self.error_text = QPlainTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setMaximumBlockCount(self.MAX_LINES)
        self.error_text.setFont(QFont("JetBrains Mono", 11))
        self.error_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {ERROR_BG};
                border: none;
                color: {TEXT_PRIMARY};
                padding: 8px;
            }}
        """)
        self.tab_widget.addTab(self.error_text, "에러")

        # 경고 탭
        self.warning_text = QPlainTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setMaximumBlockCount(self.MAX_LINES)
        self.warning_text.setFont(QFont("JetBrains Mono", 11))
        self.warning_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {WARNING_BG};
                border: none;
                color: {TEXT_PRIMARY};
                padding: 8px;
            }}
        """)
        self.tab_widget.addTab(self.warning_text, "경고")

        content_layout.addWidget(self.tab_widget)
        self.content_widget.setLayout(content_layout)
        layout.addWidget(self.content_widget)

        self.setLayout(layout)

        # 초기 높이 설정
        self.setFixedHeight(200)  # 펼쳐진 상태

    def toggle_expanded(self):
        """접기/펼치기 토글"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def collapse(self):
        """접기"""
        self.is_expanded = False
        self.toggle_btn.setText("▶ 로그")
        self.content_widget.hide()
        self.setFixedHeight(32)

    def expand(self):
        """펼치기"""
        self.is_expanded = True
        self.toggle_btn.setText("▼ 로그")
        self.content_widget.show()
        self.setFixedHeight(200)

    def add_log(self, message: str):
        """로그 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")

    def add_error(self, message: str):
        """에러 추가 (에러 탭으로 자동 전환)"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.error_text.appendPlainText(f"[{timestamp}] ❌ {message}")
        self.tab_widget.setCurrentIndex(1)  # 에러 탭으로 전환

    def add_warning(self, message: str):
        """경고 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.warning_text.appendPlainText(f"[{timestamp}] ⚠️ {message}")

    def clear_all(self):
        """모든 로그 지우기"""
        self.log_text.clear()
        self.error_text.clear()
        self.warning_text.clear()
