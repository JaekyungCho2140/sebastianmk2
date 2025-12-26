"""
배치 선택 UI 모듈

PRD v1.4.0 섹션 2.3 "배치 선택 다이얼로그"에 정의된 UI를 구현합니다.
- 체크박스: 배치 선택
- 라디오 버튼: 기준 배치 선택
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import List, Dict, Callable, Optional, Tuple


class BatchSelectionDialog(ctk.CTkToplevel):
    """배치 선택 다이얼로그 (v1.4.0)"""

    def __init__(self, parent, batch_info: Dict, on_confirm: Callable, on_cancel: Callable):
        """
        Args:
            parent: 부모 윈도우
            batch_info: scan_batch_folders() 결과
            on_confirm: 확인 버튼 콜백 (selected_batches: List[str], base_batch: str)
            on_cancel: 취소 버튼 콜백
        """
        super().__init__(parent)

        self.batch_info = batch_info
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
        self.result = False

        # 배치 정렬 (REGULAR 첫 번째, EXTRA 번호순)
        from .batch_merger import sort_batches
        self.batch_names = sort_batches(list(batch_info.keys()))

        # 체크박스 딕셔너리
        self.checkbox_vars: Dict[str, ctk.BooleanVar] = {}
        self.checkbox_widgets: Dict[str, ctk.CTkCheckBox] = {}

        # 기준 배치 라디오 버튼 변수
        default_base = 'REGULAR' if 'REGULAR' in self.batch_names else self.batch_names[0]
        self.base_batch_var = ctk.StringVar(value=default_base)

        # 선택된 배치 저장
        self.selected_batches: List[str] = []

        # UI 설정
        self.title("배치 선택")
        self.resizable(False, True)

        # 창 크기 계산 (배치 개수에 따라 동적 조절)
        base_height = 280
        checkbox_height = 38 * len(self.batch_names)
        total_height = min(base_height + checkbox_height, 700)  # 최대 700

        self.geometry(f"550x{total_height}")

        # 모달 설정
        self.transient(parent)
        self.grab_set()

        # UI 생성
        self._create_widgets()

        # 기본 기준 배치 체크
        self._ensure_base_batch_checked()

        # 창 중앙 배치
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """UI 위젯 생성"""
        # 헤더
        header = ctk.CTkLabel(
            self,
            text="병합할 배치를 선택해주세요",
            font=("맑은 고딕", 16, "bold"),
            text_color="#1e293b"
        )
        header.pack(pady=(20, 15))

        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=500,
            height=min(300, 38 * len(self.batch_names))
        )
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 헤더 행
        header_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_row,
            text="선택",
            width=60,
            font=("맑은 고딕", 11, "bold"),
            text_color="#64748b"
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            header_row,
            text="배치",
            width=280,
            anchor="w",
            font=("맑은 고딕", 11, "bold"),
            text_color="#64748b"
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            header_row,
            text="기준",
            width=60,
            font=("맑은 고딕", 11, "bold"),
            text_color="#64748b"
        ).pack(side="left", padx=(10, 0))

        # 배치별 행 생성
        for batch_name in self.batch_names:
            self._create_batch_row(scroll_frame, batch_name)

        # 버튼 프레임
        button_frame1 = ctk.CTkFrame(self, fg_color="transparent")
        button_frame1.pack(pady=5)

        # 전체 선택/해제 버튼
        btn_select_all = ctk.CTkButton(
            button_frame1,
            text="전체 선택",
            width=120,
            height=32,
            command=self._select_all
        )
        btn_select_all.pack(side="left", padx=5)

        btn_deselect_all = ctk.CTkButton(
            button_frame1,
            text="전체 해제",
            width=120,
            height=32,
            command=self._deselect_all
        )
        btn_deselect_all.pack(side="left", padx=5)

        # 확인/취소 버튼 프레임
        button_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        button_frame2.pack(pady=(5, 20))

        btn_confirm = ctk.CTkButton(
            button_frame2,
            text="확인",
            width=120,
            height=36,
            fg_color="#1e293b",
            hover_color="#334155",
            command=self._on_confirm
        )
        btn_confirm.pack(side="left", padx=5)

        btn_cancel = ctk.CTkButton(
            button_frame2,
            text="취소",
            width=120,
            height=36,
            fg_color="transparent",
            border_width=2,
            border_color="#1e293b",
            text_color="#1e293b",
            hover_color="#f1f5f9",
            command=self._on_cancel
        )
        btn_cancel.pack(side="left", padx=5)

    def _create_batch_row(self, parent, batch_name: str):
        """배치별 행 생성 (체크박스 + 라벨 + 라디오 버튼)"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        # 체크박스 변수
        var = ctk.BooleanVar(value=True)  # 기본 체크
        self.checkbox_vars[batch_name] = var

        # 체크박스
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=var,
            width=40,
            command=lambda bn=batch_name: self._on_checkbox_changed(bn)
        )
        checkbox.pack(side="left", padx=(10, 0))
        self.checkbox_widgets[batch_name] = checkbox

        # 배치명 라벨
        ctk.CTkLabel(
            row_frame,
            text=batch_name,
            width=280,
            anchor="w",
            font=("맑은 고딕", 12)
        ).pack(side="left", padx=(10, 0))

        # 라디오 버튼 (기준 배치 선택)
        radio = ctk.CTkRadioButton(
            row_frame,
            text="",
            variable=self.base_batch_var,
            value=batch_name,
            width=40,
            command=lambda bn=batch_name: self._on_base_batch_changed(bn)
        )
        radio.pack(side="left", padx=(10, 0))

    def _on_base_batch_changed(self, batch_name: str):
        """
        기준 배치 라디오 버튼 선택 시

        Args:
            batch_name: 선택된 배치명
        """
        # 해당 배치의 체크박스 자동 체크
        self.checkbox_vars[batch_name].set(True)

    def _on_checkbox_changed(self, batch_name: str):
        """
        체크박스 변경 시

        Args:
            batch_name: 배치명
        """
        is_checked = self.checkbox_vars[batch_name].get()

        # 기준 배치인 경우
        if self.base_batch_var.get() == batch_name:
            if not is_checked:
                # 체크 해제 시도: 강제로 다시 체크
                self.checkbox_vars[batch_name].set(True)

                # 경고 메시지
                messagebox.showwarning(
                    "기준 배치",
                    f"{batch_name}는 기준 배치로 선택되어 있어 체크를 해제할 수 없습니다.\n\n"
                    f"다른 배치를 기준으로 선택한 후 체크를 해제해주세요."
                )

    def _ensure_base_batch_checked(self):
        """기준 배치가 반드시 체크되어 있도록 보장"""
        base_batch = self.base_batch_var.get()
        if base_batch:
            self.checkbox_vars[base_batch].set(True)

    def _select_all(self):
        """전체 선택"""
        for batch_name in self.checkbox_vars:
            self.checkbox_vars[batch_name].set(True)

    def _deselect_all(self):
        """전체 해제 (기준 배치 제외)"""
        base_batch = self.base_batch_var.get()
        for batch_name in self.checkbox_vars:
            if batch_name != base_batch:
                self.checkbox_vars[batch_name].set(False)

    def _on_confirm(self):
        """확인 버튼 클릭"""
        # 선택된 배치 수집
        self.selected_batches = [
            batch_name
            for batch_name, var in self.checkbox_vars.items()
            if var.get()
        ]

        self.result = True

        # 콜백 호출
        if self.on_confirm_callback:
            base_batch = self.base_batch_var.get()
            self.on_confirm_callback(self.selected_batches, base_batch)

        self.destroy()

    def _on_cancel(self):
        """취소 버튼 클릭"""
        self.result = False

        if self.on_cancel_callback:
            self.on_cancel_callback()

        self.destroy()

    def get_result(self) -> Tuple[List[str], str]:
        """
        다이얼로그 결과 반환

        Returns:
            Tuple[List[str], str]: (선택된 배치 리스트, 기준 배치명)
            - 취소 시: ([], "")
        """
        if self.result:
            return self.selected_batches, self.base_batch_var.get()
        return [], ""


# 기존 BatchCheckbox 클래스는 더 이상 사용되지 않음 (호환성을 위해 유지)
class BatchCheckbox:
    """배치 체크박스 (deprecated - v1.4.0에서는 BatchSelectionDialog 내부로 통합됨)"""

    def __init__(self, parent, batch_name: str, is_required: bool, batch_data: Dict):
        """
        Args:
            parent: 부모 위젯
            batch_name: 배치명
            is_required: 필수 여부 (더 이상 사용되지 않음)
            batch_data: 배치 정보
        """
        self.batch_name = batch_name
        self.is_required = is_required

        # 변수
        self.var = ctk.BooleanVar(value=True)  # 기본 체크

        # 표시 텍스트
        display_text = batch_name

        # 체크박스
        self.checkbox = ctk.CTkCheckBox(
            parent,
            text=display_text,
            variable=self.var,
            font=("맑은 고딕", 12)
        )
        self.checkbox.pack(pady=3, padx=20, anchor="w")

    def is_checked(self) -> bool:
        """체크 상태 반환"""
        return self.var.get()

    def set_checked(self, checked: bool):
        """체크 상태 설정"""
        self.var.set(checked)
