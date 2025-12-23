"""
M4GL 탭 - MIR4 현지화 도구

wireframe 스펙:
- 기능 버튼: 280 × 200
- DIALOGUE: gradient(#E8F5E9, #C8E6C9) → 선택 시 #4CAF50
- STRING: gradient(#E3F2FD, #BBDEFB) → 선택 시 #2196F3
- 실행 버튼: 160 × 48
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .common import *
from workers.m4gl_worker import M4GLWorker


class M4GLTab(QWidget):
    """M4/GL 탭"""

    # Signals
    execute_requested = pyqtSignal(str, str)  # (mode, folder_path)

    def __init__(self):
        super().__init__()
        self.selected_mode = None  # 'dialogue' or 'string'
        self.folder_path = ""
        self.worker = None
        self.progress_dialog = None
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)

        # 기능 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(24)

        # DIALOGUE 버튼
        self.dialogue_btn = QPushButton()
        self.dialogue_btn.setFixedSize(280, 200)
        self.dialogue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dialogue_btn.clicked.connect(lambda: self._select_mode('dialogue'))
        self._update_dialogue_button_style(False)

        dialogue_layout = QVBoxLayout()
        dialogue_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dialogue_title = QLabel("DIALOGUE")
        dialogue_title.setFont(QFont("Pretendard", 18, QFont.Weight.Bold))
        dialogue_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialogue_layout.addWidget(dialogue_title)

        dialogue_subtitle = QLabel("병합")
        dialogue_subtitle.setFont(QFont("Pretendard", 16))
        dialogue_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialogue_layout.addWidget(dialogue_subtitle)

        dialogue_desc1 = QLabel("대화 데이터")
        dialogue_desc1.setFont(QFont("Pretendard", 13))
        dialogue_desc1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialogue_layout.addWidget(dialogue_desc1)

        dialogue_desc2 = QLabel("3개 파일")
        dialogue_desc2.setFont(QFont("Pretendard", 13))
        dialogue_desc2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialogue_layout.addWidget(dialogue_desc2)

        self.dialogue_btn.setLayout(dialogue_layout)
        button_layout.addWidget(self.dialogue_btn)

        # STRING 버튼
        self.string_btn = QPushButton()
        self.string_btn.setFixedSize(280, 200)
        self.string_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.string_btn.clicked.connect(lambda: self._select_mode('string'))
        self._update_string_button_style(False)

        string_layout = QVBoxLayout()
        string_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        string_title = QLabel("STRING")
        string_title.setFont(QFont("Pretendard", 18, QFont.Weight.Bold))
        string_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        string_layout.addWidget(string_title)

        string_subtitle = QLabel("병합")
        string_subtitle.setFont(QFont("Pretendard", 16))
        string_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        string_layout.addWidget(string_subtitle)

        string_desc1 = QLabel("문자열 데이터")
        string_desc1.setFont(QFont("Pretendard", 13))
        string_desc1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        string_layout.addWidget(string_desc1)

        string_desc2 = QLabel("8개 파일")
        string_desc2.setFont(QFont("Pretendard", 13))
        string_desc2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        string_layout.addWidget(string_desc2)

        self.string_btn.setLayout(string_layout)
        button_layout.addWidget(self.string_btn)

        layout.addLayout(button_layout)

        # 폴더 선택 영역
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)

        folder_label = QLabel("선택한 폴더")
        folder_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        folder_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(folder_label)

        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        self.folder_input.setPlaceholderText("(경로 표시)")
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

        # 실행 버튼
        execute_layout = QHBoxLayout()
        execute_layout.addStretch()

        self.execute_btn = QPushButton("실행 (Enter)")
        self.execute_btn.setFixedSize(160, 48)
        self.execute_btn.setFont(QFont("Pretendard", 14, QFont.Weight.DemiBold))
        self.execute_btn.setEnabled(False)
        self.execute_btn.clicked.connect(self._execute)
        self._update_execute_button_style()
        execute_layout.addWidget(self.execute_btn)

        layout.addLayout(execute_layout)

        layout.addStretch()

        self.setLayout(layout)

    def _select_mode(self, mode: str):
        """모드 선택 (dialogue 또는 string)"""
        self.selected_mode = mode

        # 버튼 스타일 업데이트
        self._update_dialogue_button_style(mode == 'dialogue')
        self._update_string_button_style(mode == 'string')

        # 실행 버튼 활성화 체크
        self._check_execute_enabled()

    def _select_folder(self):
        """폴더 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "폴더 선택",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder_path = folder
            self.folder_input.setText(folder)
            self._check_execute_enabled()

    def _check_execute_enabled(self):
        """실행 버튼 활성화 체크"""
        enabled = self.selected_mode is not None and self.folder_path != ""
        self.execute_btn.setEnabled(enabled)
        self._update_execute_button_style()

    def _update_dialogue_button_style(self, selected: bool):
        """DIALOGUE 버튼 스타일 업데이트"""
        if selected:
            style = f"""
                QPushButton {{
                    background-color: {M4GL_DIALOGUE};
                    border: 2px solid {M4GL_DIALOGUE};
                    border-radius: 12px;
                    color: #FFFFFF;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #E8F5E9,
                        stop:1 #C8E6C9
                    );
                    border: 2px solid {M4GL_DIALOGUE};
                    border-radius: 12px;
                    color: {TEXT_PRIMARY};
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #C8E6C9,
                        stop:1 #A5D6A7
                    );
                }}
            """
        self.dialogue_btn.setStyleSheet(style)

    def _update_string_button_style(self, selected: bool):
        """STRING 버튼 스타일 업데이트"""
        if selected:
            style = f"""
                QPushButton {{
                    background-color: {M4GL_STRING};
                    border: 2px solid {M4GL_STRING};
                    border-radius: 12px;
                    color: #FFFFFF;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #E3F2FD,
                        stop:1 #BBDEFB
                    );
                    border: 2px solid {M4GL_STRING};
                    border-radius: 12px;
                    color: {TEXT_PRIMARY};
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #BBDEFB,
                        stop:1 #90CAF9
                    );
                }}
            """
        self.string_btn.setStyleSheet(style)

    def _update_execute_button_style(self):
        """실행 버튼 스타일 업데이트"""
        if self.execute_btn.isEnabled():
            color = M4GL_DIALOGUE if self.selected_mode == 'dialogue' else M4GL_STRING
            style = f"""
                QPushButton {{
                    background-color: {color};
                    border: none;
                    border-radius: 8px;
                    color: #FFFFFF;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    opacity: 0.9;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background-color: {BG_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    color: {TEXT_DISABLED};
                }}
            """
        self.execute_btn.setStyleSheet(style)

    def _execute(self):
        """실행"""
        if self.selected_mode and self.folder_path:
            # Worker 생성
            self.worker = M4GLWorker(self.selected_mode, self.folder_path)

            # ProgressDialog 생성
            color = M4GL_DIALOGUE if self.selected_mode == 'dialogue' else M4GL_STRING
            title = "M4/GL DIALOGUE 병합" if self.selected_mode == 'dialogue' else "M4/GL STRING 병합"
            self.progress_dialog = ProgressDialog(self, title, color)

            # Signal 연결
            self.worker.progress_updated.connect(self.progress_dialog.update_progress)
            self.worker.step_updated.connect(self.progress_dialog.update_step)
            self.worker.file_updated.connect(self.progress_dialog.update_file)
            self.worker.files_count_updated.connect(
                lambda count: self.progress_dialog.update_files(count, 3 if self.selected_mode == 'dialogue' else 8)
            )
            self.worker.completed.connect(self._on_completed)
            self.worker.error_occurred.connect(self._on_error)

            # 취소/최소화 버튼 연결
            self.progress_dialog.cancel_requested.connect(self._on_cancel)
            self.progress_dialog.minimize_requested.connect(self.progress_dialog.hide)

            # Worker 시작
            self.worker.start()
            self.progress_dialog.exec()

    def _on_completed(self, message: str):
        """작업 완료"""
        if self.progress_dialog:
            self.progress_dialog.accept()
        QMessageBox.information(self, "완료", message)
        self.execute_requested.emit(self.selected_mode, self.folder_path)

    def _on_error(self, message: str):
        """에러 발생"""
        if self.progress_dialog:
            self.progress_dialog.reject()
        QMessageBox.critical(self, "오류", message)

    def _on_cancel(self):
        """작업 취소"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        if self.progress_dialog:
            self.progress_dialog.reject()
