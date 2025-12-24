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
        """UI 초기화 - v2 미니멀 카드 디자인"""
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)

        # 기능 카드 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(48)

        # DIALOGUE 카드
        self.dialogue_btn = self._create_card_button(
            "DIALOGUE",
            "병합",
            "대화 데이터",
            "3개 파일"
        )
        self.dialogue_btn.clicked.connect(lambda: self._select_mode('dialogue'))
        button_layout.addWidget(self.dialogue_btn)

        # STRING 카드
        self.string_btn = self._create_card_button(
            "STRING",
            "병합",
            "문자열 데이터",
            "8개 파일"
        )
        self.string_btn.clicked.connect(lambda: self._select_mode('string'))
        button_layout.addWidget(self.string_btn)

        layout.addLayout(button_layout)

        # 폴더 선택 영역
        folder_label = QLabel("폴더 선택")
        folder_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        layout.addWidget(folder_label)

        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)

        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        self.folder_input.setPlaceholderText("(경로 표시)")
        self.folder_input.setFont(QFont("Pretendard", 12))
        folder_layout.addWidget(self.folder_input)

        folder_btn = QPushButton("📁 폴더 선택")
        folder_btn.setObjectName("secondaryButton")
        folder_btn.setMinimumSize(120, 40)
        folder_btn.setFont(QFont("Pretendard", 12))
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
        execute_layout.addWidget(self.execute_btn)

        layout.addLayout(execute_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _create_card_button(self, title: str, subtitle: str, desc1: str, desc2: str) -> QPushButton:
        """카드 스타일 버튼 생성 (v2 미니멀 디자인)
        
        Args:
            title: 제목 (예: "DIALOGUE")
            subtitle: 부제목 (예: "병합")
            desc1: 설명 1 (예: "대화 데이터")
            desc2: 설명 2 (예: "3개 파일")
        
        Returns:
            QPushButton: 카드 스타일 버튼
        """
        btn = QPushButton()
        btn.setObjectName("cardButton")
        btn.setFixedSize(240, 200)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("selected", False)

        # 내부 레이아웃
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(8)

        # 제목
        title_label = QLabel(title)
        title_label.setFont(QFont("Pretendard", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(title_label)

        # 부제목
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Pretendard", 15))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from .common import TEXT_SECONDARY
        subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        btn_layout.addWidget(subtitle_label)

        # 설명 1
        desc1_label = QLabel(desc1)
        desc1_label.setFont(QFont("Pretendard", 13))
        desc1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc1_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        btn_layout.addWidget(desc1_label)

        # 설명 2
        desc2_label = QLabel(desc2)
        desc2_label.setFont(QFont("Pretendard", 13))
        desc2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc2_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        btn_layout.addWidget(desc2_label)

        btn.setLayout(btn_layout)

        return btn

    def _select_mode(self, mode: str):
        """모드 선택 (dialogue 또는 string) - v2 카드 선택 스타일"""
        self.selected_mode = mode

        # 카드 선택 상태 업데이트 (property 사용)
        self.dialogue_btn.setProperty("selected", mode == 'dialogue')
        self.string_btn.setProperty("selected", mode == 'string')

        # 스타일 다시 적용 (property 변경 반영)
        self.dialogue_btn.style().unpolish(self.dialogue_btn)
        self.dialogue_btn.style().polish(self.dialogue_btn)
        self.string_btn.style().unpolish(self.string_btn)
        self.string_btn.style().polish(self.string_btn)

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
        # 스타일은 QSS에서 자동 처리됨 (enabled/disabled 상태)







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
