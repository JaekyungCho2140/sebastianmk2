"""
NCGL 탭 - NC 현지화 도구

wireframe 스펙:
- 입력 필드: 48px 높이
- 검증 아이콘: 48px 너비
- Focus Shadow: 0 0 0 3px rgba(0, 137, 123, 0.1)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .common import *
from workers.ncgl_worker import NCGLWorker


class NCGLTab(QWidget):
    """NC/GL 탭"""

    # Signals
    execute_requested = pyqtSignal(str, str, str)  # (folder_path, date, milestone)

    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.worker = None
        self.progress_dialog = None
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)

        # 날짜 입력
        date_label = QLabel("날짜 (YYMMDD)")
        date_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        date_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(date_label)

        date_layout = QHBoxLayout()
        date_layout.setSpacing(0)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("250512")
        self.date_input.setMaxLength(6)
        self.date_input.setMinimumHeight(48)
        self.date_input.setFont(QFont("Pretendard", 13))
        self.date_input.textChanged.connect(self._validate_date)
        self._update_input_style(self.date_input, None)
        date_layout.addWidget(self.date_input)

        self.date_icon = QLabel()
        self.date_icon.setFixedSize(48, 48)
        self.date_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_icon.setStyleSheet(f"""
            background-color: {BG_SECONDARY};
            border-left: none;
        """)
        date_layout.addWidget(self.date_icon)

        layout.addLayout(date_layout)

        date_hint = QLabel("6자리 숫자 (예: 250512)")
        date_hint.setFont(QFont("Pretendard", 11))
        date_hint.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(date_hint)

        # 마일스톤 입력
        milestone_label = QLabel("마일스톤 차수")
        milestone_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        milestone_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(milestone_label)

        milestone_layout = QHBoxLayout()
        milestone_layout.setSpacing(0)

        self.milestone_input = QLineEdit()
        self.milestone_input.setPlaceholderText("15")
        self.milestone_input.setMaxLength(3)
        self.milestone_input.setMinimumHeight(48)
        self.milestone_input.setFont(QFont("Pretendard", 13))
        self.milestone_input.textChanged.connect(self._validate_milestone)
        self._update_input_style(self.milestone_input, None)
        milestone_layout.addWidget(self.milestone_input)

        self.milestone_icon = QLabel()
        self.milestone_icon.setFixedSize(48, 48)
        self.milestone_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.milestone_icon.setStyleSheet(f"""
            background-color: {BG_SECONDARY};
            border-left: none;
        """)
        milestone_layout.addWidget(self.milestone_icon)

        layout.addLayout(milestone_layout)

        milestone_hint = QLabel("1-3자리 숫자 (예: 15 → M15)")
        milestone_hint.setFont(QFont("Pretendard", 11))
        milestone_hint.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(milestone_hint)

        # 폴더 선택
        folder_label = QLabel("선택한 폴더")
        folder_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        folder_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(folder_label)

        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)

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
        # 스타일은 QSS에서 자동 적용
        execute_layout.addWidget(self.execute_btn)

        layout.addLayout(execute_layout)

        layout.addStretch()

        self.setLayout(layout)

    def _validate_date(self, text: str):
        """날짜 검증 (6자리 숫자)"""
        is_valid = text.isdigit() and len(text) == 6
        self._update_validation_icon(self.date_icon, is_valid)
        self._update_input_style(self.date_input, is_valid if text else None)
        self._check_execute_enabled()

    def _validate_milestone(self, text: str):
        """마일스톤 검증 (1-3자리 숫자)"""
        is_valid = text.isdigit() and 1 <= len(text) <= 3
        self._update_validation_icon(self.milestone_icon, is_valid)
        self._update_input_style(self.milestone_input, is_valid if text else None)
        self._check_execute_enabled()

    def _update_validation_icon(self, icon_label: QLabel, is_valid: bool):
        """검증 아이콘 업데이트"""
        if is_valid:
            icon_label.setText("✓")
            icon_label.setStyleSheet(f"""
                background-color: {BG_SECONDARY};
                color: {SUCCESS};
                font-size: 24px;
            """)
        else:
            icon_label.setText("✗")
            icon_label.setStyleSheet(f"""
                background-color: {BG_SECONDARY};
                color: {ERROR};
                font-size: 24px;
            """)

    def _update_input_style(self, input_field: QLineEdit, is_valid: bool | None):
        """입력 필드 스타일 업데이트 - v2 미니멀 디자인"""
        if is_valid is None:
            # 입력 전 - 기본 스타일 (QSS 적용)
            input_field.setObjectName("")
        elif is_valid:
            # 유효 - validInput 스타일
            input_field.setObjectName("validInput")
        else:
            # 무효 - invalidInput 스타일
            input_field.setObjectName("invalidInput")

        # 스타일 다시 적용
        input_field.style().unpolish(input_field)
        input_field.style().polish(input_field)

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
        date_valid = self.date_input.text().isdigit() and len(self.date_input.text()) == 6
        milestone_valid = self.milestone_input.text().isdigit() and 1 <= len(self.milestone_input.text()) <= 3
        folder_valid = self.folder_path != ""

        enabled = date_valid and milestone_valid and folder_valid
        self.execute_btn.setEnabled(enabled)
        # 스타일은 QSS에서 자동 처리됨 (enabled/disabled 상태)



    def _execute(self):
        """실행"""
        date = self.date_input.text()
        milestone = self.milestone_input.text()
        if date and milestone and self.folder_path:
            # Worker 생성
            self.worker = NCGLWorker(self.folder_path, date, milestone)

            # ProgressDialog 생성
            self.progress_dialog = ProgressDialog(self, "NC/GL 병합", NCGL)

            # Signal 연결
            self.worker.progress_updated.connect(self.progress_dialog.update_progress)
            self.worker.step_updated.connect(self.progress_dialog.update_step)
            self.worker.file_updated.connect(self.progress_dialog.update_file)
            self.worker.files_count_updated.connect(
                lambda count: self.progress_dialog.update_files(count, 8)
            )
            self.worker.time_updated.connect(self.progress_dialog.update_time)
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
        date = self.date_input.text()
        milestone = self.milestone_input.text()
        self.execute_requested.emit(self.folder_path, date, milestone)

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
