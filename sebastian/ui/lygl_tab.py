"""
LYGL 탭 - LY Table 현지화 도구

wireframe 스펙:
- 기능 버튼: 240 × 180
- 그리드: 2×2, gap 24px
- 배경: gradient(#F3E5F5, #E1BEE7)
- 테두리: 2px solid #BA68C8
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .common import *
from .wizards import MergeWizard, SplitWizard, BatchWizard, DiffWizard, StatusCheckWizard
from workers.lygl_worker import LYGLMergeWorker, LYGLSplitWorker, LYGLBatchWorker, LYGLDiffWorker, LYGLStatusCheckWorker


class LYGLTab(QWidget):
    """LY/GL 탭"""

    # Signals
    merge_requested = pyqtSignal()
    split_requested = pyqtSignal()
    batch_requested = pyqtSignal()
    diff_requested = pyqtSignal()
    status_check_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()

    def _connect_signals(self):
        """Signal 연결"""
        self.merge_requested.connect(self._show_merge_wizard)
        self.split_requested.connect(self._show_split_wizard)
        self.batch_requested.connect(self._show_batch_wizard)
        self.diff_requested.connect(self._show_diff_wizard)
        self.status_check_requested.connect(self._show_status_check_wizard)

    def _show_merge_wizard(self):
        """Merge 위저드 표시"""
        wizard = MergeWizard(self)
        if wizard.exec():
            data = wizard.get_data()
            # Worker 실행
            self.worker = LYGLMergeWorker(data['files'], data['output'])
            self._run_worker(self.worker, "LY/GL Merge")

    def _show_split_wizard(self):
        """Split 위저드 표시"""
        wizard = SplitWizard(self)
        if wizard.exec():
            data = wizard.get_data()
            # Worker 실행
            self.worker = LYGLSplitWorker(data['input_file'], data['output_folder'])
            self._run_worker(self.worker, "LY/GL Split")

    def _show_batch_wizard(self):
        """Batch 위저드 표시"""
        wizard = BatchWizard(self)
        if wizard.exec():
            data = wizard.get_data()
            # Worker 실행 (batch_info 포함)
            self.worker = LYGLBatchWorker(
                root_folder=data['root_folder'],
                selected_batches=data['selected_batches'],
                base_batch=data['base_batch'],
                batch_info=data['batch_info'],
                output_path=data['output'],
                auto_complete=data['auto_complete']
            )
            self._run_worker(self.worker, "LY/GL Batches")

    def _show_diff_wizard(self):
        """Diff 위저드 표시"""
        wizard = DiffWizard(self)
        if wizard.exec():
            data = wizard.get_data()
            # Worker 실행
            self.worker = LYGLDiffWorker(
                data['folder1'],
                data['folder2'],
                data['output']
            )
            self._run_worker(self.worker, "LY/GL Diff")

    def _show_status_check_wizard(self):
        """Status Check 위저드 표시"""
        wizard = StatusCheckWizard(self)
        if wizard.exec():
            data = wizard.get_data()
            # Worker 실행 (파일 리스트와 출력 경로 전달)
            self.worker = LYGLStatusCheckWorker(
                file_paths=data['files'],  # 파일 경로 리스트
                output_path=str(data['output'])
            )
            self._run_worker(self.worker, "LY/GL Status Check")

    def _run_worker(self, worker, title: str):
        """Worker 실행 (공통)"""
        from .common import ProgressDialog

        # ProgressDialog 생성
        self.progress_dialog = ProgressDialog(self, title, LYGL)

        # Signal 연결
        worker.progress_updated.connect(self.progress_dialog.update_progress)
        worker.status_updated.connect(lambda msg: self.progress_dialog.update_file(msg))
        worker.completed.connect(self._on_completed)
        worker.error_occurred.connect(self._on_error)

        # 취소/최소화 연결
        self.progress_dialog.cancel_requested.connect(self._on_cancel)
        self.progress_dialog.minimize_requested.connect(self.progress_dialog.hide)

        # Worker 시작
        worker.start()
        self.progress_dialog.exec()

    def _on_completed(self, message: str):
        """작업 완료"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.accept()
        QMessageBox.information(self, "완료", message)

    def _on_error(self, message: str):
        """에러 발생"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.reject()
        QMessageBox.critical(self, "오류", message)

    def _on_cancel(self):
        """작업 취소"""
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.reject()

    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)

        # 그리드 레이아웃 (2×2)
        grid = QGridLayout()
        grid.setSpacing(24)

        # Merge 버튼
        merge_btn = self._create_function_button(
            "Merge",
            "7 → 1",
            "언어별 파일",
            "통합 생성"
        )
        merge_btn.clicked.connect(self.merge_requested.emit)
        grid.addWidget(merge_btn, 0, 0)

        # Split 버튼
        split_btn = self._create_function_button(
            "Split",
            "1 → 7",
            "통합 파일",
            "언어별 분리"
        )
        split_btn.clicked.connect(self.split_requested.emit)
        grid.addWidget(split_btn, 0, 1)

        # Batches 버튼
        batch_btn = self._create_function_button(
            "Batches",
            "배치 병합",
            "중복 KEY",
            "자동 제거"
        )
        batch_btn.clicked.connect(self.batch_requested.emit)
        grid.addWidget(batch_btn, 1, 0)

        # Diff 버튼
        diff_btn = self._create_function_button(
            "Diff",
            "버전 비교",
            "변경 사항",
            "추적"
        )
        diff_btn.clicked.connect(self.diff_requested.emit)
        grid.addWidget(diff_btn, 1, 1)

        layout.addLayout(grid)

        # Status Check 버튼 (중앙)
        status_check_layout = QVBoxLayout()
        status_check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_check_layout.setSpacing(8)

        status_check_btn = QPushButton("Status Check")
        status_check_btn.setFixedSize(120, 40)
        status_check_btn.setFont(QFont("Pretendard", 11, QFont.Weight.Bold))
        status_check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        status_check_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #BA68C8,
                    stop:1 #9C27B0
                );
                color: white;
                border: 1px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #CE93D8,
                    stop:1 #BA68C8
                );
            }}
        """)
        status_check_btn.clicked.connect(self.status_check_requested.emit)
        status_check_layout.addWidget(status_check_btn)

        # 설명 레이블
        status_desc = QLabel("언어별 Status 통일 검증")
        status_desc.setFont(QFont("Pretendard", 10))
        status_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_desc.setStyleSheet(f"color: {TEXT_SECONDARY};")
        status_check_layout.addWidget(status_desc)

        layout.addLayout(status_check_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _create_function_button(self, title: str, subtitle: str, desc1: str, desc2: str) -> QPushButton:
        """기능 버튼 생성"""
        btn = QPushButton()
        btn.setFixedSize(240, 180)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F3E5F5,
                    stop:1 #E1BEE7
                );
                border: 2px solid #BA68C8;
                border-radius: 12px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E1BEE7,
                    stop:1 #CE93D8
                );
            }}
        """)

        # 버튼 내부 레이아웃
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setFont(QFont("Pretendard", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Pretendard", 16))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(subtitle_label)

        desc1_label = QLabel(desc1)
        desc1_label.setFont(QFont("Pretendard", 13))
        desc1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(desc1_label)

        desc2_label = QLabel(desc2)
        desc2_label.setFont(QFont("Pretendard", 13))
        desc2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(desc2_label)

        btn.setLayout(btn_layout)

        return btn
