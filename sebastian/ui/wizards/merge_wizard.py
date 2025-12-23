"""
LY/GL Merge 위저드

wireframe 스펙:
- 크기: 600 × 500 (최소)
- 7개 언어 파일 선택
- 파일 목록: 최대 200px, scroll
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QScrollArea,
    QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path

import sys
sys.path.append('..')
from ui.common.colors import *


class MergeWizard(QDialog):
    """LY/GL Merge 위저드"""

    REQUIRED_LANGUAGES = ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files = []
        self.output_path = ""
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setWindowTitle("LY/GL Merge 위저드")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # 타이틀
        title = QLabel("7개 언어 파일을 선택하세요")
        title.setFont(QFont("Pretendard", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        # 파일 선택 영역
        file_layout = QHBoxLayout()

        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("(파일 선택)")
        self.file_input.setMinimumHeight(40)
        self.file_input.setFont(QFont("Pretendard", 12))
        self.file_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        file_layout.addWidget(self.file_input)

        file_btn = QPushButton("파일 선택")
        file_btn.setMinimumSize(100, 40)
        file_btn.setFont(QFont("Pretendard", 12))
        file_btn.setStyleSheet(f"""
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
        file_btn.clicked.connect(self._select_files)
        file_layout.addWidget(file_btn)

        layout.addLayout(file_layout)

        # 선택된 파일 목록
        list_label = QLabel(f"선택된 파일 ({len(self.selected_files)}/7):")
        list_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        list_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.list_label = list_label
        layout.addWidget(list_label)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                background-color: {BG_PRIMARY};
            }}
        """)

        self.file_list_widget = QWidget()
        self.file_list_layout = QVBoxLayout()
        self.file_list_layout.setSpacing(4)
        self.file_list_layout.setContentsMargins(8, 8, 8, 8)
        self.file_list_widget.setLayout(self.file_list_layout)
        scroll.setWidget(self.file_list_widget)

        layout.addWidget(scroll)

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
        self.execute_btn.setFont(QFont("Pretendard", 13, QFont.Weight.DemiBold))
        self.execute_btn.setEnabled(False)
        self.execute_btn.clicked.connect(self.accept)
        self._update_execute_button()
        button_layout.addWidget(self.execute_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _select_files(self):
        """파일 선택"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "언어 파일 선택 (7개)",
            "",
            "Excel Files (*.xlsx *.xlsm);;All Files (*)"
        )
        if files:
            self.selected_files = files
            self._update_file_list()
            self._check_execute_enabled()

    def _update_file_list(self):
        """파일 목록 업데이트"""
        # 기존 항목 제거
        for i in reversed(range(self.file_list_layout.count())):
            self.file_list_layout.itemAt(i).widget().setParent(None)

        # 새 항목 추가
        for file_path in self.selected_files:
            item = QLabel(f"✓ {Path(file_path).name}")
            item.setFont(QFont("Pretendard", 12))
            item.setStyleSheet(f"""
                color: {TEXT_PRIMARY};
                padding: 4px 8px;
                background-color: {SUCCESS_BG};
                border-radius: 4px;
            """)
            item.setMinimumHeight(32)
            self.file_list_layout.addWidget(item)

        self.list_label.setText(f"선택된 파일 ({len(self.selected_files)}/7):")

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
        enabled = len(self.selected_files) == 7 and self.output_path != ""
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
            'files': self.selected_files,
            'output': self.output_path
        }
