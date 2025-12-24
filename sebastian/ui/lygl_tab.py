"""
LYGL 탭 - LY Table 현지화 도구

wireframe 스펙:
- 기능 버튼: 240 × 180
- 그리드: 2×2, gap 24px
- 배경: gradient(#F3E5F5, #E1BEE7)
- 테두리: 2px solid #BA68C8
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
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
        
        # step_updated, files_count_updated가 있으면 연결
        if hasattr(worker, 'step_updated'):
            worker.step_updated.connect(self.progress_dialog.update_step)
        if hasattr(worker, 'files_count_updated'):
            worker.files_count_updated.connect(self.progress_dialog.update_files)
        
        worker.time_updated.connect(self.progress_dialog.update_time)
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
        """UI 초기화 - v2 수직 리스트 디자인"""
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(12)  # 버튼 간격 12px

        # 기능 버튼 (수직 리스트)
        functions = [
            ("Merge", "7 → 1", "언어별 파일 → 통합 생성", self.merge_requested.emit),
            ("Split", "1 → 7", "통합 파일 → 언어별 분리", self.split_requested.emit),
            ("Batches", "배치 병합", "Status 자동 완료 처리", self.batch_requested.emit),
            ("Diff", "버전 비교", "변경 사항 추적", self.diff_requested.emit),
            ("Status Check", "Status 통일 검증", "언어별 Status 일치 확인", self.status_check_requested.emit),
        ]

        for title, subtitle, description, signal in functions:
            btn = self._create_list_button(title, subtitle, description)
            btn.clicked.connect(signal)
            layout.addWidget(btn)

        layout.addStretch()

        self.setLayout(layout)

    def _create_list_button(self, title: str, subtitle: str, description: str) -> QPushButton:
        """수직 리스트 아이템 버튼 생성 (v2 미니멀 디자인)
        
        Args:
            title: 제목 (예: "Merge")
            subtitle: 부제목 (예: "7 → 1")
            description: 설명 (예: "언어별 파일 → 통합 생성")
        
        Returns:
            QPushButton: 리스트 아이템 버튼
        """
        btn = QPushButton()
        btn.setObjectName("listItemButton")
        btn.setMinimumHeight(64)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 내부 레이아웃 (수평)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(16, 10, 16, 10)
        btn_layout.setSpacing(16)

        # 왼쪽 영역: 제목 + 설명 (수직)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setFont(QFont("Pretendard", 15, QFont.Weight.DemiBold))
        left_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setFont(QFont("Pretendard", 12))
        from .common import TEXT_SECONDARY
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        left_layout.addWidget(desc_label)

        btn_layout.addLayout(left_layout)

        # 중앙: 빈 공간 (flexible)
        btn_layout.addStretch()

        # 우측: 부제목
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Pretendard", 13))
        subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        btn_layout.addWidget(subtitle_label)

        # 화살표 아이콘
        arrow_label = QLabel("→")
        arrow_label.setFont(QFont("Pretendard", 20))
        from .common import TEXT_DISABLED
        arrow_label.setStyleSheet(f"color: {TEXT_DISABLED};")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(arrow_label)

        btn.setLayout(btn_layout)

        return btn
