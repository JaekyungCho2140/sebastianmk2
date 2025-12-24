"""
Status Check 위저드

7개 언어 파일을 복수 선택하고 자동으로 언어를 인식합니다.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path

import sys
sys.path.append('..')
from ui.common.colors import *


class StatusCheckWizard(QDialog):
    """Status Check 위저드 - 복수 파일 선택 + 자동 언어 인식"""

    REQUIRED_LANGUAGES = ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files = []
        self.output_path = ""
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setWindowTitle("Status Check - 언어 파일 선택")
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
        title = QLabel("Status Check - 언어 파일 선택")
        title.setFont(QFont("Pretendard", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        # 설명
        desc = QLabel("7개 언어 파일을 선택하세요.\n파일명에서 언어 코드를 자동으로 인식합니다. (예: 251201_EN.xlsx)")
        desc.setFont(QFont("맑은 고딕", 11))
        desc.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(desc)

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
                background-color: #FAFAFA;
            }}
        """)

        scroll_widget = QWidget()
        self.file_list_layout = QVBoxLayout()
        self.file_list_layout.setSpacing(4)
        self.file_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_widget.setLayout(self.file_list_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 출력 파일 선택
        output_label = QLabel("출력 파일:")
        output_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        output_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(output_label)

        output_layout = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        self.output_input.setPlaceholderText("(출력 파일 경로)")
        self.output_input.setMinimumHeight(40)
        self.output_input.setFont(QFont("맑은 고딕", 11))
        self.output_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        output_layout.addWidget(self.output_input)

        output_btn = QPushButton("폴더 선택")
        output_btn.setMinimumSize(100, 40)
        output_btn.setFont(QFont("Pretendard", 11))
        output_btn.setStyleSheet(f"""
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
        output_btn.clicked.connect(self._select_output)
        output_layout.addWidget(output_btn)

        layout.addLayout(output_layout)

        # 간격
        layout.addStretch()

        # 버튼 영역
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("취소")
        cancel_btn.setMinimumSize(100, 40)
        cancel_btn.setFont(QFont("Pretendard", 11))
        cancel_btn.setStyleSheet(f"""
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
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        start_btn = QPushButton("실행 →")
        start_btn.setMinimumSize(100, 40)
        start_btn.setFont(QFont("Pretendard", 11, QFont.Weight.Bold))
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LYGL};
                border: none;
                border-radius: 4px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #9C27B0;
            }}
        """)
        start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(start_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _select_files(self):
        """복수 파일 선택"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "언어 파일 선택 (7개)",
            "",
            "Excel Files (*.xlsx *.xlsm);;All Files (*)"
        )
        if files:
            self.selected_files = files
            self._update_file_list()

    def _update_file_list(self):
        """파일 목록 업데이트"""
        # 기존 항목 제거
        for i in reversed(range(self.file_list_layout.count())):
            widget = self.file_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

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
        """출력 파일 선택"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "출력 파일 선택",
            "",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            # .xlsx 확장자 자동 추가
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            self.output_path = file_path
            self.output_input.setText(file_path)

    def _on_start(self):
        """Start 버튼 클릭"""
        # 1. 7개 파일이 모두 선택되었는지 확인
        if len(self.selected_files) != 7:
            QMessageBox.warning(
                self,
                "파일 선택 필요",
                f"7개 언어 파일을 모두 선택해주세요.\n현재: {len(self.selected_files)}개"
            )
            return

        # 2. 출력 파일이 지정되었는지 확인
        if not self.output_path:
            QMessageBox.warning(
                self,
                "출력 파일 필요",
                "출력 파일 경로를 지정해주세요."
            )
            return

        # 3. 모든 파일이 존재하는지 확인
        for file_path in self.selected_files:
            if not Path(file_path).exists():
                QMessageBox.critical(
                    self,
                    "파일 없음",
                    f"파일을 찾을 수 없습니다:\n{file_path}"
                )
                return

        # 4. 완료
        self.accept()

    def get_data(self) -> dict:
        """
        선택된 파일 정보 반환

        Returns:
            {
                'files': [Path, Path, ...],  # 7개 파일 리스트
                'output': Path
            }
        """
        return {
            'files': self.selected_files,
            'output': Path(self.output_path)
        }
