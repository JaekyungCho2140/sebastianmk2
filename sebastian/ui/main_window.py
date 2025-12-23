"""
MainWindow - Sebastian 메인 창

wireframe 스펙:
- 창 크기: 1000 × 700 (기본), 800 × 600 (최소)
- 탭바: 48px 높이
- 로그: 200px (펼침), 32px (접힘)
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMenuBar, QMenu, QStatusBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont

from .common import *
from .m4gl_tab import M4GLTab
from .ncgl_tab import NCGLTab
from .lygl_tab import LYGLTab


class MainWindow(QMainWindow):
    """Sebastian 메인 창"""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        # 창 설정
        self.setWindowTitle("Sebastian - 게임 현지화 도구")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # 중앙 위젯
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 탭 위젯
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {BG_PRIMARY};
            }}
            QTabBar::tab {{
                background-color: {BG_SECONDARY};
                color: {TEXT_SECONDARY};
                padding: 12px 0;
                width: 120px;
                height: 48px;
                border: none;
                font-family: "Pretendard";
                font-size: 14px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {BG_PRIMARY};
                color: {TEXT_PRIMARY};
            }}
            QTabBar::tab:hover {{
                background-color: #FAFAFA;
            }}
        """)

        # 탭 추가
        self.m4gl_tab = M4GLTab()
        self.ncgl_tab = NCGLTab()
        self.lygl_tab = LYGLTab()

        self.tab_widget.addTab(self.m4gl_tab, "M4/GL")
        self.tab_widget.addTab(self.ncgl_tab, "NC/GL")
        self.tab_widget.addTab(self.lygl_tab, "LY/GL")

        layout.addWidget(self.tab_widget)

        # LogViewer
        self.log_viewer = LogViewer()
        layout.addWidget(self.log_viewer)

        # Signal 연결
        self._connect_signals()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 메뉴바
        self._setup_menubar()

        # 상태바
        self._setup_statusbar()

        # 전역 스타일
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BG_PRIMARY};
            }}
        """)

    def _connect_signals(self):
        """탭 Signal을 LogViewer와 연결"""
        # M4GL 탭
        self.m4gl_tab.execute_requested.connect(self._on_m4gl_execute)

        # NCGL 탭
        self.ncgl_tab.execute_requested.connect(self._on_ncgl_execute)

    def _on_m4gl_execute(self, mode: str, folder_path: str):
        """M4GL 실행 완료"""
        mode_name = "DIALOGUE" if mode == 'dialogue' else "STRING"
        self.log_viewer.add_log(f"M4/GL {mode_name} 병합 완료: {folder_path}")
        self.update_status("완료", SUCCESS)

    def _on_ncgl_execute(self, folder_path: str, date: str, milestone: str):
        """NCGL 실행 완료"""
        self.log_viewer.add_log(f"NC/GL 병합 완료: {folder_path} (날짜: {date}, 마일스톤: M{milestone})")
        self.update_status("완료", SUCCESS)

    def _setup_menubar(self):
        """메뉴바 구성"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {BG_PRIMARY};
                border-bottom: 1px solid {BORDER};
                padding: 4px 8px;
                font-family: "Pretendard";
                font-size: 13px;
            }}
            QMenuBar::item {{
                padding: 4px 12px;
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {BG_SECONDARY};
            }}
            QMenu {{
                background-color: {BG_PRIMARY};
                border: 1px solid {BORDER};
                font-family: "Pretendard";
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 8px 24px;
            }}
            QMenu::item:selected {{
                background-color: {BG_SECONDARY};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {BORDER};
                margin: 4px 0;
            }}
        """)

        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")

        save_log_action = QAction("로그 저장...", self)
        save_log_action.triggered.connect(self._save_log)
        file_menu.addAction(save_log_action)

        file_menu.addSeparator()

        quit_action = QAction("종료", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말(&H)")

        guide_action = QAction("사용자 가이드", self)
        guide_action.triggered.connect(self._show_guide)
        help_menu.addAction(guide_action)

        help_menu.addSeparator()

        about_action = QAction("Sebastian 정보", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        """상태바 구성"""
        statusbar = QStatusBar()
        statusbar.setFont(QFont("Pretendard", 11))
        statusbar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {BG_SECONDARY};
                border-top: 1px solid {BORDER};
                color: {TEXT_SECONDARY};
                padding: 0 16px;
                min-height: 24px;
            }}
        """)
        statusbar.showMessage("준비 완료")
        self.setStatusBar(statusbar)

    def _save_log(self):
        """로그 저장"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "로그 저장",
            "sebastian_log.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_viewer.log_text.toPlainText())
                self.statusBar().showMessage(f"로그 저장됨: {file_path}", 3000)
                self.log_viewer.add_log(f"로그 저장: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"로그 저장 실패: {str(e)}")

    def _show_guide(self):
        """사용자 가이드 표시"""
        QMessageBox.information(
            self,
            "사용자 가이드",
            "README.md 파일을 참조하세요.\n\n"
            "각 탭에서 게임별 현지화 작업을 수행할 수 있습니다."
        )

    def _show_about(self):
        """Sebastian 정보 표시"""
        QMessageBox.about(
            self,
            "Sebastian 정보",
            "Sebastian v1.0.0\n\n"
            "게임 현지화 도구 통합 프로그램\n\n"
            "지원 게임:\n"
            "- M4/GL (MIR4)\n"
            "- NC/GL (NC)\n"
            "- LY/GL (LY Table)\n\n"
            "© 2025"
        )

    def update_status(self, message: str, color: str = TEXT_SECONDARY):
        """상태바 메시지 업데이트"""
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {BG_SECONDARY};
                border-top: 1px solid {BORDER};
                color: {color};
                padding: 0 16px;
                min-height: 24px;
            }}
        """)
        self.statusBar().showMessage(message)
