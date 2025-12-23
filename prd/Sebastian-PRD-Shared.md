# Sebastian PRD - Shared (공통 요소)

**문서 유형**: Shared
**버전**: 1.0.0
**작성일**: 2025-12-10
**최종 수정일**: 2025-12-10

---

## 📋 이 문서의 역할

이 문서는 Sebastian 프로젝트의 **모든 기능이 공통으로 사용하는 요소**를 정의합니다.

**참조 원칙**:
- Feature 문서(M4GL, NCGL, LYGL)는 이 문서를 **참조만** 합니다
- 공통 요소를 Feature 문서에 **중복 작성 금지**
- 변경 시 이 문서만 수정하면 전체 적용됨

---

## 🔧 기술 스택

### GUI 프레임워크

**선택**: **PyQt6**

**선정 이유**:
1. **네이티브 성능**: C++ 기반 → 빠른 렌더링
2. **풍부한 위젯**: 복잡한 UI 구성 가능
3. **크로스 플랫폼**: Windows 우선, 향후 Mac/Linux 확장 가능
4. **PyInstaller 호환**: 독립 실행 파일 빌드 용이
5. **상용 라이선스**: 상업적 사용 가능 (LGPL)

**레거시와의 차이**:
| 레거시 | Sebastian |
|--------|-----------|
| tkinter (M4/GL, NC/GL) | PyQt6 |
| customtkinter (LY/GL) | PyQt6 |

### Excel 처리

| 라이브러리 | 용도 | 버전 |
|------------|------|------|
| **pandas** | 데이터 분석 및 변환 | >= 2.0.0 |
| **openpyxl** | Excel 읽기 및 서식 지정 | >= 3.1.2 |
| **xlsxwriter** | 고속 Excel 쓰기 (NC/GL) | >= 3.1.0 |

**pandas 사용 이유**:
- DataFrame 기반 병합 → 직관적인 데이터 처리
- 대용량 데이터 최적화 (49,600행+)

**openpyxl 사용 이유**:
- 셀 단위 스타일 지정 가능
- .xlsm (매크로 포함) 파일 읽기 지원

**xlsxwriter 사용 이유**:
- openpyxl 대비 5-10배 빠른 쓰기 속도
- 메모리 효율적 (스트리밍 모드)

### 비동기 처리

**선택**: **QThread** (PyQt6 내장)

**레거시와의 차이**:
| 레거시 | Sebastian |
|--------|-----------|
| threading.Thread (M4/GL) | QThread |
| ProcessPoolExecutor (NC/GL) | QThreadPool |

**QThread 선정 이유**:
1. **GUI 통합**: Qt signal/slot 시스템과 자연스러운 통신
2. **안전성**: UI 스레드와 워커 스레드 분리
3. **디버깅**: PyQt 디버거 호환

**NCGL 병렬 처리**: **QThreadPool** (Round 2 결정)
- 파일 읽기는 I/O 바운드 → GIL 영향 적음
- PyQt 네이티브 통합으로 Signal/Slot 자연스러움
- 예상 성능: ~2-3초 (레거시 ~1.5초 대비 약간 느림, 허용 범위)

### 빌드 및 배포

**PyInstaller**: >= 6.0.0

**빌드 명령어**:
```bash
pyinstaller --onefile --windowed --name Sebastian --icon=sebastian.ico main.py
```

**빌드 옵션 설명**:
- `--onefile`: 단일 .exe 파일 생성
- `--windowed`: 콘솔 창 숨김 (GUI만 표시)
- `--name Sebastian`: 출력 파일명
- `--icon`: 아이콘 지정

---

## 🎨 공통 UI 컴포넌트

### 1. 진행도 Dialog (ProgressDialog)

**목적**: 백그라운드 작업의 실시간 진행 상태 표시

**레거시 참조**: `progress_window.py` (M4/GL, NC/GL 공통 사용)

**UI 레이아웃**: [Sebastian-UI-Wireframes.md#progressdialog](Sebastian-UI-Wireframes.md#progressdialog) 참조

**Signal/Slot 구조** (양방향):

```python
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMutex
import time

class ProgressSignals(QObject):
    """진행도 업데이트 signals (Worker → Dialog)"""
    progress_changed = pyqtSignal(int)        # 진행률 (0-100)
    step_changed = pyqtSignal(int, int)       # (current_step, total_steps)
    file_changed = pyqtSignal(str)            # 현재 파일명
    files_processed = pyqtSignal(int, int)    # (processed, total)
    status_message = pyqtSignal(str)          # 일반 상태 메시지
    completed = pyqtSignal(str)               # 완료 메시지
    error_occurred = pyqtSignal(str)          # 에러 메시지


class BaseWorker(QThread):
    """모든 병합 워커의 기본 클래스 (양방향 Signal)"""

    # Dialog → Worker signal
    cancel_requested = pyqtSignal()  # 취소 요청

    def __init__(self):
        super().__init__()
        self.signals = ProgressSignals()
        self.is_cancelled = False
        self.cancel_mutex = QMutex()

        # 자기 자신의 cancel signal 연결
        self.cancel_requested.connect(self._handle_cancel)

    def _handle_cancel(self):
        """취소 signal 처리 (스레드 안전)"""
        self.cancel_mutex.lock()
        self.is_cancelled = True
        self.cancel_mutex.unlock()

    def update_progress(self, percent=None, current_step=None, total_steps=None,
                       filename=None, files_processed=None, total_files=None,
                       status=None):
        """진행도 통합 업데이트 헬퍼 함수"""
        if percent is not None:
            self.signals.progress_changed.emit(percent)

        if current_step is not None and total_steps is not None:
            self.signals.step_changed.emit(current_step, total_steps)

        if filename is not None:
            self.signals.file_changed.emit(filename)

        if files_processed is not None and total_files is not None:
            self.signals.files_processed.emit(files_processed, total_files)

        if status is not None:
            self.signals.status_message.emit(status)

    def run(self):
        """서브클래스에서 구현 필요"""
        raise NotImplementedError("run() 메서드를 구현해야 합니다")
```

**남은 시간 계산 알고리즘**:
```python
def calculate_remaining_time(self, progress_percent):
    """레거시 알고리즘 유지 (단순 비례식 + 평활화)"""
    elapsed = time.time() - self.start_time
    if progress_percent > 0 and progress_percent < 100:
        rate = elapsed / progress_percent
        remaining = (100 - progress_percent) * rate

        # 이동 평균으로 급격한 변동 방지
        if hasattr(self, 'last_estimate'):
            remaining = (remaining + self.last_estimate) / 2

        self.last_estimate = remaining
        return remaining
    return 0
```

**ProgressDialog 구현**:
```python
class ProgressDialog(QDialog):
    """공통 진행도 Dialog (양방향 Signal/Slot)"""

    def __init__(self, parent=None, title="처리 중", theme_color="#4CAF50"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 300)

        # UI 요소
        self.step_label = QLabel("대기 중...")
        self.file_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.time_label = QLabel("남은 시간: 계산 중...")
        self.files_label = QLabel("처리된 파일: 0/0")
        self.cancel_button = QPushButton("취소")
        self.minimize_button = QPushButton("최소화")

        # 레이아웃 구성
        layout = QVBoxLayout()
        layout.addWidget(self.step_label)
        layout.addWidget(self.file_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.time_label)
        layout.addWidget(self.files_label)

        # 버튼 레이아웃 (수평, 우측 정렬)
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 왼쪽 공간
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.minimize_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.worker = None
        self.start_time = None
        self.last_estimate = None

    def connect_worker(self, worker: BaseWorker):
        """워커의 signals 연결 (양방향)"""
        self.worker = worker
        self.start_time = time.time()

        # Worker → Dialog signals
        worker.signals.progress_changed.connect(self._on_progress)
        worker.signals.step_changed.connect(self._on_step)
        worker.signals.file_changed.connect(self._on_file)
        worker.signals.files_processed.connect(self._on_files)
        worker.signals.status_message.connect(self._on_status)
        worker.signals.completed.connect(self._on_completed)
        worker.signals.error_occurred.connect(self._on_error)

        # Dialog → Worker signal (양방향!)
        self.cancel_button.clicked.connect(worker.cancel_requested.emit)

    def _on_progress(self, percent):
        """진행률 업데이트 + 남은 시간 계산"""
        self.progress_bar.setValue(percent)
        remaining = self.calculate_remaining_time(percent)
        if remaining > 60:
            minutes = int(remaining / 60)
            seconds = int(remaining % 60)
            self.time_label.setText(f"남은 시간: 약 {minutes}분 {seconds}초")
        else:
            self.time_label.setText(f"남은 시간: 약 {int(remaining)}초")

    def _on_step(self, current, total):
        """단계 업데이트"""
        self.step_label.setText(f"단계: {current}/{total}")

    def _on_file(self, filename):
        """파일명 업데이트"""
        self.file_label.setText(f"처리 중: {filename}")

    def _on_files(self, processed, total):
        """파일 카운터 업데이트"""
        self.files_label.setText(f"처리된 파일: {processed}/{total}")

    def _on_status(self, message):
        """상태 메시지 업데이트"""
        # 추가 상태 라벨에 표시 (선택 사항)
        pass

    def _on_completed(self, message):
        """완료 처리"""
        QMessageBox.information(self, "완료", message)
        self.close()

    def _on_error(self, error_msg):
        """에러 처리"""
        QMessageBox.critical(self, "오류", error_msg)
        self.close()

    def calculate_remaining_time(self, progress_percent):
        """남은 시간 계산 (레거시 알고리즘 유지)"""
        elapsed = time.time() - self.start_time
        if progress_percent > 0 and progress_percent < 100:
            rate = elapsed / progress_percent
            remaining = (100 - progress_percent) * rate

            # 이동 평균으로 급격한 변동 방지
            if self.last_estimate is not None:
                remaining = (remaining + self.last_estimate) / 2

            self.last_estimate = remaining
            return remaining
        return 0
```

**사용 예시**:
```python
# M4/GL DIALOGUE 워커
class M4GLDialogueWorker(BaseWorker):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        try:
            # 헬퍼 함수 사용 - 간결!
            self.update_progress(
                percent=20,
                current_step=1,
                total_steps=3,
                filename="CINEMATIC_DIALOGUE.xlsm",
                files_processed=1,
                total_files=3
            )

            # 또는 부분 업데이트
            self.update_progress(percent=50)

            # 취소 확인
            if self.is_cancelled:
                return

            # ...

            self.signals.completed.emit("파일이 저장되었습니다.")

        except Exception as e:
            self.signals.error_occurred.emit(str(e))

# 메인 창에서 사용
worker = M4GLDialogueWorker(folder)
progress_dialog = ProgressDialog(self, "M4 DIALOGUE 병합 중")
progress_dialog.connect_worker(worker)
worker.start()
progress_dialog.exec()  # 모달로 표시
```

---

### 2. 파일 선택 Dialog (FileSelectionDialog)

**목적**: 일관된 파일/폴더 선택 UI 제공

**PyQt6 구현**:
```python
class FileSelectionDialog:
    @staticmethod
    def select_files(parent, title="파일 선택", filters="Excel files (*.xlsx *.xlsm)", multiple=False):
        """파일 선택 다이얼로그"""
        if multiple:
            files, _ = QFileDialog.getOpenFileNames(parent, title, "", filters)
            return files
        else:
            file, _ = QFileDialog.getOpenFileName(parent, title, "", filters)
            return file

    @staticmethod
    def select_folder(parent, title="폴더 선택"):
        """폴더 선택 다이얼로그"""
        folder = QFileDialog.getExistingDirectory(parent, title)
        return folder

    @staticmethod
    def save_file(parent, title="저장", default_name="", filters="Excel files (*.xlsx)"):
        """파일 저장 다이얼로그"""
        file, _ = QFileDialog.getSaveFileName(parent, title, default_name, filters)
        return file
```

**사용 예시**:
```python
# 단일 파일 선택 (M4/GL DIALOGUE)
folder = FileSelectionDialog.select_folder(self, "대화 파일 폴더 선택")

# 복수 파일 선택 (LY/GL Merge)
files = FileSelectionDialog.select_files(
    self,
    "언어별 파일 선택 (7개)",
    "Excel files (*.xlsx)",
    multiple=True
)

# 저장 위치 선택
output_file = FileSelectionDialog.save_file(
    self,
    "저장",
    "250512_MIR4_MASTER_DIALOGUE.xlsx",
    "Excel files (*.xlsx)"
)
```

---

### 3. 에러/로그 뷰어 (LogViewerWidget)

**목적**: 실행 로그 및 에러 메시지 실시간 표시

**UI 레이아웃**: [Sebastian-UI-Wireframes.md#logviewer](Sebastian-UI-Wireframes.md#logviewer) 참조

**PyQt6 구현**:
```python
class LogViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 탭 위젯
        self.tab_widget = QTabWidget()

        # 로그 텍스트 에디터 (읽기 전용)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)  # 최대 1000줄 (초과 시 오래된 로그 자동 삭제)

        self.error_text = QPlainTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setStyleSheet("background-color: #502020;")  # 어두운 빨강

        self.warning_text = QPlainTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setStyleSheet("background-color: #504020;")  # 어두운 노랑

        # 탭 추가
        self.tab_widget.addTab(self.log_text, "로그")
        self.tab_widget.addTab(self.error_text, "에러")
        self.tab_widget.addTab(self.warning_text, "경고")
```

**메시지 추가 메서드** (클래스 내부):
```python
class LogViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 탭 위젯
        self.tab_widget = QTabWidget()

        # 로그 텍스트 에디터 (읽기 전용)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)

        self.error_text = QPlainTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setStyleSheet("background-color: #502020;")

        self.warning_text = QPlainTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setStyleSheet("background-color: #504020;")

        # 탭 추가
        self.tab_widget.addTab(self.log_text, "로그")
        self.tab_widget.addTab(self.error_text, "에러")
        self.tab_widget.addTab(self.warning_text, "경고")

    def add_log(self, message):
        """일반 로그 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")

    def add_error(self, message):
        """에러 메시지 추가 (에러 탭으로 자동 전환)"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.error_text.appendPlainText(f"[{timestamp}] ❌ {message}")
        self.tab_widget.setCurrentIndex(1)  # 에러 탭으로 전환

    def add_warning(self, message):
        """경고 메시지 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.warning_text.appendPlainText(f"[{timestamp}] ⚠️ {message}")

    def clear_all(self):
        """모든 로그 지우기"""
        self.log_text.clear()
        self.error_text.clear()
        self.warning_text.clear()
```

---

## 📦 공통 데이터 구조

### Excel 파일 메타데이터

**목적**: 모든 기능에서 사용하는 파일 정보 표준화

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ExcelFileInfo:
    """Excel 파일 메타데이터"""
    path: str                    # 절대 경로
    filename: str                # 파일명 (확장자 포함)
    size_bytes: int              # 파일 크기 (바이트)
    sheet_names: List[str]       # 시트명 목록
    row_count: Optional[int]     # 행 개수 (로드 후)
    col_count: Optional[int]     # 열 개수 (로드 후)

    def is_valid(self) -> bool:
        """파일 유효성 검증"""
        import os
        return os.path.exists(self.path) and self.size_bytes > 0

    def get_size_mb(self) -> float:
        """MB 단위 크기 반환"""
        return self.size_bytes / (1024 * 1024)
```

**사용 예시**:
```python
# 파일 정보 수집
file_info = ExcelFileInfo(
    path="/path/to/file.xlsx",
    filename="CINEMATIC_DIALOGUE.xlsm",
    size_bytes=os.path.getsize(path),
    sheet_names=openpyxl.load_workbook(path).sheetnames,
    row_count=None,  # 아직 로드 전
    col_count=None
)

if not file_info.is_valid():
    raise FileNotFoundError(f"유효하지 않은 파일: {file_info.filename}")
```

---

### 처리 결과 데이터

**목적**: 병합/분할 작업 결과 표준화

```python
@dataclass
class ProcessingResult:
    """작업 처리 결과"""
    success: bool                # 성공 여부
    output_file: Optional[str]   # 출력 파일 경로
    input_files: List[str]       # 입력 파일 목록
    rows_processed: int          # 처리된 행 수
    elapsed_seconds: float       # 소요 시간 (초)
    error_message: Optional[str] # 에러 메시지 (실패 시)
    warnings: List[str]          # 경고 메시지 목록

    def get_summary(self) -> str:
        """결과 요약 문자열"""
        if self.success:
            return (f"✅ 성공: {self.rows_processed}행 처리 완료\n"
                   f"   출력: {os.path.basename(self.output_file)}\n"
                   f"   소요 시간: {self.elapsed_seconds:.2f}초")
        else:
            return f"❌ 실패: {self.error_message}"
```

---

## 📖 용어집

### 게임 프로젝트

| 용어 | 전체 명칭 | 설명 |
|------|-----------|------|
| **M4/GL** | 미르4 글로벌 | 위메이드 퍼블리싱 MMORPG |
| **NC/GL** | 나이트크로우 글로벌 | 위메이드 퍼블리싱 MMORPG |
| **LY/GL** | 레전드 오브 이미르 글로벌 | 위메이드 퍼블리싱 MMORPG |

### 현지화(L10n) 용어

| 용어 | 영문 | 설명 |
|------|------|------|
| **L10n** | Localization | 현지화 (Localization의 약어: L + 10글자 + n) |
| **번역 테이블** | Translation Table | 게임 내 모든 텍스트를 관리하는 Excel 파일 |
| **소스(Source)** | Source | 원문 (보통 한국어) |
| **타겟(Target)** | Target | 번역문 (각 언어별) |
| **KEY** | Key | 문자열 고유 식별자 |
| **String ID** | String ID | M4/GL에서 사용하는 KEY 이름 |
| **Status** | Status | 번역 상태 (신규, 기존, 수정, 완료 등) |

### 언어 코드

| 코드 | 언어 | 영문명 |
|------|------|--------|
| **KO** | 한국어 | Korean |
| **EN** | 영어 | English |
| **CT** | 중국어 번체 | Traditional Chinese |
| **CS** | 중국어 간체 | Simplified Chinese |
| **JA** | 일본어 | Japanese |
| **TH** | 태국어 | Thai |
| **ES** / **ES-LATAM** | 스페인어 (라틴아메리카) | Spanish (Latin America) |
| **PT** / **PT-BR** | 포르투갈어 (브라질) | Portuguese (Brazil) |
| **RU** | 러시아어 | Russian |

### 작업 용어

| 용어 | 설명 | 사용 예 |
|------|------|---------|
| **병합(Merge)** | 여러 파일을 하나로 통합 | 7개 언어 파일 → 1개 통합 파일 |
| **분할(Split)** | 하나의 파일을 여러 파일로 분리 | 1개 통합 파일 → 7개 언어 파일 |
| **배치(Batch)** | 작업 단위 (보통 업데이트 차수) | Batch 1, Batch 2, Batch 3 |
| **마일스톤(Milestone)** | 개발 단계 | M15 = 15번째 마일스톤 |
| **Round-trip** | 병합 → 분할 → 원본 일치 | 데이터 무결성 검증 방법 |
| **NPC** | Non-Player Character | 게임 내 AI 캐릭터 |
| **DIALOGUE** | 대화 | 캐릭터 간 대화 데이터 |
| **STRING** | 문자열 | UI, 메시지 등 모든 텍스트 |

---

## ⚙️ 공통 설정 관리

### 설정 파일 형식

**PyQt6 구현**: `QSettings` 사용 (플랫폼별 자동 저장)

**저장 위치** (플랫폼별):
- **Windows**: 레지스트리 `HKEY_CURRENT_USER\Software\Sebastian\L10nTool`
- **macOS**: `~/Library/Preferences/com.Sebastian.L10nTool.plist`
- **Linux**: `~/.config/Sebastian/L10nTool.conf`

```python
from PyQt6.QtCore import QSettings

class SettingsManager:
    def __init__(self):
        self.settings = QSettings("Sebastian", "L10nTool")

    def get(self, key, default=None):
        """설정 값 가져오기"""
        return self.settings.value(key, default)

    def set(self, key, value):
        """설정 값 저장 (메모리에만, 종료 시 자동 저장)"""
        self.settings.setValue(key, value)
        # sync() 호출 안 함 → 프로그램 정상 종료 시 자동 저장
        # 참고: 비정상 종료 시 설정 손실 가능 (PyQt6 QSettings 기본 동작)

    def get_recent_folder(self, project):
        """최근 사용 폴더 (프로젝트별)"""
        return self.get(f"recent_folder/{project}", "")

    def set_recent_folder(self, project, folder):
        """최근 사용 폴더 저장"""
        self.set(f"recent_folder/{project}", folder)
```

### 저장되는 설정 항목

| 키 | 설명 | 예시 값 |
|-----|------|---------|
| `recent_folder/M4GL` | M4/GL 최근 폴더 | `C:\Work\M4\2025-05` |
| `recent_folder/NCGL` | NC/GL 최근 폴더 | `C:\Work\NC\Batch15` |
| `recent_folder/LYGL` | LY/GL 최근 폴더 | `C:\Work\LY\251128` |
| `window/geometry` | 창 위치/크기 | `800,600,100,100` |
| `window/maximized` | 창 최대화 상태 | `true` |
| `theme` | UI 테마 | `light` / `dark` |
| `log_level` | 로그 레벨 | `INFO` / `DEBUG` |

---

## 🛡️ 공통 에러 처리

### 에러 계층 구조

```python
class SebastianError(Exception):
    """Sebastian 프로젝트 기본 예외"""
    pass

class FileValidationError(SebastianError):
    """파일 검증 실패"""
    pass

class DataIntegrityError(SebastianError):
    """데이터 무결성 오류 (KEY 불일치, 필드 불일치 등)"""
    pass

class ExcelProcessingError(SebastianError):
    """Excel 처리 오류"""
    pass

class UserCancelledException(SebastianError):
    """사용자가 작업 취소"""
    pass
```

### 에러 메시지 포맷

**원칙**: 사용자가 이해하기 쉽고, 해결 방법을 포함

**레거시 유지 항목**:
- "파일을 찾을 수 없습니다: {path}" (M4/GL)
- "유효한 값이 아닙니다." (NC/GL 날짜/마일스톤)
- "KEY가 일치하지 않습니다: {key}" (LY/GL)

**개선 항목**:
```python
# 기존 (모호함)
"올바른 폴더가 아닙니다."

# 개선 (구체적)
"필수 파일이 없습니다:\n- StringEnglish.xlsx\n- StringJapanese.xlsx\n\n선택한 폴더: {folder_path}"
```

### 공통 검증 함수

```python
class Validator:
    @staticmethod
    def validate_file_exists(path: str, file_description: str = "파일") -> None:
        """파일 존재 확인"""
        if not os.path.exists(path):
            raise FileValidationError(f"{file_description}을 찾을 수 없습니다: {path}")

    @staticmethod
    def validate_excel_file(path: str) -> None:
        """Excel 파일 유효성 검증"""
        Validator.validate_file_exists(path, "Excel 파일")

        # 확장자 확인
        ext = os.path.splitext(path)[1].lower()
        if ext not in ['.xlsx', '.xlsm', '.xls']:
            raise FileValidationError(f"지원하지 않는 파일 형식: {ext}\n(.xlsx, .xlsm, .xls만 가능)")

        # 파일 크기 확인 (50MB 제한 - LYGL 대용량 고려)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > 50:
            raise FileValidationError(f"파일 크기가 너무 큽니다: {size_mb:.2f}MB\n(최대 50MB)")

        # openpyxl로 열기 시도
        try:
            import openpyxl
            openpyxl.load_workbook(path, data_only=True)
        except Exception as e:
            raise ExcelProcessingError(f"Excel 파일을 열 수 없습니다: {str(e)}")

    @staticmethod
    def validate_yymmdd(date_str: str) -> bool:
        """YYMMDD 형식 검증 (NC/GL)"""
        if not date_str or not date_str.isdigit() or len(date_str) != 6:
            return False

        # 실제 날짜인지 확인
        try:
            year = int("20" + date_str[:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            datetime(year, month, day)  # 유효한 날짜인지 검증
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_required_files(folder: str, required_files: List[str]) -> None:
        """필수 파일 존재 확인

        Args:
            folder: 검색할 폴더 경로
            required_files: 필수 파일명 리스트

        Raises:
            FileValidationError: 누락된 파일이 있을 때

        Examples:
            # M4GL DIALOGUE 검증
            validate_required_files(
                folder="/path/to/folder",
                required_files=[
                    "CINEMATIC_DIALOGUE.xlsm",
                    "SMALLTALK_DIALOGUE.xlsm",
                    "NPC.xlsm"
                ]
            )

            # NC/GL 검증
            validate_required_files(
                folder="/path/to/folder",
                required_files=[
                    "StringEnglish.xlsx",
                    "StringTraditionalChinese.xlsx",
                    "StringSimplifiedChinese.xlsx",
                    "StringJapanese.xlsx",
                    "StringThai.xlsx",
                    "StringSpanish.xlsx",
                    "StringPortuguese.xlsx",
                    "StringRussian.xlsx"
                ]
            )
        """
        missing = []
        for filename in required_files:
            path = os.path.join(folder, filename)
            if not os.path.exists(path):
                missing.append(filename)

        if missing:
            raise FileValidationError(
                f"필수 파일이 없습니다:\n"
                f"- 누락된 파일: {', '.join(missing)}\n"
                f"- 선택한 폴더: {folder}"
            )
```

---

## 🎨 공통 UI 스타일

**상세 스타일 가이드**: [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md) 참조

와이어프레임 문서에서 다음 항목 확인:
- 색상 시스템 (프로젝트별 Primary, 공통 색상, 상태별 배경)
- 타이포그래피 (폰트, 스케일)
- 간격 시스템 (Spacing, Border Radius)
- PyQt6 구현 가이드 (스타일시트 예시, 색상 상수)

### 아이콘 리소스

**애플리케이션 아이콘**:
- **파일**: `Sebastian.ico` (프로젝트 루트)
- **용도**:
  - Windows 실행 파일(.exe) 아이콘
  - 작업 표시줄 아이콘
  - Alt+Tab 전환 시 표시 아이콘
- **PyInstaller 빌드 시 사용**:
  ```bash
  pyinstaller --onefile --windowed --name Sebastian --icon=Sebastian.ico main.py
  ```

**UI 아이콘** (선택적):
- `folder.png` - 폴더 아이콘 (없으면 Qt 기본 아이콘 사용)
- `file.png` - 파일 아이콘 (없으면 Qt 기본 아이콘 사용)
- `success.png` - 성공 아이콘 (없으면 텍스트로 대체)
- `error.png` - 에러 아이콘 (없으면 텍스트로 대체)

**위치**: `resources/icons/` (선택적, 개발자가 제공)

---

## 📝 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0.0 | 2025-12-10 | 초안 작성 | 재경 |
| 1.1.0 | 2025-12-11 | 파일 크기 제한 50MB로 통일, sync() 정책 주석 추가, LogViewer 1000줄 동작 명시, Sebastian.ico 아이콘 명시 | 재경 |
| 1.2.0 | 2025-12-11 | 검수 반영: validate_required_files() 함수 추가 (필수 파일 존재 확인 통합) | 재경 |
| 1.3.0 | 2025-12-12 | UI 레이아웃/스타일 정보 와이어프레임 문서 참조로 변경 (중복 제거) | 재경 |

---

**참조 문서**:
- [Master 문서](Sebastian-PRD-Master.md)
- [M4GL 기능 문서](Sebastian-PRD-M4GL.md)
- [NCGL 기능 문서](Sebastian-PRD-NCGL.md)
- [LYGL 기능 문서](Sebastian-PRD-LYGL.md)
