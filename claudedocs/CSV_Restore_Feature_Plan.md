# CSV 따옴표 복원 기능 구현 계획

**작성일**: 2025-12-26
**대상 프로젝트**: Sebastian v0.2.0
**기능 코드명**: Common/CSV-Restore
**우선순위**: Medium

---

## 📋 목차

1. [개요](#개요)
2. [요구사항 정리](#요구사항-정리)
3. [아키텍처 설계](#아키텍처-설계)
4. [상세 설계](#상세-설계)
5. [파일 구조](#파일-구조)
6. [구현 단계](#구현-단계)
7. [테스트 계획](#테스트-계획)
8. [검증 기준](#검증-기준)

---

## 개요

### 배경

L10n 팀에서 사용하는 memoQ 도구는 RFC 4180 규격에 맞지 않는 CSV 파일을 자동으로 정규화(Truncate)하는 기능이 있으며, 이 기능을 비활성화할 수 없습니다. 이로 인해 다음과 같은 문제가 발생합니다:

1. **따옴표 누락**: 원본에 있던 필드 따옴표가 export 후 사라짐
2. **따옴표 불필요 추가**: HTML 태그 내 따옴표가 이중으로 변환됨 (`"` → `""`)

### 목적

memoQ에서 export한 CSV 파일을 원본 파일과 비교하여, 원본의 따옴표 패턴을 그대로 복원합니다.

### 범위

- **새 탭 추가**: "공통" 탭 (M4/GL, NC/GL, LY/GL 외)
- **새 기능**: "CSV 따옴표 복원 (Restore Quotes)"
- **UI 스타일**: LY/GL과 동일한 수직 리스트 레이아웃

---

## 요구사항 정리

### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-01 | 원본 CSV 파일 1개 + memoQ export CSV 파일 1개를 입력받음 | 필수 |
| FR-02 | key-name 컬럼(첫 번째 컬럼)을 기준으로 행 매칭 | 필수 |
| FR-03 | 원본의 따옴표 패턴을 그대로 복원 | 필수 |
| FR-04 | 복원된 파일을 `_restored.csv` 접미사로 저장 | 필수 |
| FR-05 | 차이점 보고서를 `.xlsx` 형식으로 생성 (원본/export/복원 비교) | 필수 |
| FR-06 | 컬럼 수 불일치 시 오류 표시 및 중단 | 필수 |
| FR-07 | 헤더/key-name 불일치 시 경고 표시 및 중단 | 필수 |

### UI/UX 요구사항

| ID | 요구사항 | 설명 |
|----|----------|------|
| UI-01 | "공통" 탭 추가 | M4/GL, NC/GL, LY/GL 탭 옆에 추가 |
| UI-02 | LY/GL과 동일한 수직 리스트 레이아웃 | 64px 높이 버튼, 12px 간격 |
| UI-03 | 단일 페이지 Wizard | 모든 설정을 한 화면에서 입력 |
| UI-04 | 버튼 이름: "CSV 따옴표 복원" | 부제: "memoQ export 파일의 따옴표 복원" |

### 비기능 요구사항

| ID | 요구사항 | 기준 |
|----|----------|------|
| NF-01 | 성능 | 10,000행 파일 처리 시간 < 5초 |
| NF-02 | 안정성 | 에러 발생 시 원본 파일 손상 없음 |
| NF-03 | 확장성 | 향후 다른 CSV 관련 기능 추가 용이 |

---

## 아키텍처 설계

### 3계층 구조 준수

```
┌─────────────────────────────────────────┐
│         UI Layer (PyQt6 v2)              │
│  - CommonTab (새 탭)                     │
│  - RestoreCSVWizard (단일 페이지)        │
└──────────────┬──────────────────────────┘
               │ Signal/Slot
               ▼
┌─────────────────────────────────────────┐
│      Worker Layer (QThread)              │
│  - CommonWorker                          │
│    - restore_csv_quotes() 작업           │
└──────────────┬──────────────────────────┘
               │ progress_queue
               ▼
┌─────────────────────────────────────────┐
│       Core Layer (Business Logic)        │
│  - core/common/csv_restore.py            │
│    - restore_csv_quotes()                │
│    - generate_diff_report()              │
│  - core/common/csv_validator.py          │
│    - validate_csv_structure()            │
└─────────────────────────────────────────┘
```

### Signal/Slot 정의

**CommonWorker Signals**:
```python
progress_updated = pyqtSignal(int)        # 0-100 진행률
status_updated = pyqtSignal(str)          # 상태 메시지
completed = pyqtSignal(str)               # 완료 메시지
error_occurred = pyqtSignal(str)          # 에러 메시지
```

**CommonTab Signals**:
```python
restore_csv_requested = pyqtSignal()      # CSV 복원 요청
```

---

## 상세 설계

### 1. Core Layer (core/common/)

#### 1.1. csv_validator.py

**목적**: CSV 파일 구조 검증

```python
from typing import Tuple, List
import pandas as pd

class CSVValidationError(Exception):
    """CSV 검증 에러"""
    pass

def validate_csv_structure(
    original_path: str,
    export_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """CSV 파일 구조 검증

    Args:
        original_path: 원본 CSV 파일 경로
        export_path: memoQ export CSV 파일 경로

    Returns:
        (원본 DataFrame, export DataFrame, 경고 메시지 리스트)

    Raises:
        CSVValidationError: 검증 실패 시
        - 컬럼 수 불일치
        - 헤더 불일치
        - key-name 불일치
    """
```

**검증 항목**:
1. ✅ 파일 존재 여부
2. ✅ CSV 파싱 가능 여부
3. ✅ 컬럼 수 일치 (불일치 시 예외 발생)
4. ✅ 헤더 일치 (불일치 시 경고 + 예외)
5. ✅ key-name 컬럼(첫 번째) 존재
6. ✅ key-name 값 일치 (export에만 있거나 원본에만 있으면 경고 + 예외)

#### 1.2. csv_restore.py

**목적**: CSV 따옴표 복원 및 보고서 생성

```python
from typing import Tuple, Dict
import pandas as pd
from pathlib import Path
import queue

def restore_csv_quotes(
    original_path: str,
    export_path: str,
    output_path: str,
    progress_queue: queue.Queue
) -> Tuple[str, str]:
    """CSV 따옴표 복원

    Args:
        original_path: 원본 CSV 파일 경로
        export_path: memoQ export CSV 파일 경로
        output_path: 복원 파일 저장 경로 (_restored.csv)
        progress_queue: 진행 상황 Queue

    Returns:
        (복원 파일 경로, 보고서 파일 경로)

    Raises:
        CSVValidationError: 검증 실패 시
        IOError: 파일 I/O 실패 시
    """
```

**알고리즘**:
1. **검증**: `validate_csv_structure()` 호출
2. **key-name 기준 매칭**: 딕셔너리 생성 `{key_name: row_index}`
3. **필드별 복원**:
   ```python
   for col in columns:
       original_field = original_df.at[orig_idx, col]
       export_field = export_df.at[exp_idx, col]

       # 원본 따옴표 패턴 복원
       if has_quotes(original_field):
           restored_field = add_quotes(export_field_content)
       else:
           restored_field = remove_quotes(export_field_content)
   ```
4. **파일 저장**: `_restored.csv` 생성
5. **보고서 생성**: `generate_diff_report()` 호출

```python
def generate_diff_report(
    original_df: pd.DataFrame,
    export_df: pd.DataFrame,
    restored_df: pd.DataFrame,
    output_path: str
) -> str:
    """차이점 보고서 생성 (Excel)

    Args:
        original_df: 원본 DataFrame
        export_df: export DataFrame
        restored_df: 복원 DataFrame
        output_path: 보고서 저장 경로 (_diff_report.xlsx)

    Returns:
        보고서 파일 경로
    """
```

**보고서 구조** (Excel 3개 시트):
- **Sheet 1: Summary**
  - 총 행 수
  - 복원된 필드 수
  - 경고 수
  - 오류 수

- **Sheet 2: Restored Fields**
  | key-name | Column | Original | Export | Restored | Status |
  |----------|--------|----------|--------|----------|--------|
  | key1 | ko | "텍스트" | 텍스트 | "텍스트" | ✅ 복원 |

- **Sheet 3: Warnings**
  | Type | key-name | Message |
  |------|----------|---------|
  | Header Mismatch | - | 헤더가 다릅니다 |

---

### 2. Worker Layer (workers/common_worker.py)

```python
from PyQt6.QtCore import QThread, pyqtSignal
import queue

class CommonWorker(QThread):
    """공통 기능 Worker

    Signals:
        progress_updated: 진행률 (0-100)
        status_updated: 상태 메시지
        completed: 완료 메시지
        error_occurred: 에러 메시지
    """

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        operation: str,  # 'restore_csv'
        original_path: str,
        export_path: str,
        output_path: str
    ):
        super().__init__()
        self.operation = operation
        self.original_path = original_path
        self.export_path = export_path
        self.output_path = output_path
        self.progress_queue = queue.Queue()

    def run(self):
        """QThread.run 오버라이드"""
        try:
            if self.operation == 'restore_csv':
                self._restore_csv_quotes()
        except Exception as e:
            self.error_occurred.emit(f"실패: {e}")

    def _restore_csv_quotes(self):
        """CSV 따옴표 복원 작업"""
        from sebastian.core.common.csv_restore import restore_csv_quotes

        restored_path, report_path = restore_csv_quotes(
            self.original_path,
            self.export_path,
            self.output_path,
            self.progress_queue
        )

        self.completed.emit(
            f"복원 완료!\n"
            f"복원 파일: {restored_path}\n"
            f"보고서: {report_path}"
        )
```

---

### 3. UI Layer

#### 3.1. RestoreCSVWizard (ui/wizards/restore_csv_wizard.py)

**레이아웃**: 단일 페이지 (모든 설정 한 번에)

```python
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt6.QtCore import Qt

class RestoreCSVWizard(QDialog):
    """CSV 따옴표 복원 Wizard (단일 페이지)

    UI 구성:
        [원본 파일 선택]  [📁 찾아보기]
        [export 파일 선택] [📁 찾아보기]
        [출력 폴더 선택]   [📁 찾아보기]

        [취소] [복원 시작]
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("CSV 따옴표 복원")
        self.resize(600, 300)

        self.original_path = ""
        self.export_path = ""
        self.output_dir = ""

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignTokens.SPACING_MD)

        # 원본 파일 선택
        original_layout = QHBoxLayout()
        self.original_label = QLabel("원본 파일:")
        self.original_edit = QLineEdit()
        self.original_edit.setReadOnly(True)
        self.original_btn = QPushButton("찾아보기")
        self.original_btn.setObjectName("secondaryButton")
        original_layout.addWidget(self.original_label)
        original_layout.addWidget(self.original_edit)
        original_layout.addWidget(self.original_btn)
        layout.addLayout(original_layout)

        # export 파일 선택
        export_layout = QHBoxLayout()
        self.export_label = QLabel("memoQ Export 파일:")
        self.export_edit = QLineEdit()
        self.export_edit.setReadOnly(True)
        self.export_btn = QPushButton("찾아보기")
        self.export_btn.setObjectName("secondaryButton")
        export_layout.addWidget(self.export_label)
        export_layout.addWidget(self.export_edit)
        export_layout.addWidget(self.export_btn)
        layout.addLayout(export_layout)

        # 출력 폴더 선택
        output_layout = QHBoxLayout()
        self.output_label = QLabel("출력 폴더:")
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        self.output_btn = QPushButton("찾아보기")
        self.output_btn.setObjectName("secondaryButton")
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_btn)
        layout.addLayout(output_layout)

        layout.addStretch()

        # 하단 버튼
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setObjectName("secondaryButton")
        self.start_btn = QPushButton("복원 시작")
        self.start_btn.setObjectName("primaryButton")
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
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "원본 CSV 파일 선택", "", "CSV Files (*.csv)"
        )
        if path:
            self.original_path = path
            self.original_edit.setText(path)
            self._update_start_button()

    def _select_export(self):
        """export 파일 선택"""
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "memoQ Export CSV 파일 선택", "", "CSV Files (*.csv)"
        )
        if path:
            self.export_path = path
            self.export_edit.setText(path)
            self._update_start_button()

    def _select_output(self):
        """출력 폴더 선택"""
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if path:
            self.output_dir = path
            self.output_edit.setText(path)
            self._update_start_button()

    def _update_start_button(self):
        """시작 버튼 활성화 상태 업데이트"""
        enabled = (
            bool(self.original_path) and
            bool(self.export_path) and
            bool(self.output_dir)
        )
        self.start_btn.setEnabled(enabled)

    def get_data(self) -> dict:
        """선택된 데이터 반환"""
        return {
            'original_path': self.original_path,
            'export_path': self.export_path,
            'output_dir': self.output_dir
        }
```

#### 3.2. CommonTab (ui/common_tab.py)

**레이아웃**: LY/GL과 동일한 수직 리스트

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from sebastian.ui.common.design_tokens import DesignTokens

class CommonTab(QWidget):
    """공통 기능 탭

    Signals:
        restore_csv_requested: CSV 복원 요청
    """

    restore_csv_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignTokens.SPACING_LG)
        layout.setContentsMargins(
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG
        )

        # 제목
        title = QLabel("공통 도구")
        title.setObjectName("tabTitle")
        layout.addWidget(title)

        # 기능 리스트
        functions = [
            (
                "CSV 따옴표 복원",
                "memoQ export 파일의 따옴표 복원",
                self.restore_csv_requested.emit
            ),
            # 향후 추가 기능...
        ]

        for title, description, handler in functions:
            btn = self._create_function_button(title, description)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()

    def _create_function_button(self, title: str, description: str) -> QPushButton:
        """기능 버튼 생성 (LY/GL 스타일)"""
        btn = QPushButton()
        btn.setObjectName("listItemButton")
        btn.setFixedHeight(64)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 버튼 텍스트 (타이틀 + 설명)
        btn.setText(f"{title}\n{description}")

        return btn

    def _connect_signals(self):
        """Signal 연결"""
        pass
```

#### 3.3. MainWindow 통합 (ui/main_window.py)

```python
# MainWindow.__init__() 수정

# 탭 생성
self.m4gl_tab = M4GLTab()
self.ncgl_tab = NCGLTab()
self.lygl_tab = LYGLTab()
self.common_tab = CommonTab()  # 새 탭 추가

# 탭 추가
self.tabs.addTab(self.m4gl_tab, "M4/GL")
self.tabs.addTab(self.ncgl_tab, "NC/GL")
self.tabs.addTab(self.lygl_tab, "LY/GL")
self.tabs.addTab(self.common_tab, "공통")  # 새 탭 추가

# Signal 연결
self.common_tab.restore_csv_requested.connect(self._on_restore_csv_requested)

# ...

def _on_restore_csv_requested(self):
    """CSV 복원 요청 처리"""
    from sebastian.ui.wizards.restore_csv_wizard import RestoreCSVWizard
    from sebastian.workers.common_worker import CommonWorker
    from sebastian.ui.common.progress_dialog import ProgressDialog

    wizard = RestoreCSVWizard(self)
    if wizard.exec() != QDialog.DialogCode.Accepted:
        return

    data = wizard.get_data()

    # Worker 생성
    output_path = Path(data['output_dir']) / f"{Path(data['export_path']).stem}_restored.csv"
    worker = CommonWorker(
        operation='restore_csv',
        original_path=data['original_path'],
        export_path=data['export_path'],
        output_path=str(output_path)
    )

    # Progress Dialog
    progress = ProgressDialog("CSV 따옴표 복원", self)
    worker.progress_updated.connect(progress.set_progress)
    worker.status_updated.connect(progress.set_status)
    worker.completed.connect(lambda msg: self._on_worker_completed(progress, msg))
    worker.error_occurred.connect(lambda msg: self._on_worker_error(progress, msg))

    worker.start()
    progress.exec()
```

---

## 파일 구조

```
sebastianmk2/
├── sebastian/
│   ├── core/
│   │   ├── common/              # 새 디렉토리
│   │   │   ├── __init__.py
│   │   │   ├── csv_validator.py  # CSV 검증
│   │   │   └── csv_restore.py    # CSV 복원 + 보고서
│   │   ├── m4gl/
│   │   ├── ncgl/
│   │   └── lygl/
│   ├── workers/
│   │   ├── common_worker.py      # 새 파일
│   │   ├── m4gl_worker.py
│   │   ├── ncgl_worker.py
│   │   └── lygl_worker.py
│   ├── ui/
│   │   ├── common_tab.py         # 새 파일
│   │   ├── m4gl_tab.py
│   │   ├── ncgl_tab.py
│   │   ├── lygl_tab.py
│   │   ├── wizards/
│   │   │   ├── restore_csv_wizard.py  # 새 파일
│   │   │   ├── merge_wizard.py
│   │   │   └── ...
│   │   └── main_window.py        # 수정
├── tests/
│   ├── test_common/              # 새 디렉토리
│   │   ├── __init__.py
│   │   ├── test_csv_validator.py
│   │   └── test_csv_restore.py
│   ├── test_m4gl/
│   ├── test_ncgl/
│   └── test_lygl/
└── claudedocs/
    └── CSV_Restore_Feature_Plan.md  # 이 문서
```

---

## 구현 단계

### Phase 1: Core Layer (우선순위: 최고)

**작업 항목**:
1. ✅ `core/common/__init__.py` 생성
2. ✅ `core/common/csv_validator.py` 구현
   - `validate_csv_structure()` 함수
   - `CSVValidationError` 예외 클래스
3. ✅ `core/common/csv_restore.py` 구현
   - `restore_csv_quotes()` 함수
   - `generate_diff_report()` 함수

**검증**:
- 단위 테스트 작성 및 통과
- 수동 테스트 (샘플 CSV 파일)

### Phase 2: Worker Layer (우선순위: 높음)

**작업 항목**:
1. ✅ `workers/common_worker.py` 구현
   - `CommonWorker` 클래스
   - Signal/Slot 정의
   - `_restore_csv_quotes()` 메서드

**검증**:
- Signal 정상 동작 확인
- Progress Queue 업데이트 확인

### Phase 3: UI Layer (우선순위: 높음)

**작업 항목**:
1. ✅ `ui/wizards/restore_csv_wizard.py` 구현
   - 단일 페이지 Wizard
   - 파일 선택 UI
   - 검증 로직
2. ✅ `ui/common_tab.py` 구현
   - LY/GL 스타일 레이아웃
   - 버튼 생성
   - Signal 정의
3. ✅ `ui/main_window.py` 수정
   - 공통 탭 추가
   - Signal 연결
   - Worker 실행 로직

**검증**:
- UI 레이아웃 확인 (LY/GL과 일치)
- 디자인 토큰 적용 확인
- Wizard 동작 확인

### Phase 4: 테스트 (우선순위: 중간)

**작업 항목**:
1. ✅ `tests/test_common/test_csv_validator.py` 작성
2. ✅ `tests/test_common/test_csv_restore.py` 작성
3. ✅ 통합 테스트 작성

**검증**:
- 테스트 커버리지 ≥80%
- 모든 테스트 통과

### Phase 5: 문서화 (우선순위: 낮음)

**작업 항목**:
1. ✅ PRD 업데이트 (`prd/PRD-Common.md` 생성)
2. ✅ 사용자 가이드 업데이트 (`docs/user-guide.html`)
3. ✅ CLAUDE.md 업데이트

---

## 테스트 계획

### 단위 테스트 (tests/test_common/)

#### test_csv_validator.py

```python
import pytest
from sebastian.core.common.csv_validator import validate_csv_structure, CSVValidationError

class TestCSVValidator:
    def test_valid_files(self, tmp_path):
        """정상 파일 검증"""
        # 테스트 파일 생성
        original = tmp_path / "original.csv"
        export = tmp_path / "export.csv"

        # 정상 케이스
        original_df, export_df, warnings = validate_csv_structure(
            str(original), str(export)
        )
        assert len(warnings) == 0

    def test_column_count_mismatch(self, tmp_path):
        """컬럼 수 불일치"""
        # 컬럼 수가 다른 파일 생성
        with pytest.raises(CSVValidationError, match="컬럼 수 불일치"):
            validate_csv_structure(...)

    def test_header_mismatch(self, tmp_path):
        """헤더 불일치"""
        # 헤더가 다른 파일 생성
        with pytest.raises(CSVValidationError, match="헤더 불일치"):
            validate_csv_structure(...)

    def test_keyname_mismatch(self, tmp_path):
        """key-name 불일치"""
        # export에만 있는 key-name
        with pytest.raises(CSVValidationError, match="key-name 불일치"):
            validate_csv_structure(...)
```

#### test_csv_restore.py

```python
import pytest
from sebastian.core.common.csv_restore import restore_csv_quotes

class TestCSVRestore:
    def test_restore_quotes_simple(self, tmp_path):
        """단순 따옴표 복원"""
        # 원본: "텍스트", export: 텍스트 → 복원: "텍스트"
        restored_path, report_path = restore_csv_quotes(...)

        # 복원 파일 검증
        assert Path(restored_path).exists()
        assert restored_path.endswith("_restored.csv")

        # 보고서 파일 검증
        assert Path(report_path).exists()
        assert report_path.endswith("_diff_report.xlsx")

    def test_restore_double_quotes(self, tmp_path):
        """이중 따옴표 복원"""
        # HTML 내 "" → " 복원
        ...

    def test_generate_diff_report(self, tmp_path):
        """차이점 보고서 생성"""
        # Excel 파일 구조 검증
        ...
```

### 통합 테스트

```python
class TestCommonTabIntegration:
    def test_full_workflow(self, qtbot, tmp_path):
        """전체 워크플로우 테스트"""
        # 1. Wizard 실행
        # 2. 파일 선택
        # 3. Worker 실행
        # 4. 결과 확인
        ...
```

---

## 검증 기준

### 기능 검증

| 항목 | 기준 | 상태 |
|------|------|------|
| 컬럼 수 일치 검증 | 불일치 시 예외 발생 | ⏳ |
| 헤더 일치 검증 | 불일치 시 경고 + 예외 | ⏳ |
| key-name 매칭 | 100% 정확도 | ⏳ |
| 따옴표 복원 | 원본 패턴과 100% 일치 | ⏳ |
| 파일 저장 | `_restored.csv` 생성 | ⏳ |
| 보고서 생성 | `.xlsx` 3개 시트 | ⏳ |

### 성능 검증

| 항목 | 기준 | 상태 |
|------|------|------|
| 10,000행 처리 | < 5초 | ⏳ |
| 메모리 사용량 | < 500MB | ⏳ |
| UI 반응성 | 블로킹 없음 | ⏳ |

### UI/UX 검증

| 항목 | 기준 | 상태 |
|------|------|------|
| 탭 레이아웃 | LY/GL과 일치 | ⏳ |
| 버튼 스타일 | objectName 사용 | ⏳ |
| Wizard 동작 | 단일 페이지, 검증 완료 후 시작 | ⏳ |
| 디자인 토큰 | Primary 색상 #5E35B1 | ⏳ |

### 코드 품질

| 항목 | 기준 | 상태 |
|------|------|------|
| 타입 힌트 | 모든 함수 | ⏳ |
| Docstring | 모든 클래스/함수 | ⏳ |
| 테스트 커버리지 | ≥80% | ⏳ |
| 3계층 분리 | 준수 | ⏳ |

---

## 리스크 및 대응 방안

### 리스크 1: CSV 파싱 복잡도

**설명**: RFC 4180 규격이 복잡하여 파싱 오류 발생 가능

**대응**:
- Python `csv` 모듈 사용 (RFC 4180 준수)
- pandas `read_csv()` 사용 시 `quoting=csv.QUOTE_ALL` 옵션 활용
- 테스트 케이스 충분히 작성

### 리스크 2: 성능 저하

**설명**: 대용량 CSV 파일 처리 시 성능 저하

**대응**:
- chunk 단위 처리 (10,000행씩)
- Progress Queue로 사용자 피드백 제공
- 필요 시 멀티프로세싱 고려

### 리스크 3: memoQ 규칙 변경

**설명**: memoQ의 정규화 규칙이 변경될 가능성

**대응**:
- 검증 로직을 별도 모듈로 분리 (`csv_validator.py`)
- 규칙 변경 시 해당 모듈만 수정
- 버전별 처리 로직 추가 가능

---

## 향후 확장 계획

### 1단계 (현재)
- ✅ CSV 따옴표 복원 기능

### 2단계 (향후)
- CSV 병합 기능
- CSV 분할 기능
- CSV 형식 변환 (UTF-8 ↔ EUC-KR)

### 3단계 (장기)
- 다양한 CSV 도구 지원 (SDL Trados, Smartling 등)
- 자동화 스크립트 생성
- 배치 처리 기능

---

## 체크리스트

### 개발 시작 전
- [ ] 요구사항 최종 확인
- [ ] 아키텍처 설계 검토
- [ ] 파일 구조 확정
- [ ] 샘플 데이터 준비

### 개발 중
- [ ] Core Layer 구현 완료
- [ ] Worker Layer 구현 완료
- [ ] UI Layer 구현 완료
- [ ] 단위 테스트 작성 완료
- [ ] 통합 테스트 작성 완료

### 개발 완료 후
- [ ] 모든 테스트 통과
- [ ] 수동 UI 테스트 완료
- [ ] 레거시 비교 (해당 없음)
- [ ] 문서 업데이트
- [ ] Git 커밋 및 PR

---

## 부록

### A. 샘플 데이터

**원본 CSV** (original.csv):
```csv
key-name,ko,en
key1,"안녕하세요, 세계",Hello World
key2,텍스트,"Quoted Text"
key3,"HTML <span class=""green"">테스트</span>",HTML Test
```

**memoQ Export CSV** (export.csv):
```csv
key-name,ko,en
key1,안녕하세요, 세계,"Hello, World"
key2,"텍스트",Quoted Text
key3,"HTML <span class=""green"">테스트</span>","HTML Test"
```

**복원 CSV** (export_restored.csv):
```csv
key-name,ko,en
key1,"안녕하세요, 세계",Hello World
key2,텍스트,"Quoted Text"
key3,"HTML <span class=""green"">테스트</span>",HTML Test
```

### B. 참고 문서

- **RFC 4180**: https://www.ietf.org/rfc/rfc4180.txt
- **memoQ 문서**: (사내 문서)
- **Sebastian CLAUDE.md**: `D:\Repository\sebastianmk2\CLAUDE.md`
- **PRD-Overview.md**: `prd/PRD-Overview.md`

---

**문서 버전**: 1.0
**최종 수정**: 2025-12-26
**작성자**: Claude (Sebastian AI Assistant)
