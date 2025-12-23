"""
LY/GL Diff 위저드

wireframe 스펙:
- 비교1 (이전 버전) 폴더
- 비교2 (현재 버전) 폴더
- 저장 위치
- 생성 파일: YYYYMMDDHHMMSS_DIFF.xlsx
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import sys
sys.path.append('..')
from ui.common.colors import *


class DiffWizard(QDialog):
    """LY/GL Diff 위저드"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder1 = ""
        self.folder2 = ""
        self.output_path = ""
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setWindowTitle("LY/GL Legacy Diff 위저드")
        self.setMinimumSize(600, 450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # 비교1 (이전 버전)
        compare1_label = QLabel("비교1 (이전 버전)")
        compare1_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        compare1_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(compare1_label)

        folder1_layout = QHBoxLayout()

        self.folder1_input = QLineEdit()
        self.folder1_input.setReadOnly(True)
        self.folder1_input.setPlaceholderText("(폴더 경로)")
        self.folder1_input.setMinimumHeight(40)
        self.folder1_input.setFont(QFont("Pretendard", 12))
        self.folder1_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        folder1_layout.addWidget(self.folder1_input)

        folder1_btn = QPushButton("폴더 선택")
        folder1_btn.setMinimumSize(100, 40)
        folder1_btn.setFont(QFont("Pretendard", 12))
        folder1_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {BG_TERTIARY};
            }}
        """)
        folder1_btn.clicked.connect(self._select_folder1)
        folder1_layout.addWidget(folder1_btn)

        layout.addLayout(folder1_layout)

        # 힌트
        hint1 = QLabel("예: 251128_EN.xlsx ~ 251128_RU.xlsx")
        hint1.setFont(QFont("Pretendard", 11))
        hint1.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(hint1)

        # 비교2 (현재 버전)
        compare2_label = QLabel("비교2 (현재 버전)")
        compare2_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        compare2_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(compare2_label)

        folder2_layout = QHBoxLayout()

        self.folder2_input = QLineEdit()
        self.folder2_input.setReadOnly(True)
        self.folder2_input.setPlaceholderText("(폴더 경로)")
        self.folder2_input.setMinimumHeight(40)
        self.folder2_input.setFont(QFont("Pretendard", 12))
        self.folder2_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        folder2_layout.addWidget(self.folder2_input)

        folder2_btn = QPushButton("폴더 선택")
        folder2_btn.setMinimumSize(100, 40)
        folder2_btn.setFont(QFont("Pretendard", 12))
        folder2_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {BG_TERTIARY};
            }}
        """)
        folder2_btn.clicked.connect(self._select_folder2)
        folder2_layout.addWidget(folder2_btn)

        layout.addLayout(folder2_layout)

        # 힌트
        hint2 = QLabel("예: 251210_EN.xlsx ~ 251210_RU.xlsx")
        hint2.setFont(QFont("Pretendard", 11))
        hint2.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(hint2)

        # 저장 위치
        save_label = QLabel("저장 위치")
        save_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        save_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(save_label)

        save_layout = QHBoxLayout()

        self.save_input = QLineEdit()
        self.save_input.setReadOnly(True)
        self.save_input.setPlaceholderText("(경로)")
        self.save_input.setMinimumHeight(40)
        self.save_input.setFont(QFont("Pretendard", 12))
        self.save_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        save_layout.addWidget(self.save_input)

        save_btn = QPushButton("선택")
        save_btn.setMinimumSize(80, 40)
        save_btn.setFont(QFont("Pretendard", 12))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {BG_TERTIARY};
            }}
        """)
        save_btn.clicked.connect(self._select_output)
        save_layout.addWidget(save_btn)

        layout.addLayout(save_layout)

        # 생성 파일명 힌트
        file_hint = QLabel("생성 파일: YYYYMMDDHHMMSS_DIFF.xlsx")
        file_hint.setFont(QFont("JetBrains Mono", 11))
        file_hint.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(file_hint)

        layout.addStretch()

        # 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("취소")
        cancel_btn.setMinimumSize(80, 40)
        cancel_btn.setFont(QFont("Pretendard", 13))
        cancel_btn.setStyleSheet(f"""
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
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.execute_btn = QPushButton("실행 →")
        self.execute_btn.setMinimumSize(100, 40)
        self.execute_btn.setFont(QFont("Pretendart", 13, QFont.Weight.DemiBold))
        self.execute_btn.setEnabled(False)
        self.execute_btn.clicked.connect(self.accept)
        self._update_execute_button()
        button_layout.addWidget(self.execute_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _select_folder1(self):
        """비교1 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "비교1 폴더 선택 (이전 버전)",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder1 = folder
            self.folder1_input.setText(folder)
            self._check_execute_enabled()

    def _select_folder2(self):
        """비교2 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "비교2 폴더 선택 (현재 버전)",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder2 = folder
            self.folder2_input.setText(folder)
            self._check_execute_enabled()

    def _select_output(self):
        """저장 위치 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "저장 위치 선택",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.output_path = folder
            self.save_input.setText(folder)
            self._check_execute_enabled()

    def _check_execute_enabled(self):
        """실행 버튼 활성화 체크"""
        enabled = self.folder1 != "" and self.folder2 != "" and self.output_path != ""
        self.execute_btn.setEnabled(enabled)
        self._update_execute_button()

    def _update_execute_button(self):
        """실행 버튼 스타일 업데이트"""
        if self.execute_btn.isEnabled():
            style = f"""
                QPushButton {{
                    background-color: {LYGL};
                    border: none;
                    border-radius: 8px;
                    padding: 0 24px;
                    color: #FFFFFF;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background-color: {BG_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    padding: 0 24px;
                    color: {TEXT_DISABLED};
                }}
            """
        self.execute_btn.setStyleSheet(style)

    def get_data(self):
        """선택된 데이터 반환"""
        return {
            'folder1': self.folder1,
            'folder2': self.folder2,
            'output': self.output_path
        }
