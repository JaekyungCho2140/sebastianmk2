"""
NCGL Worker - QThread 기반 비동기 처리

레거시 인터페이스 유지: progress_queue
"""

from PyQt6.QtCore import QThread, pyqtSignal
import queue

from core.ncgl import merge_ncgl


class NCGLWorker(QThread):
    """NC/GL 병합 작업 Worker"""

    # Signals
    progress_updated = pyqtSignal(int)  # 0-100
    status_updated = pyqtSignal(str)  # 상태 메시지
    step_updated = pyqtSignal(str)  # 단계 정보
    file_updated = pyqtSignal(str)  # 처리 중 파일
    files_count_updated = pyqtSignal(int)  # 처리된 파일 수
    completed = pyqtSignal(str)  # 완료 메시지
    error_occurred = pyqtSignal(str)  # 에러 메시지

    def __init__(self, folder_path: str, date: str, milestone: str):
        super().__init__()
        self.folder_path = folder_path
        self.date = date
        self.milestone = milestone
        self.progress_queue = queue.Queue()

    def run(self):
        """작업 실행"""
        import threading
        import time

        try:
            # 작업 함수를 별도 스레드에서 실행
            work_thread = threading.Thread(target=self._do_work)
            work_thread.start()

            # Queue를 실시간으로 폴링
            while work_thread.is_alive():
                self._process_queue()
                time.sleep(0.1)  # 100ms마다 확인

            # 작업 완료 후 마지막으로 한 번 더 처리
            self._process_queue()

        except Exception as e:
            self.error_occurred.emit(f"작업 실패: {str(e)}")

    def _do_work(self):
        """실제 병합 작업 수행"""
        try:
            merge_ncgl(self.folder_path, self.date, self.milestone, self.progress_queue)
        except Exception as e:
            self.progress_queue.put(("error", str(e)))

    def _process_queue(self):
        """Queue 메시지 처리 및 Signal 발송"""
        while not self.progress_queue.empty():
            try:
                msg = self.progress_queue.get_nowait()

                # 메시지 타입별 처리
                if isinstance(msg, int):
                    # 진행률
                    self.progress_updated.emit(msg)

                elif isinstance(msg, str):
                    if msg.startswith("단계:"):
                        # 단계 정보
                        self.step_updated.emit(msg.replace("단계:", ""))
                    elif msg.startswith("파일:"):
                        # 처리 중 파일
                        self.file_updated.emit(msg.replace("파일:", ""))
                    elif msg.startswith("처리된 파일:"):
                        # 처리된 파일 수
                        count = int(msg.replace("처리된 파일:", ""))
                        self.files_count_updated.emit(count)
                    elif msg.startswith("완료:"):
                        # 완료 메시지
                        self.completed.emit(msg.replace("완료:", ""))
                    else:
                        # 일반 상태 메시지
                        self.status_updated.emit(msg)

                elif isinstance(msg, tuple) and msg[0] == "error":
                    # 에러 메시지
                    self.error_occurred.emit(msg[1])

            except queue.Empty:
                break
