"""CSV 따옴표 복원 Wizard

단일 페이지 Wizard로 원본 파일, export 파일, 출력 폴더를 선택합니다.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QFileDialog,
)
from PyQt6.QtCore import Qt
from sebastian.ui.common.design_tokens import DesignTokens
import logging

logger = logging.getLogger(__name__)


class RestoreCSVWizard(QDialog):
    """CSV 따옴표 복원 Wizard (단일 페이지)

    원본 CSV 파일, memoQ export CSV 파일, 출력 폴더를 선택하여
    CSV 따옴표 복원 작업을 설정합니다.

    UI 구성:
        [원본 파일 선택]  [📁 찾아보기]
        [export 파일 선택] [📁 찾아보기]
        [출력 폴더 선택]   [📁 찾아보기]

        [취소] [복원 시작]

    Examples:
        >>> wizard = RestoreCSVWizard(parent_window)
        >>> if wizard.exec() == QDialog.DialogCode.Accepted:
        ...     data = wizard.get_data()
        ...     print(data['original_path'])
    """

    def __init__(self, parent=None):
        """초기화

        Args:
            parent: 부모 위젯 (MainWindow)
        """
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("CSV 따옴표 복원")
        self.resize(700, 350)

        self.original_path = ""
        self.export_path = ""
        self.output_dir = ""

        self._setup_ui()
        self._connect_signals()

        logger.info("RestoreCSVWizard 생성")

    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignTokens.SPACING_MD)
        layout.setContentsMargins(
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
        )

        # 제목
        title = QLabel("CSV 따옴표 복원")
        title.setObjectName("dialogTitle")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {DesignTokens.TEXT_PRIMARY};"
        )
        layout.addWidget(title)

        # 설명
        description = QLabel(
            "memoQ에서 export한 CSV 파일의 따옴표를 원본 파일과 비교하여 복원합니다.\n"
            "원본 파일, export 파일, 출력 폴더를 선택해주세요."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {DesignTokens.TEXT_SECONDARY}; margin-bottom: 16px;")
        layout.addWidget(description)

        # 원본 파일 선택
        original_layout = QHBoxLayout()
        original_layout.setSpacing(DesignTokens.SPACING_SM)

        self.original_label = QLabel("원본 파일:")
        self.original_label.setMinimumWidth(120)
        self.original_label.setStyleSheet(f"font-weight: bold; color: {DesignTokens.TEXT_PRIMARY};")

        self.original_edit = QLineEdit()
        self.original_edit.setReadOnly(True)
        self.original_edit.setPlaceholderText("원본 CSV 파일을 선택하세요")
        self.original_edit.setMinimumHeight(40)

        self.original_btn = QPushButton("📁 찾아보기")
        self.original_btn.setObjectName("secondaryButton")
        self.original_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.original_btn.setMinimumWidth(120)
        self.original_btn.setMinimumHeight(40)

        original_layout.addWidget(self.original_label)
        original_layout.addWidget(self.original_edit, 1)
        original_layout.addWidget(self.original_btn)
        layout.addLayout(original_layout)

        # export 파일 선택
        export_layout = QHBoxLayout()
        export_layout.setSpacing(DesignTokens.SPACING_SM)

        self.export_label = QLabel("memoQ Export:")
        self.export_label.setMinimumWidth(120)
        self.export_label.setStyleSheet(f"font-weight: bold; color: {DesignTokens.TEXT_PRIMARY};")

        self.export_edit = QLineEdit()
        self.export_edit.setReadOnly(True)
        self.export_edit.setPlaceholderText("memoQ export CSV 파일을 선택하세요")
        self.export_edit.setMinimumHeight(40)

        self.export_btn = QPushButton("📁 찾아보기")
        self.export_btn.setObjectName("secondaryButton")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setMinimumWidth(120)
        self.export_btn.setMinimumHeight(40)

        export_layout.addWidget(self.export_label)
        export_layout.addWidget(self.export_edit, 1)
        export_layout.addWidget(self.export_btn)
        layout.addLayout(export_layout)

        # 출력 폴더 선택
        output_layout = QHBoxLayout()
        output_layout.setSpacing(DesignTokens.SPACING_SM)

        self.output_label = QLabel("출력 폴더:")
        self.output_label.setMinimumWidth(120)
        self.output_label.setStyleSheet(f"font-weight: bold; color: {DesignTokens.TEXT_PRIMARY};")

        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("복원 파일을 저장할 폴더를 선택하세요")
        self.output_edit.setMinimumHeight(40)

        self.output_btn = QPushButton("📁 찾아보기")
        self.output_btn.setObjectName("secondaryButton")
        self.output_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_btn.setMinimumWidth(120)
        self.output_btn.setMinimumHeight(40)

        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_edit, 1)
        output_layout.addWidget(self.output_btn)
        layout.addLayout(output_layout)

        layout.addStretch()

        # 하단 버튼
        button_layout = QHBoxLayout()
        button_layout.setSpacing(DesignTokens.SPACING_SM)
        button_layout.addStretch()

        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setMinimumHeight(40)

        self.start_btn = QPushButton("복원 시작")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setEnabled(False)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.start_btn)
        layout.addLayout(button_layout)

    def _connect_signals(self):
        """Signal 연결"""
        self.original_btn.clicked.connect(self._select_original)
        self.export_btn.clicked.connect(self._select_export)
        self.output_btn.clicked.connect(self._select_output)
        self.cancel_btn.clicked.connect(self.reject)
        self.start_btn.clicked.connect(self.accept)

    def _select_original(self):
        """원본 파일 선택"""
        path, _ = QFileDialog.getOpenFileName(
            self, "원본 CSV 파일 선택", "", "CSV Files (*.csv)"
        )
        if path:
            self.original_path = path
            self.original_edit.setText(path)
            self._update_start_button()
            logger.info(f"원본 파일 선택: {path}")

    def _select_export(self):
        """export 파일 선택"""
        path, _ = QFileDialog.getOpenFileName(
            self, "memoQ Export CSV 파일 선택", "", "CSV Files (*.csv)"
        )
        if path:
            self.export_path = path
            self.export_edit.setText(path)
            self._update_start_button()
            logger.info(f"Export 파일 선택: {path}")

    def _select_output(self):
        """출력 폴더 선택"""
        path = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if path:
            self.output_dir = path
            self.output_edit.setText(path)
            self._update_start_button()
            logger.info(f"출력 폴더 선택: {path}")

    def _update_start_button(self):
        """시작 버튼 활성화 상태 업데이트

        모든 필드가 입력되었을 때만 시작 버튼을 활성화합니다.
        """
        enabled = (
            bool(self.original_path)
            and bool(self.export_path)
            and bool(self.output_dir)
        )
        self.start_btn.setEnabled(enabled)

    def get_data(self) -> dict:
        """선택된 데이터 반환

        Returns:
            {
                'original_path': str,  # 원본 파일 경로
                'export_path': str,    # export 파일 경로
                'output_dir': str      # 출력 폴더 경로
            }
        """
        return {
            "original_path": self.original_path,
            "export_path": self.export_path,
            "output_dir": self.output_dir,
        }
