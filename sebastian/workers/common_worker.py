"""공통 기능 Worker 모듈

공통 기능을 비동기로 처리하는 QThread Worker입니다.
"""

from PyQt6.QtCore import QThread, pyqtSignal
import queue
import logging

logger = logging.getLogger(__name__)


class CommonWorker(QThread):
    """공통 기능 Worker

    공통 기능을 비동기로 처리합니다.
    현재 지원 기능:
        - restore_csv: CSV 따옴표 복원

    Signals:
        progress_updated: 진행률 (0-100)
        status_updated: 상태 메시지
        completed: 완료 메시지
        error_occurred: 에러 메시지

    Examples:
        >>> worker = CommonWorker(
        ...     operation='restore_csv',
        ...     original_path='original.csv',
        ...     export_path='export.csv',
        ...     output_path='restored.csv'
        ... )
        >>> worker.completed.connect(on_completed)
        >>> worker.start()
    """

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        operation: str,
        original_path: str = "",
        export_path: str = "",
        output_path: str = "",
    ):
        """초기화

        Args:
            operation: 작업 종류 ('restore_csv')
            original_path: 원본 파일 경로 (restore_csv용)
            export_path: export 파일 경로 (restore_csv용)
            output_path: 출력 파일 경로 (restore_csv용)
        """
        super().__init__()
        self.operation = operation
        self.original_path = original_path
        self.export_path = export_path
        self.output_path = output_path
        self.progress_queue = queue.Queue()

        logger.info(f"CommonWorker 생성: operation={operation}")

    def run(self):
        """QThread.run 오버라이드

        작업을 실행하고 Signal을 통해 UI에 상태를 전달합니다.
        """
        try:
            logger.info(f"CommonWorker 시작: operation={self.operation}")

            if self.operation == "restore_csv":
                self._restore_csv_quotes()
            else:
                raise ValueError(f"알 수 없는 작업: {self.operation}")

        except Exception as e:
            logger.exception(f"CommonWorker 실패: {e}")
            self.error_occurred.emit(f"작업 실패: {e}")

    def _restore_csv_quotes(self):
        """CSV 따옴표 복원 작업

        원본 CSV와 export CSV를 비교하여 따옴표를 복원합니다.
        """
        from sebastian.core.common.csv_restore import restore_csv_quotes

        # Progress Queue 모니터링 스레드 시작
        import threading

        def monitor_progress():
            while True:
                try:
                    msg_type, msg_value = self.progress_queue.get(timeout=0.1)
                    if msg_type == "progress":
                        self.progress_updated.emit(msg_value)
                    elif msg_type == "status":
                        self.status_updated.emit(msg_value)
                    elif msg_type == "done":
                        break
                except queue.Empty:
                    continue

        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()

        try:
            # Core 로직 호출
            restored_path, report_path = restore_csv_quotes(
                self.original_path, self.export_path, self.output_path, self.progress_queue
            )

            # 완료 신호
            self.progress_queue.put(("done", None))
            monitor_thread.join(timeout=1.0)

            completion_msg = (
                f"✅ CSV 따옴표 복원 완료!\n\n"
                f"📄 복원 파일: {restored_path}\n"
                f"📊 보고서: {report_path}"
            )
            self.completed.emit(completion_msg)

            logger.info("CSV 복원 성공")

        except Exception as e:
            self.progress_queue.put(("done", None))
            monitor_thread.join(timeout=1.0)
            raise
