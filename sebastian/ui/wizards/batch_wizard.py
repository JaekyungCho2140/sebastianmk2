"""
LY/GL Batch 위저드

wireframe 스펙:
- 배치 폴더 목록 (라디오 + 제어)
- 기준 배치 선택
- Status 자동 완료 체크박스
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QScrollArea,
    QWidget, QRadioButton, QCheckBox, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import sys
sys.path.append('..')
from ui.common.colors import *


class BatchWizard(QDialog):
    """LY/GL Batch 위저드"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.batch_folders = []  # [(name, path), ...]
        self.batch_info = {}  # scan_batch_folders() 결과
        self.root_folder = None
        self.base_batch_index = 0
        self.output_path = ""
        self.auto_complete = False
        self.radio_group = QButtonGroup()  # 라디오 버튼 그룹
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setWindowTitle("LY/GL Merge Batches 위저드")
        self.setMinimumSize(600, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # 타이틀
        title = QLabel("배치 폴더 목록")
        title.setFont(QFont("Pretendard", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        # 배치 목록 스크롤
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                background-color: {BG_PRIMARY};
            }}
        """)

        self.batch_list_widget = QWidget()
        self.batch_list_layout = QVBoxLayout()
        self.batch_list_layout.setSpacing(4)
        self.batch_list_layout.setContentsMargins(8, 8, 8, 8)
        self.batch_list_widget.setLayout(self.batch_list_layout)
        scroll.setWidget(self.batch_list_widget)

        layout.addWidget(scroll)

        # 배치 루트 폴더 선택 버튼 (레거시 방식: 자동 스캔)
        add_btn = QPushButton("+ 루트 폴더 선택 (배치 자동 스캔)")
        add_btn.setMinimumHeight(40)
        add_btn.setFont(QFont("Pretendard", 12))
        add_btn.setStyleSheet(f"""
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
        add_btn.clicked.connect(self._scan_batches)
        layout.addWidget(add_btn)

        # 기준 배치 안내
        self.base_info = QLabel()
        self.base_info.setWordWrap(True)
        self.base_info.setFont(QFont("Pretendard", 12))
        self.base_info.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #F3E5F5,
                stop:1 #E1BEE7
            );
            border: 2px solid {LYGL};
            border-radius: 8px;
            padding: 16px;
            color: {TEXT_PRIMARY};
        """)
        self._update_base_info()
        layout.addWidget(self.base_info)

        # 저장 위치
        save_label = QLabel("저장 위치")
        save_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
        save_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(save_label)

        save_layout = QHBoxLayout()

        self.save_input = QLineEdit()
        self.save_input.setReadOnly(True)
        self.save_input.setPlaceholderText("{루트}/Output/")
        self.save_input.setMinimumHeight(40)
        self.save_input.setFont(QFont("Pretendard", 12))
        self.save_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
            }}
        """)
        save_layout.addWidget(self.save_input)

        save_btn = QPushButton("선택")
        save_btn.setMinimumSize(80, 40)
        save_btn.setFont(QFont("Pretendard", 12))
        save_btn.setStyleSheet(f"""
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
        save_btn.clicked.connect(self._select_output)
        save_layout.addWidget(save_btn)

        layout.addLayout(save_layout)

        # Status 자동 완료 체크박스
        self.auto_complete_cb = QCheckBox("Status 자동 완료 적용")
        self.auto_complete_cb.setFont(QFont("Pretendard", 12))
        self.auto_complete_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRIMARY};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {BORDER};
                border-radius: 4px;
                background-color: {BG_PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {LYGL};
                border-color: {LYGL};
            }}
        """)
        self.auto_complete_cb.stateChanged.connect(lambda: setattr(self, 'auto_complete', self.auto_complete_cb.isChecked()))
        layout.addWidget(self.auto_complete_cb)

        hint = QLabel("(번역필요/수정 → 완료)")
        hint.setFont(QFont("Pretendard", 11))
        hint.setStyleSheet(f"color: {TEXT_SECONDARY}; margin-left: 32px;")
        layout.addWidget(hint)

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

    def _scan_batches(self):
        """루트 폴더 선택 후 배치 자동 스캔 (레거시 방식)"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "배치 루트 폴더 선택",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            try:
                from pathlib import Path
                from core.lygl.batch_merger import scan_batch_folders, sort_batches

                # 배치 폴더 스캔
                root_path = Path(folder)
                self.root_folder = root_path
                self.batch_info = scan_batch_folders(root_path)

                # 유효한 배치만 필터링
                valid_batches = {name: info for name, info in self.batch_info.items() if info.get('valid', False)}

                if not valid_batches:
                    raise Exception("유효한 배치 폴더가 없습니다. 7개 언어 파일이 있는 배치를 확인하세요.")

                # 배치 정렬 (REGULAR 첫 번째)
                batch_names = sort_batches(list(valid_batches.keys()))

                # batch_folders 구성 (유효한 배치만)
                self.batch_folders = []
                for batch_name in batch_names:
                    info = valid_batches[batch_name]
                    batch_path = root_path / info['folder']
                    self.batch_folders.append((batch_name, str(batch_path)))

                # batch_info도 유효한 배치만 유지
                self.batch_info = valid_batches

                # REGULAR가 있으면 기준 배치로 설정
                if 'REGULAR' in batch_names:
                    self.base_batch_index = batch_names.index('REGULAR')
                else:
                    self.base_batch_index = 0

                self._update_batch_list()
                self._check_execute_enabled()

            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "경고", f"배치 스캔 실패: {str(e)}")

    def _update_batch_list(self):
        """배치 목록 업데이트"""
        # 기존 항목 제거
        for i in reversed(range(self.batch_list_layout.count())):
            self.batch_list_layout.itemAt(i).widget().setParent(None)

        # 라디오 버튼 그룹 초기화
        for button in self.radio_group.buttons():
            self.radio_group.removeButton(button)

        # 새 항목 추가
        for idx, (name, path) in enumerate(self.batch_folders):
            item_widget = QWidget()
            item_widget.setFixedHeight(48)
            item_widget.setStyleSheet(f"""
                background-color: {BG_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
            """)

            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(12, 0, 12, 0)
            item_layout.setSpacing(8)

            # 라디오 버튼 (그룹에 추가)
            radio = QRadioButton()
            radio.setChecked(idx == self.base_batch_index)
            self.radio_group.addButton(radio, idx)  # 그룹에 추가 + ID 설정
            radio.toggled.connect(lambda checked, i=idx: self._set_base_batch(i) if checked else None)
            radio.setStyleSheet(f"""
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {LYGL};
                }}
            """)
            item_layout.addWidget(radio)

            # 이름
            name_label = QLabel(f"{name}")
            name_label.setFont(QFont("Pretendard", 12, QFont.Weight.Medium))
            item_layout.addWidget(name_label)

            item_layout.addStretch()

            # 제어 버튼 (lambda 캡처 버그 수정: i=idx로 고정)
            up_btn = QPushButton("↑")
            up_btn.setFixedSize(32, 32)
            up_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_SECONDARY};
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {BG_TERTIARY};
                }}
            """)
            up_btn.clicked.connect(lambda checked=False, i=idx: self._move_up(i))
            item_layout.addWidget(up_btn)

            down_btn = QPushButton("↓")
            down_btn.setFixedSize(32, 32)
            down_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_SECONDARY};
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {BG_TERTIARY};
                }}
            """)
            down_btn.clicked.connect(lambda checked=False, i=idx: self._move_down(i))
            item_layout.addWidget(down_btn)

            remove_btn = QPushButton("제거")
            remove_btn.setFixedSize(50, 32)
            remove_btn.setFont(QFont("Pretendard", 10))
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_SECONDARY};
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                    color: {ERROR};
                }}
                QPushButton:hover {{
                    background-color: {ERROR_BG};
                }}
            """)
            remove_btn.clicked.connect(lambda checked=False, i=idx: self._remove_batch(i))
            item_layout.addWidget(remove_btn)

            item_widget.setLayout(item_layout)
            self.batch_list_layout.addWidget(item_widget)

        self._update_base_info()

    def _set_base_batch(self, index: int):
        """기준 배치 설정"""
        self.base_batch_index = index
        self._update_base_info()

    def _move_up(self, index: int):
        """배치 위로 이동"""
        if index > 0:
            self.batch_folders[index], self.batch_folders[index - 1] = \
                self.batch_folders[index - 1], self.batch_folders[index]
            if self.base_batch_index == index:
                self.base_batch_index = index - 1
            elif self.base_batch_index == index - 1:
                self.base_batch_index = index
            self._update_batch_list()

    def _move_down(self, index: int):
        """배치 아래로 이동"""
        if index < len(self.batch_folders) - 1:
            self.batch_folders[index], self.batch_folders[index + 1] = \
                self.batch_folders[index + 1], self.batch_folders[index]
            if self.base_batch_index == index:
                self.base_batch_index = index + 1
            elif self.base_batch_index == index + 1:
                self.base_batch_index = index
            self._update_batch_list()

    def _remove_batch(self, index: int):
        """배치 제거"""
        del self.batch_folders[index]
        if self.base_batch_index >= len(self.batch_folders):
            self.base_batch_index = max(0, len(self.batch_folders) - 1)
        self._update_batch_list()
        self._check_execute_enabled()

    def _update_base_info(self):
        """기준 배치 정보 업데이트"""
        if self.batch_folders:
            base_name = self.batch_folders[self.base_batch_index][0]
            self.base_info.setText(f"📌 기준 배치: {base_name}\n    (병합 순서의 첫 번째가 됩니다)")
        else:
            self.base_info.setText("📌 기준 배치: (배치 폴더를 추가하세요)")

    def _select_output(self):
        """저장 위치 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "저장 위치 선택",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.output_path = folder
            self.save_input.setText(folder)
            self._check_execute_enabled()

    def _check_execute_enabled(self):
        """실행 버튼 활성화 체크"""
        enabled = len(self.batch_folders) >= 2 and self.output_path != ""
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
        # 기준 배치를 첫 번째로 정렬
        ordered_folders = [self.batch_folders[self.base_batch_index]]
        ordered_folders.extend([f for i, f in enumerate(self.batch_folders) if i != self.base_batch_index])

        # 선택된 배치 이름 목록
        selected_batches = [name for name, path in ordered_folders]
        base_batch = selected_batches[0]

        return {
            'root_folder': self.root_folder,
            'selected_batches': selected_batches,
            'base_batch': base_batch,
            'batch_info': self.batch_info,
            'output': self.output_path,
            'auto_complete': self.auto_complete
        }
