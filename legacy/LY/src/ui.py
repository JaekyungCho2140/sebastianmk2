"""
UI 모듈 (CustomTkinter)

PRD 섹션 3 "User Interface Specifications"에 정의된 UI를 구현합니다.
"""

import json
import threading
import time
from pathlib import Path
from typing import Optional, Callable, Dict, List
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .merge import merge_files
from .split import split_file
from .validator import ValidationError, extract_date
from .batch_merger import (
    scan_batch_folders,
    validate_batch_selection,
    merge_batches,
    BatchMergerError,
    UserCancelledError
)
from .batch_ui import BatchSelectionDialog
from .legacy_diff import legacy_diff, generate_diff_filename, LegacyDiffError


# 설정 파일 경로
CONFIG_FILE = Path.home() / ".ly_table_config.json"


class LYTableApp(ctk.CTk):
    """LY/GL 현지화 테이블 병합/분할 도구 메인 앱"""

    def __init__(self):
        super().__init__()

        # 앱 설정
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 윈도우 설정
        self.title("LY/GL 미네 전용 도구")
        self.geometry("400x410")  # v1.4.0: 버튼 4개 수용
        self.resizable(False, False)

        # 설정 로드
        self.config = self._load_config()

        # 작업 상태
        self.is_processing = False
        self.cancel_requested = False
        self.start_time = None
        self.last_progress = 0
        self.last_progress_time = None

        # UI 생성
        self._create_widgets()

    def _load_config(self) -> dict:
        """설정 파일 로드"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self):
        """설정 파일 저장"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def _get_last_directory(self, operation: str) -> str:
        """마지막 사용 디렉토리 가져오기"""
        path = self.config.get(operation)
        if path and Path(path).exists():
            return path
        return str(Path.home() / "Documents")

    def _save_last_directory(self, operation: str, directory: str):
        """마지막 사용 디렉토리 저장"""
        self.config[operation] = directory
        self._save_config()

    def _create_widgets(self):
        """UI 위젯 생성"""
        # 헤더
        self.header = ctk.CTkLabel(
            self,
            text="LY/GL 미네 전용 도구",
            font=("맑은 고딕", 20, "bold"),
            text_color="#1e293b",
        )
        self.header.pack(pady=(30, 30))

        # Merge 버튼
        self.btn_merge = ctk.CTkButton(
            self,
            text="🔀 Merge",
            width=250,
            height=44,
            fg_color="#1e293b",
            hover_color="#334155",
            font=("맑은 고딕", 14, "bold"),
            command=self._on_merge_click,
        )
        self.btn_merge.pack(pady=6)

        # Split 버튼
        self.btn_split = ctk.CTkButton(
            self,
            text="🔗 Split",
            width=250,
            height=44,
            fg_color="transparent",
            border_width=2,
            border_color="#1e293b",
            text_color="#1e293b",
            hover_color="#f1f5f9",
            font=("맑은 고딕", 14, "bold"),
            command=self._on_split_click,
        )
        self.btn_split.pack(pady=6)

        # Merge Batches 버튼
        self.btn_merge_batches = ctk.CTkButton(
            self,
            text="📦 Merge Batches",
            width=250,
            height=44,
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            font=("맑은 고딕", 14, "bold"),
            command=self._on_merge_batches_click,
        )
        self.btn_merge_batches.pack(pady=6)

        # Legacy Diff 버튼 (v1.4.0 신규)
        self.btn_legacy_diff = ctk.CTkButton(
            self,
            text="🔍 Legacy Diff",
            width=250,
            height=44,
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            font=("맑은 고딕", 14, "bold"),
            command=self._on_legacy_diff_click,
        )
        self.btn_legacy_diff.pack(pady=6)

        # 진행 상태 레이블 (숨김)
        self.status_label = ctk.CTkLabel(
            self, text="", font=("맑은 고딕", 11), text_color="#64748b"
        )

        # 진행률 바 (숨김)
        self.progress_bar = ctk.CTkProgressBar(self, width=250, height=10)

    def _show_processing_ui(self):
        """처리 중 UI 표시"""
        self.btn_merge.pack_forget()
        self.btn_split.pack_forget()
        self.btn_merge_batches.pack_forget()
        self.btn_legacy_diff.pack_forget()

        # 시작 시간 기록
        self.start_time = time.time()
        self.last_progress = 0
        self.last_progress_time = self.start_time

        self.status_label.pack(pady=(10, 5))
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

    def _show_initial_ui(self):
        """초기 UI 표시"""
        self.status_label.pack_forget()
        self.progress_bar.pack_forget()

        self.btn_merge.pack(pady=6)
        self.btn_split.pack(pady=6)
        self.btn_merge_batches.pack(pady=6)
        self.btn_legacy_diff.pack(pady=6)

    def _on_merge_click(self):
        """Merge 버튼 클릭 핸들러"""
        if self.is_processing:
            return

        # 1. 파일 선택 (Multi-select)
        initial_dir = self._get_last_directory("merge_input")
        file_paths = filedialog.askopenfilenames(
            title="7개 언어 파일 선택",
            initialdir=initial_dir,
            filetypes=[("Excel files", "*.xlsx")],
        )

        if not file_paths:
            return

        # 선택한 디렉토리 저장
        self._save_last_directory("merge_input", str(Path(file_paths[0]).parent))

        # 2. 파일 검증
        try:
            from .validator import validate_language_files, extract_language_code

            paths = [Path(p) for p in file_paths]
            validate_language_files(paths)

            # 언어 코드 및 날짜 추출
            lang_files = {}
            dates = set()
            for path in paths:
                lang_code = extract_language_code(path)
                lang_files[lang_code] = path
                date = extract_date(path)
                if date:
                    dates.add(date)

            # 확인 대화상자
            date_str = list(dates)[0] if dates else "알 수 없음"
            lang_list = "\n".join(
                [f"✓ {lang}.xlsx" for lang in sorted(lang_files.keys())]
            )
            confirm_msg = f"7개 언어 파일을 찾았습니다 ({date_str}):\n\n{lang_list}\n\n하나의 파일로 병합하시겠습니까?"

            if not messagebox.askyesno("병합 확인", confirm_msg):
                return

        except ValidationError as e:
            messagebox.showerror("검증 오류", str(e))
            return

        # 3. 출력 파일 저장 위치 선택
        initial_dir = self._get_last_directory("merge_output")
        today = datetime.now().strftime("%y%m%d")
        default_name = f"{today}_LYGL_StringALL.xlsx"

        output_path = filedialog.asksaveasfilename(
            title="병합 파일 저장",
            initialdir=initial_dir,
            initialfile=default_name,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
        )

        if not output_path:
            return

        # 저장 디렉토리 기록
        self._save_last_directory("merge_output", str(Path(output_path).parent))

        # 4. 병합 수행 (백그라운드 스레드)
        self._perform_merge(lang_files, output_path)

    def _perform_merge(self, lang_files: Dict[str, Path], output_path: str):
        """병합 작업 수행"""
        self.is_processing = True
        self._show_processing_ui()

        def progress_callback(percent: int, message: str):
            """진행률 콜백"""
            self.after(0, self._update_progress, percent, message)

        def merge_thread():
            """병합 스레드"""
            try:
                # 경로를 문자열로 변환
                file_paths = {lang: str(path) for lang, path in lang_files.items()}

                # 병합 수행
                merge_files(file_paths, output_path, progress_callback)

                # 소요 시간 계산
                elapsed_time = time.time() - self.start_time
                time_str = self._format_time(elapsed_time)

                # 성공 메시지
                success_msg = f"출력 파일: {output_path}\n\n소요 시간: {time_str}"
                self.after(0, self._show_success, "병합 완료!", success_msg)

            except Exception as e:
                # 에러 메시지
                self.after(0, self._show_error, "병합 오류", str(e))

            finally:
                self.is_processing = False
                self.after(0, self._show_initial_ui)

        thread = threading.Thread(target=merge_thread, daemon=True)
        thread.start()

    def _on_split_click(self):
        """Split 버튼 클릭 핸들러"""
        if self.is_processing:
            return

        # 1. 병합 파일 선택
        initial_dir = self._get_last_directory("split_input")
        merged_file = filedialog.askopenfilename(
            title="병합 파일 선택",
            initialdir=initial_dir,
            filetypes=[
                ("Excel files", "*_LYGL_StringALL.xlsx"),
                ("All Excel files", "*.xlsx"),
            ],
        )

        if not merged_file:
            return

        # 선택한 디렉토리 저장
        self._save_last_directory("split_input", str(Path(merged_file).parent))

        # 2. 출력 디렉토리 선택
        initial_dir = self._get_last_directory("split_output")
        output_dir = filedialog.askdirectory(
            title="분할 파일 저장 디렉토리 선택", initialdir=initial_dir
        )

        if not output_dir:
            return

        # 저장 디렉토리 기록
        self._save_last_directory("split_output", output_dir)

        # 3. 확인 대화상자
        file_name = Path(merged_file).name
        confirm_msg = (
            f"파일 분할: {file_name}\n"
            f"7개 언어 파일로 분할하시겠습니까?\n\n"
            f"저장 디렉토리: {output_dir}\n"
            f"경고: 기존 파일이 있으면 덮어씁니다."
        )

        if not messagebox.askyesno("분할 확인", confirm_msg):
            return

        # 4. 분할 수행 (백그라운드 스레드)
        self._perform_split(merged_file, output_dir)

    def _perform_split(self, merged_file: str, output_dir: str):
        """분할 작업 수행"""
        self.is_processing = True
        self._show_processing_ui()

        def progress_callback(percent: int, message: str):
            """진행률 콜백"""
            self.after(0, self._update_progress, percent, message)

        def split_thread():
            """분할 스레드"""
            try:
                # 분할 수행
                output_paths = split_file(
                    merged_file, output_dir, progress_callback=progress_callback
                )

                # 소요 시간 계산
                elapsed_time = time.time() - self.start_time
                time_str = self._format_time(elapsed_time)

                # 성공 메시지
                file_list = "\n".join(
                    [f"✓ {Path(p).name}" for p in output_paths.values()]
                )
                success_msg = f"생성된 파일:\n{file_list}\n\n소요 시간: {time_str}"
                self.after(0, self._show_success, "분할 완료!", success_msg)

            except Exception as e:
                # 에러 메시지
                self.after(0, self._show_error, "분할 오류", str(e))

            finally:
                self.is_processing = False
                self.after(0, self._show_initial_ui)

        thread = threading.Thread(target=split_thread, daemon=True)
        thread.start()

    def _on_merge_batches_click(self):
        """Merge Batches 버튼 클릭 핸들러"""
        if self.is_processing:
            return

        # 1. 루트 폴더 선택
        initial_dir = self._get_last_directory("merge_batches_root")
        root_folder = filedialog.askdirectory(
            title="배치 폴더가 있는 루트 폴더 선택",
            initialdir=initial_dir
        )

        if not root_folder:
            return

        # 선택한 디렉토리 저장
        self._save_last_directory("merge_batches_root", root_folder)

        # 2. 배치 폴더 스캔
        try:
            from pathlib import Path
            batch_info = scan_batch_folders(Path(root_folder))

        except BatchMergerError as e:
            messagebox.showerror("배치 스캔 오류", str(e))
            return
        except Exception as e:
            messagebox.showerror("오류", f"배치 폴더 스캔 중 오류가 발생했습니다.\n\n{e}")
            return

        # 3. 배치 선택 UI 표시
        self._show_batch_selection_dialog(root_folder, batch_info)

    def _show_batch_selection_dialog(self, root_folder: str, batch_info: dict):
        """배치 선택 다이얼로그 표시"""

        def on_confirm(selected_batches: list, base_batch: str):
            """확인 버튼 콜백 (v1.4.0: base_batch 추가)"""
            # 선택 검증
            is_valid, error_msg = validate_batch_selection(selected_batches, base_batch, batch_info)

            if not is_valid:
                messagebox.showerror("선택 오류", error_msg)
                # 다이얼로그는 닫히지 않음 (사용자가 다시 선택 가능)
                self._show_batch_selection_dialog(root_folder, batch_info)
                return

            # 병합 수행 (v1.4.0: base_batch 추가)
            self._perform_merge_batches(root_folder, selected_batches, base_batch, batch_info)

        def on_cancel():
            """취소 버튼 콜백"""
            pass  # 창만 닫힘

        # 배치 선택 다이얼로그 생성
        BatchSelectionDialog(self, batch_info, on_confirm, on_cancel)

    def _perform_merge_batches(self, root_folder: str, selected_batches: list, base_batch: str, batch_info: dict):
        """Merge Batches 작업 수행 (v1.4.0: base_batch 추가)"""
        self.is_processing = True
        self._show_processing_ui()

        # 취소 플래그
        self.cancel_requested = False

        def progress_callback(percent: int, message: str):
            """진행률 콜백"""
            self.after(0, self._update_progress, percent, message)

        def cancel_check():
            """취소 확인"""
            return self.cancel_requested

        def overwrite_callback(existing_files: list) -> bool:
            """덮어쓰기 확인 콜백"""
            result = messagebox.askyesno(
                "파일 덮어쓰기 확인",
                f"다음 파일이 이미 존재합니다:\n\n" +
                "\n".join(f"- {f}" for f in existing_files) +
                "\n\n덮어쓰시겠습니까?"
            )
            return result

        def merge_batches_thread():
            """Merge Batches 스레드"""
            try:
                from pathlib import Path

                # 배치 병합 수행 (v1.4.0: base_batch 추가)
                saved_files, log_path = merge_batches(
                    Path(root_folder),
                    selected_batches,
                    base_batch,
                    batch_info,
                    progress_callback,
                    cancel_check,
                    overwrite_callback
                )

                # 소요 시간 계산
                elapsed_time = time.time() - self.start_time
                time_str = self._format_time(elapsed_time)

                # 성공 메시지
                file_list = "\n".join([f"✓ {Path(p).name}" for p in saved_files.values()])
                success_msg = (
                    f"생성된 파일:\n{file_list}\n\n"
                    f"로그 파일: {Path(log_path).name}\n\n"
                    f"소요 시간: {time_str}"
                )
                self.after(0, self._show_success, "Merge Batches 완료!", success_msg)

            except UserCancelledError:
                # 사용자 취소
                self.after(0, self._show_error, "취소됨", "작업이 취소되었습니다.")

            except BatchMergerError as e:
                # 배치 병합 오류
                self.after(0, self._show_error, "Merge Batches 오류", str(e))

            except Exception as e:
                # 기타 오류
                self.after(0, self._show_error, "오류", str(e))

            finally:
                self.is_processing = False
                self.cancel_requested = False
                self.after(0, self._show_initial_ui)

        thread = threading.Thread(target=merge_batches_thread, daemon=True)
        thread.start()

    def _update_progress(self, percent: int, message: str):
        """진행률 업데이트"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # 예상 남은 시간 계산
        if percent > 0 and percent < 100:
            estimated_total_time = elapsed_time / (percent / 100.0)
            remaining_time = estimated_total_time - elapsed_time
            remaining_str = self._format_time(remaining_time)
            status_text = f"{message} ({percent}% 완료, 남은 시간: 약 {remaining_str})"
        elif percent == 100:
            total_time_str = self._format_time(elapsed_time)
            status_text = f"{message} (완료, 소요 시간: {total_time_str})"
        else:
            status_text = f"{message} ({percent}% 완료)"

        self.status_label.configure(text=status_text)
        self.progress_bar.set(percent / 100.0)

        # 진행률 추적 업데이트
        self.last_progress = percent
        self.last_progress_time = current_time

    def _format_time(self, seconds: float) -> str:
        """
        시간을 사람이 읽기 쉬운 형식으로 포맷팅

        Args:
            seconds: 초 단위 시간

        Returns:
            포맷팅된 시간 문자열 (예: "1분 30초", "45초")
        """
        if seconds < 60:
            return f"{int(seconds)}초"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = int(seconds % 60)
            if remaining_seconds > 0:
                return f"{minutes}분 {remaining_seconds}초"
            return f"{minutes}분"
        else:
            hours = int(seconds / 3600)
            remaining_minutes = int((seconds % 3600) / 60)
            if remaining_minutes > 0:
                return f"{hours}시간 {remaining_minutes}분"
            return f"{hours}시간"

    def _show_success(self, title: str, message: str):
        """성공 메시지 표시"""
        messagebox.showinfo(title, message)

    def _show_error(self, title: str, message: str):
        """에러 메시지 표시"""
        messagebox.showerror(title, message)

    # ========== Legacy Diff (v1.4.0) ==========

    def _on_legacy_diff_click(self):
        """Legacy Diff 버튼 클릭 핸들러"""
        if self.is_processing:
            return

        # 1. 비교1 폴더 선택
        initial_dir = self._get_last_directory("legacy_diff_folder1")
        folder1 = filedialog.askdirectory(
            title="비교1 폴더 선택 (이전 버전)",
            initialdir=initial_dir
        )

        if not folder1:
            return

        self._save_last_directory("legacy_diff_folder1", folder1)

        # 2. 비교2 폴더 선택
        initial_dir = self._get_last_directory("legacy_diff_folder2")
        folder2 = filedialog.askdirectory(
            title="비교2 폴더 선택 (현재 버전)",
            initialdir=initial_dir
        )

        if not folder2:
            return

        self._save_last_directory("legacy_diff_folder2", folder2)

        # 3. 출력 파일 위치 선택
        initial_dir = self._get_last_directory("legacy_diff_output")
        output_filename = generate_diff_filename()
        output_path = filedialog.asksaveasfilename(
            title="결과 파일 저장 위치 선택",
            initialdir=initial_dir,
            defaultextension=".xlsx",
            initialfile=output_filename,
            filetypes=[("Excel 파일", "*.xlsx")]
        )

        if not output_path:
            return

        self._save_last_directory("legacy_diff_output", str(Path(output_path).parent))

        # 4. Legacy Diff 수행
        self._perform_legacy_diff(folder1, folder2, output_path)

    def _perform_legacy_diff(self, folder1: str, folder2: str, output_path: str):
        """Legacy Diff 작업 수행"""
        self.is_processing = True
        self._show_processing_ui()

        def progress_callback(percent: int, message: str):
            """진행률 콜백"""
            self.after(0, self._update_progress, percent, message)

        def legacy_diff_thread():
            """Legacy Diff 스레드"""
            try:
                from pathlib import Path

                # Legacy Diff 수행
                result_path, stats = legacy_diff(
                    Path(folder1),
                    Path(folder2),
                    Path(output_path),
                    progress_callback
                )

                # 소요 시간 계산
                elapsed_time = time.time() - self.start_time
                time_str = self._format_time(elapsed_time)

                # 통계 정보 생성
                total_changes = sum(stats.values())
                stats_lines = []
                for lang in ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']:
                    count = stats.get(lang, 0)
                    if count > 0:
                        stats_lines.append(f"  - {lang}: {count}개")

                # 성공 메시지
                success_msg = (
                    f"비교1: {folder1}\n"
                    f"비교2: {folder2}\n\n"
                    f"변경된 KEY: {total_changes}개\n"
                    f"언어별 변경 현황:\n"
                    + "\n".join(stats_lines) + "\n\n"
                    f"출력 파일: {Path(output_path).name}\n\n"
                    f"소요 시간: {time_str}"
                )
                self.after(0, self._show_success, "Legacy Diff 완료!", success_msg)

            except LegacyDiffError as e:
                # Legacy Diff 오류
                self.after(0, self._show_error, "Legacy Diff 오류", str(e))

            except Exception as e:
                # 기타 오류
                self.after(0, self._show_error, "오류", str(e))

            finally:
                self.is_processing = False
                self.after(0, self._show_initial_ui)

        thread = threading.Thread(target=legacy_diff_thread, daemon=True)
        thread.start()


def run_app():
    """앱 실행"""
    app = LYTableApp()
    app.mainloop()
