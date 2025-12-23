"""
LYGL Worker - QThread 기반 비동기 처리

4개 기능: merge, split, batch, diff
"""

from PyQt6.QtCore import QThread, pyqtSignal
import queue

from core.lygl import merge, merge_files, split, split_file


class LYGLMergeWorker(QThread):
    """LY/GL Merge 작업 Worker"""

    # Signals
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_paths: list, output_path: str):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path

    def run(self):
        """작업 실행"""
        try:
            from pathlib import Path
            import datetime

            self.status_updated.emit("7개 언어 파일 병합 시작...")
            self.progress_updated.emit(10)

            # 파일 경로를 딕셔너리로 변환
            language_files = {}
            for file_path in self.file_paths:
                # 파일명에서 언어 코드 추출 (예: 251128_EN.xlsx → EN)
                filename = Path(file_path).stem
                if '_EN' in filename:
                    language_files['EN'] = file_path
                elif '_CT' in filename:
                    language_files['CT'] = file_path
                elif '_CS' in filename:
                    language_files['CS'] = file_path
                elif '_JA' in filename:
                    language_files['JA'] = file_path
                elif '_TH' in filename:
                    language_files['TH'] = file_path
                elif '_PT-BR' in filename:
                    language_files['PT-BR'] = file_path
                elif '_RU' in filename:
                    language_files['RU'] = file_path

            self.progress_updated.emit(30)

            # 출력 파일명 생성
            date_str = datetime.datetime.now().strftime('%y%m%d')
            output_file = Path(self.output_path) / f"{date_str}_LYGL_StringALL.xlsx"

            # merge_files 호출
            merge_files(language_files, str(output_file), progress_callback=self._progress_callback)

            self.progress_updated.emit(100)
            self.completed.emit(f"파일이 {output_file.name}로 저장되었습니다.")

        except Exception as e:
            self.error_occurred.emit(f"Merge 실패: {str(e)}")

    def _progress_callback(self, percent: int, message: str):
        """진행 상황 콜백"""
        self.progress_updated.emit(percent)
        self.status_updated.emit(message)


class LYGLSplitWorker(QThread):
    """LY/GL Split 작업 Worker"""

    # Signals
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, input_file: str, output_folder: str):
        super().__init__()
        self.input_file = input_file
        self.output_folder = output_folder

    def run(self):
        """작업 실행"""
        try:
            from pathlib import Path

            self.status_updated.emit("통합 파일 분할 시작...")
            self.progress_updated.emit(10)

            # 파일명에서 날짜 추출 (예: 251128_LYGL_StringALL.xlsx → 251128)
            filename = Path(self.input_file).stem
            date_prefix = filename.split('_')[0] if '_' in filename else None

            self.progress_updated.emit(30)

            # split_file 호출
            result = split_file(
                self.input_file,
                self.output_folder,
                date_prefix=date_prefix,
                progress_callback=self._progress_callback
            )

            self.progress_updated.emit(100)
            self.completed.emit(f"7개 언어 파일이 생성되었습니다.")

        except Exception as e:
            self.error_occurred.emit(f"Split 실패: {str(e)}")

    def _progress_callback(self, percent: int, message: str):
        """진행 상황 콜백"""
        self.progress_updated.emit(percent)
        self.status_updated.emit(message)


class LYGLBatchWorker(QThread):
    """LY/GL Batch 작업 Worker"""

    # Signals
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, root_folder, selected_batches: list, base_batch: str,
                 batch_info: dict, output_path: str, auto_complete: bool):
        super().__init__()
        self.root_folder = root_folder
        self.selected_batches = selected_batches
        self.base_batch = base_batch
        self.batch_info = batch_info
        self.output_path = output_path
        self.auto_complete = auto_complete

    def run(self):
        """작업 실행"""
        try:
            from pathlib import Path
            from core.lygl.batch_merger import merge_batches

            self.status_updated.emit(f"{len(self.selected_batches)}개 배치 병합 시작...")
            self.progress_updated.emit(5)
            self.status_updated.emit(f"기준 배치: {self.base_batch}")

            # merge_batches 호출 (이미 준비된 batch_info 사용)
            output_files, log_path = merge_batches(
                root_folder=self.root_folder,
                selected_batches=self.selected_batches,
                base_batch=self.base_batch,
                batch_info=self.batch_info,
                progress_callback=self._progress_callback,
                cancel_check=None,
                overwrite_callback=None,
                apply_status_auto_complete=self.auto_complete  # 체크박스 값 전달
            )

            self.progress_updated.emit(100)
            self.completed.emit(f"배치 병합 완료: {len(output_files)}개 파일 생성\n로그: {log_path.name}")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Batch 에러 상세:\n{error_detail}")  # 콘솔 출력
            self.error_occurred.emit(f"Batch 실패: {str(e)}\n\n상세:\n{error_detail}")

    def _progress_callback(self, percent: int, message: str):
        """진행 상황 콜백"""
        self.progress_updated.emit(percent)
        self.status_updated.emit(message)


class LYGLDiffWorker(QThread):
    """LY/GL Diff 작업 Worker"""

    # Signals
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, folder1: str, folder2: str, output_path: str):
        super().__init__()
        self.folder1 = folder1
        self.folder2 = folder2
        self.output_path = output_path

    def run(self):
        """작업 실행"""
        try:
            from pathlib import Path
            import datetime
            from core.lygl.legacy_diff import legacy_diff

            self.status_updated.emit("버전 비교 시작...")
            self.progress_updated.emit(5)

            folder1_path = Path(self.folder1)
            folder2_path = Path(self.folder2)

            # 출력 파일명 생성
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            output_file = Path(self.output_path) / f"{timestamp}_DIFF.xlsx"

            # legacy_diff 호출
            result_path, change_counts = legacy_diff(
                folder1=folder1_path,
                folder2=folder2_path,
                output_path=output_file,
                progress_callback=self._progress_callback
            )

            self.progress_updated.emit(100)

            # 변경 개수 요약
            total_changes = sum(change_counts.values())
            summary = f"비교 완료: {total_changes}개 변경 사항\n"
            summary += "\n".join([f"{lang}: {count}개" for lang, count in change_counts.items() if count > 0])

            self.completed.emit(f"{result_path.name} 생성 완료\n{summary}")

        except Exception as e:
            self.error_occurred.emit(f"Diff 실패: {str(e)}")

    def _progress_callback(self, percent: int, message: str):
        """진행 상황 콜백"""
        self.progress_updated.emit(percent)
        self.status_updated.emit(message)
