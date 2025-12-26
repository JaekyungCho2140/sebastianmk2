"""공통 기능 탭

여러 게임에 공통으로 사용되는 기능을 제공하는 탭입니다.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from sebastian.ui.common.design_tokens import DesignTokens
import logging

logger = logging.getLogger(__name__)


class CommonTab(QWidget):
    """공통 기능 탭

    여러 게임에 공통으로 사용되는 기능을 제공합니다.
    현재 제공 기능:
        - CSV 따옴표 복원: memoQ export 파일의 따옴표 복원

    Signals:
        restore_csv_requested: CSV 복원 요청

    Examples:
        >>> tab = CommonTab()
        >>> tab.restore_csv_requested.connect(on_restore_csv)
    """

    restore_csv_requested = pyqtSignal()

    def __init__(self, parent=None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        logger.info("CommonTab 생성")

    def _setup_ui(self):
        """UI 설정 (LY/GL 스타일)"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignTokens.SPACING_LG)
        layout.setContentsMargins(
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
        )

        # 제목
        title = QLabel("공통 도구")
        title.setObjectName("tabTitle")
        title.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {DesignTokens.TEXT_PRIMARY}; "
            f"margin-bottom: {DesignTokens.SPACING_MD}px;"
        )
        layout.addWidget(title)

        # 설명
        description = QLabel(
            "여러 게임에 공통으로 사용할 수 있는 도구 모음입니다.\n"
            "CSV 파일 처리, 데이터 변환 등의 기능을 제공합니다."
        )
        description.setWordWrap(True)
        description.setStyleSheet(
            f"color: {DesignTokens.TEXT_SECONDARY}; "
            f"margin-bottom: {DesignTokens.SPACING_LG}px;"
        )
        layout.addWidget(description)

        # 기능 리스트 (LY/GL 스타일)
        functions = [
            (
                "CSV 따옴표 복원",
                "memoQ export 파일의 따옴표를 원본 파일과 비교하여 복원합니다",
                self.restore_csv_requested.emit,
            ),
            # 향후 추가 기능...
            # ("CSV 병합", "여러 CSV 파일을 하나로 병합합니다", self.merge_csv_requested.emit),
            # ("CSV 분할", "큰 CSV 파일을 작은 파일로 분할합니다", self.split_csv_requested.emit),
        ]

        for title_text, description_text, handler in functions:
            btn = self._create_function_button(title_text, description_text)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()

    def _create_function_button(self, title: str, description: str) -> QPushButton:
        """기능 버튼 생성 (LY/GL 스타일)

        Args:
            title: 버튼 제목
            description: 버튼 설명

        Returns:
            QPushButton: 생성된 버튼
        """
        btn = QPushButton()
        btn.setObjectName("listItemButton")
        btn.setFixedHeight(64)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 버튼 텍스트 (타이틀 + 설명)
        # LY/GL과 동일하게 화살표 아이콘 추가
        btn_text = f"{title}\n{description}"
        btn.setText(btn_text)

        # 텍스트 정렬 (왼쪽 정렬)
        btn.setStyleSheet(
            btn.styleSheet()
            + f"""
            QPushButton#listItemButton {{
                text-align: left;
                padding-left: {DesignTokens.SPACING_MD}px;
                padding-right: {DesignTokens.SPACING_MD}px;
            }}
            QPushButton#listItemButton::after {{
                content: '→';
                position: absolute;
                right: {DesignTokens.SPACING_MD}px;
                font-size: 24px;
                color: {DesignTokens.PRIMARY};
            }}
        """
        )

        return btn

    def _connect_signals(self):
        """Signal 연결"""
        pass
