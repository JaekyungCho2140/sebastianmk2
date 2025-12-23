"""
ProgressDialog - 진행 상황 표시 Dialog

wireframe 스펙:
- 크기: 500 x 280 (최소)
- Modal: true
- Radius: 12px
- Shadow: 0 20px 40px rgba(0,0,0,0.25)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .colors import *


class ProgressDialog(QDialog):
    """파일 처리 진행 상황 표시 Dialog"""

    # Signals
    cancel_requested = pyqtSignal()
    minimize_requested = pyqtSignal()

    def __init__(self, parent=None, title: str = "파일 처리 중", project_color: str = INFO):
        super().__init__(parent)
        self.project_color = project_color
        self._setup_ui(title)

    def _setup_ui(self, title: str):
        """UI 초기화"""
        # Dialog 설정
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 280)
        self.setMaximumSize(500, 400)

        # 레이아웃
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # 단계 라벨
        self.step_label = QLabel("단계: 1/3")
        self.step_label.setFont(QFont("Pretendard", 13))
        self.step_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(self.step_label)

        # 처리 중 파일명
        self.file_label = QLabel("처리 중: 파일명.xlsx")
        self.file_label.setFont(QFont("JetBrains Mono", 12))
        self.file_label.setStyleSheet(f"""
            background-color: {BG_SECONDARY};
            padding: 4px 8px;
            border-radius: 4px;
            color: {TEXT_PRIMARY};
        """)
        layout.addWidget(self.file_label)

        # 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setMinimumHeight(32)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border-radius: 16px;
                background-color: {BG_TERTIARY};
                text-align: center;
                font-family: "Pretendard";
                font-size: 14px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                border-radius: 16px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.project_color},
                    stop:1 {self.project_color}
                );
            }}
        """)
        layout.addWidget(self.progress_bar)

        # 정보 라벨들
        self.time_label = QLabel("남은 시간: 계산 중...")
        self.time_label.setFont(QFont("Pretendard", 12))
        self.time_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(self.time_label)

        self.files_label = QLabel("처리된 파일: 0/0")
        self.files_label.setFont(QFont("Pretendard", 12))
        self.files_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(self.files_label)

        layout.addStretch()

        # 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 취소 버튼
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setMinimumSize(80, 36)
        self.cancel_btn.setFont(QFont("Pretendard", 13))
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 24px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {BG_TERTIARY};
            }}
        """)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        button_layout.addWidget(self.cancel_btn)

        # 최소화 버튼
        self.minimize_btn = QPushButton("최소화")
        self.minimize_btn.setMinimumSize(80, 36)
        self.minimize_btn.setFont(QFont("Pretendard", 13))
        self.minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.project_color};
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                background-color: {self.project_color};
                opacity: 0.9;
            }}
        """)
        self.minimize_btn.clicked.connect(self.minimize_requested.emit)
        button_layout.addWidget(self.minimize_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Dialog 스타일
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_PRIMARY};
                border-radius: 12px;
            }}
        """)

    def update_progress(self, value: int):
        """진행률 업데이트 (0-100)"""
        self.progress_bar.setValue(value)

    def update_step(self, step: str):
        """단계 정보 업데이트"""
        self.step_label.setText(f"단계: {step}")

    def update_file(self, filename: str):
        """처리 중 파일명 업데이트"""
        self.file_label.setText(f"처리 중: {filename}")

    def update_time(self, seconds: int):
        """남은 시간 업데이트"""
        self.time_label.setText(f"남은 시간: 약 {seconds}초")

    def update_files(self, current: int, total: int):
        """처리된 파일 수 업데이트"""
        self.files_label.setText(f"처리된 파일: {current}/{total}")
