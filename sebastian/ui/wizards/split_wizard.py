"""
LY/GL Split 위저드

wireframe 스펙:
- 통합 파일 선택
- 저장 폴더 선택
- 생성될 파일 미리보기
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


class SplitWizard(QDialog):
    """LY/GL Split 위저드"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_file = ""
        self.output_folder = ""
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setWindowTitle("LY/GL Split 위저드")
        self.setMinimumSize(600, 450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # 타이틀
        title = QLabel("통합 파일을 선택하세요")
        title.setFont(QFont("Pretendard", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        # 파일 선택
        file_layout = QHBoxLayout()

        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("(파일명)")
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
        file_btn.clicked.connect(self._select_file)
        file_layout.addWidget(file_btn)

        layout.addLayout(file_layout)

        # 힌트
        hint = QLabel("예상 형식: YYMMDD_LYGL_StringALL.xlsx")
        hint.setFont(QFont("Pretendard", 11))
        hint.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(hint)

        # 저장 폴더
        folder_label = QLabel("저장 폴더")
        folder_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        folder_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(folder_label)

        folder_layout = QHBoxLayout()

        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        self.folder_input.setPlaceholderText("(경로)")
        self.folder_input.setMinimumHeight(40)
        self.folder_input.setFont(QFont("Pretendard", 12))
        self.folder_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        folder_layout.addWidget(self.folder_input)

        folder_btn = QPushButton("폴더 선택")
        folder_btn.setMinimumSize(100, 40)
        folder_btn.setFont(QFont("Pretendard", 12))
        folder_btn.setStyleSheet(f"""
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
        folder_btn.clicked.connect(self._select_folder)
        folder_layout.addWidget(folder_btn)

        layout.addLayout(folder_layout)

        # 생성될 파일 미리보기
        preview_label = QLabel("생성될 파일:")
        preview_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        preview_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(preview_label)

        preview_area = QScrollArea()
        preview_area.setWidgetResizable(True)
        preview_area.setMaximumHeight(120)
        preview_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                background-color: {BG_SECONDARY};
            }}
        """)

        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(2)
        preview_layout.setContentsMargins(8, 8, 8, 8)

        for lang in ['{YYMMDD}_EN.xlsx', '{YYMMDD}_CT.xlsx', '{YYMMDD}_CS.xlsx',
                     '{YYMMDD}_JA.xlsx', '{YYMMDD}_TH.xlsx', '{YYMMDD}_PT-BR.xlsx', '{YYMMDD}_RU.xlsx']:
            item = QLabel(lang)
            item.setFont(QFont("JetBrains Mono", 11))
            item.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 2px 4px;")
            preview_layout.addWidget(item)

        preview_widget.setLayout(preview_layout)
        preview_area.setWidget(preview_widget)
        layout.addWidget(preview_area)

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

    def _select_file(self):
        """통합 파일 선택"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "통합 파일 선택",
            "",
            "Excel Files (*.xlsx *.xlsm);;All Files (*)"
        )
        if file:
            self.input_file = file
            self.file_input.setText(Path(file).name)
            self._check_execute_enabled()

    def _select_folder(self):
        """저장 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "저장 폴더 선택",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.output_folder = folder
            self.folder_input.setText(folder)
            self._check_execute_enabled()

    def _check_execute_enabled(self):
        """실행 버튼 활성화 체크"""
        enabled = self.input_file != "" and self.output_folder != ""
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
            'input_file': self.input_file,
            'output_folder': self.output_folder
        }
