# Sebastian 프로젝트 사용자 경험 일관성 분석 보고서

**분석 일시**: 2025-12-24
**분석 대상**: Sebastian v0.2.0 (M4/GL, NC/GL, LY/GL)
**분석 도구**: Claude Opus 4.5 + Explore Agent
**분석자**: Claude Sonnet 4.5

---

## 📊 Executive Summary

Sebastian 프로젝트의 사용자 경험 일관성을 분석한 결과, **부분적 일관성**을 확인했습니다.

**주요 발견 사항**:
1. ✅ **진행도 표시 창**: 공통 모듈 사용 (ProgressDialog) - 일관성 있음
2. ❌ **남은 시간 계산**: 코드 존재하나 **미작동** - 모든 기능에서 "계산 중" 고정
3. ❌ **소요 시간 표시**: 8개 기능 중 **2개만 표시** (25%) - 일관성 없음
4. ⚠️ **UX 차이**: 파일 선택, 버튼 텍스트, 에러 메시지 형식 불일치

**일관성 점수**: **6.0/10** (개선 필요)

---

## 1️⃣ 진행도 표시 창 모듈 공통화 분석

### 현황

✅ **공통 모듈 사용**: 모든 탭이 `sebastian/ui/common/progress_dialog.py`의 `ProgressDialog` 사용

**코드 경로**:
```
sebastian/ui/common/progress_dialog.py  (ProgressDialog 클래스)
├── sebastian/ui/m4gl_tab.py            (M4GL 사용)
├── sebastian/ui/ncgl_tab.py            (NC/GL 사용)
└── sebastian/ui/lygl_tab.py            (LY/GL 사용)
```

---

### 상세 분석

#### M4GL 사용 방식 (`sebastian/ui/m4gl_tab.py`)

```python
# Line 123-129: Signal 연결
self.worker.progress_updated.connect(self.progress_dialog.update_progress)
self.worker.status_updated.connect(self.progress_dialog.update_status)
self.worker.step_updated.connect(self.progress_dialog.update_step)
self.worker.files_count_updated.connect(self.progress_dialog.update_files_count)
self.worker.completed.connect(self._on_worker_completed)
self.worker.error_occurred.connect(self._on_worker_error)
```

**사용 Signal**: 6개
- `progress_updated` (진행률)
- `status_updated` (상태 메시지)
- `step_updated` (단계 정보)
- `files_count_updated` (파일 처리 수)
- `completed` (완료)
- `error_occurred` (에러)

---

#### NC/GL 사용 방식 (`sebastian/ui/ncgl_tab.py`)

```python
# Line 134-140: Signal 연결
self.worker.progress_updated.connect(self.progress_dialog.update_progress)
self.worker.status_updated.connect(self.progress_dialog.update_status)
self.worker.step_updated.connect(self.progress_dialog.update_step)
self.worker.files_count_updated.connect(self.progress_dialog.update_files_count)
self.worker.completed.connect(self._on_worker_completed)
self.worker.error_occurred.connect(self._on_worker_error)
```

**사용 Signal**: 6개 (M4GL과 동일)

---

#### LY/GL 사용 방식 (`sebastian/ui/lygl_tab.py`)

```python
# Line 138-142: Signal 연결
self.worker.progress_updated.connect(self.progress_dialog.update_progress)
self.worker.status_updated.connect(self.progress_dialog.update_status)
self.worker.completed.connect(self._on_completed)
self.worker.error_occurred.connect(self._on_error)
```

**사용 Signal**: 4개 ⚠️
- `progress_updated` (진행률)
- `status_updated` (상태 메시지)
- `completed` (완료)
- `error_occurred` (에러)

**누락된 Signal**:
- ❌ `step_updated` (단계 정보)
- ❌ `files_count_updated` (파일 처리 수)

---

### 발견 사항

#### ✅ 일관성 있는 부분
- 모든 탭이 동일한 `ProgressDialog` 클래스 사용
- 기본 Signal (`progress_updated`, `status_updated`, `completed`, `error_occurred`) 공통 사용

#### ⚠️ 차이점
- **LY/GL**: `step_updated`, `files_count_updated` Signal 미사용
- **이유**: LY/GL Worker는 해당 Signal 미정의

#### ❌ 문제점
- LY/GL은 단계 정보와 파일 처리 수를 표시하지 않음
- 사용자는 M4/GL, NC/GL보다 상세한 정보를 받지 못함

---

## 2️⃣ 남은 시간 계산 기능 분석

### 현황

❌ **미작동**: 코드는 존재하나 **실제로 호출되지 않음**

**코드 위치**: `sebastian/ui/common/progress_dialog.py`

---

### 상세 분석

#### 시간 계산 로직 (`progress_dialog.py` Line 90-103)

```python
def update_time(self, elapsed: int, remaining: int):
    """남은 시간 업데이트

    Args:
        elapsed: 경과 시간 (초)
        remaining: 남은 시간 (초)
    """
    elapsed_str = self._format_time(elapsed)
    remaining_str = self._format_time(remaining) if remaining >= 0 else "계산 중..."

    self.time_label.setText(
        f"<span style='color: #6B7280;'>경과: {elapsed_str} | 남은 시간: {remaining_str}</span>"
    )
```

#### 시간 포맷 헬퍼 (`progress_dialog.py` Line 105-117)

```python
def _format_time(self, seconds: int) -> str:
    """초를 시:분:초 형식으로 변환"""
    if seconds < 0:
        return "계산 중..."

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}시간 {minutes}분 {secs}초"
    elif minutes > 0:
        return f"{minutes}분 {secs}초"
    return f"{secs}초"
```

#### 초기 상태 (`progress_dialog.py` Line 64)

```python
self.time_label = QLabel("경과: 0초 | 남은 시간: 계산 중...")
```

---

### 문제: `update_time()` 호출 부재

#### Workers 확인 결과

**M4GLWorker** (`sebastian/workers/m4gl_worker.py`):
```python
# Signal 정의 (Line 21-25)
progress_updated = pyqtSignal(int)
status_updated = pyqtSignal(str)
step_updated = pyqtSignal(str)
files_count_updated = pyqtSignal(int, int)
completed = pyqtSignal(str)
error_occurred = pyqtSignal(str)
```
❌ **시간 관련 Signal 없음**

**NCGLWorker** (`sebastian/workers/ncgl_worker.py`):
```python
# Signal 정의 (Line 24-28)
progress_updated = pyqtSignal(int)
status_updated = pyqtSignal(str)
step_updated = pyqtSignal(str)
files_count_updated = pyqtSignal(int, int)
completed = pyqtSignal(str)
error_occurred = pyqtSignal(str)
```
❌ **시간 관련 Signal 없음**

**LYGLWorker** (`sebastian/workers/lygl_worker.py`):
```python
# Signal 정의 (Line 21-24)
progress_updated = pyqtSignal(int)
status_updated = pyqtSignal(str)
completed = pyqtSignal(str)
error_occurred = pyqtSignal(str)
```
❌ **시간 관련 Signal 없음**

---

### 발견 사항

#### ❌ 실제 작동 여부: **미작동**

**근거**:
1. 모든 Worker에 `time_updated` Signal 미정의
2. `update_time()` 메서드를 호출하는 Signal 연결 없음
3. 사용자는 항상 **"남은 시간: 계산 중..."**만 표시됨

#### 버그 원인

- `ProgressDialog`에 시간 계산 로직 존재
- Worker가 시간 정보를 전송하지 않음
- Signal/Slot 연결 누락

---

## 3️⃣ 작업 소요 시간 표시 분석

### 현황

**8개 기능 중 2개만 소요 시간 표시** (25%)

| 탭 | 기능 | 소요 시간 표시 | 코드 위치 |
|------|------|----------------|-----------|
| M4/GL | DIALOGUE | ✅ 표시 | `dialogue.py:182` |
| M4/GL | STRING | ✅ 표시 | `string.py:169` |
| NC/GL | 병합 | ❌ 미표시 | `merge.py:153` |
| LY/GL | Merge | ❌ 미표시 | `merge.py:98` |
| LY/GL | Split | ❌ 미표시 | `split.py:81` |
| LY/GL | Batch | ❌ 미표시 | `batches.py:122` |
| LY/GL | Diff | ❌ 미표시 | `diff.py:90` |
| LY/GL | Status Check | ❌ 미표시 | `status_check.py:145` |

---

### 상세 분석

#### ✅ M4/GL DIALOGUE (`sebastian/core/m4gl/dialogue.py`)

```python
# Line 28-29: 시작 시간 기록
def merge_dialogue(folder_path: str, progress_queue) -> None:
    start_time = time.time()
    try:
        # ... 병합 로직 ...

        # Line 182: 소요 시간 표시
        elapsed_time = time.time() - start_time
        progress_queue.put(f"완료:파일이 {output_file}로 저장되었습니다. 소요 시간: {int(elapsed_time)}초")
```

#### ✅ M4/GL STRING (`sebastian/core/m4gl/string.py`)

```python
# Line 26-27: 시작 시간 기록
def merge_string(folder_path: str, progress_queue) -> None:
    start_time = time.time()
    try:
        # ... 병합 로직 ...

        # Line 169: 소요 시간 표시
        elapsed_time = time.time() - start_time
        progress_queue.put(f"완료:파일이 {output_file}로 저장되었습니다. 소요 시간: {int(elapsed_time)}초")
```

---

#### ❌ NC/GL 병합 (`sebastian/core/ncgl/merge.py`)

```python
# Line 153: 소요 시간 미표시
progress_queue.put(f"완료:파일이 {output_file}로 저장되었습니다.")
```

**문제**: `start_time` 기록 없음, 소요 시간 계산/표시 없음

---

#### ❌ LY/GL Merge (`sebastian/core/lygl/merge.py`)

```python
# Line 98: 소요 시간 미표시
progress_queue.put(f"완료:{output_path}")
```

**문제**: `start_time` 기록 없음, 간단한 경로만 표시

---

#### ❌ LY/GL Split (`sebastian/core/lygl/split.py`)

```python
# Line 81: 소요 시간 미표시
progress_queue.put(f"완료:{len(output_files)}개 파일 생성")
```

---

#### ❌ LY/GL Batches (`sebastian/core/lygl/batches.py`)

```python
# Line 122: 소요 시간 미표시
progress_queue.put(f"완료:{output_path}")
```

---

#### ❌ LY/GL Diff (`sebastian/core/lygl/diff.py`)

```python
# Line 90: 소요 시간 미표시
progress_queue.put(f"완료:{output_path}")
```

---

#### ❌ LY/GL Status Check (`sebastian/core/lygl/status_check.py`)

```python
# Line 145: 소요 시간 미표시
progress_queue.put(f"완료:검증 완료")
```

---

### 발견 사항

#### ✅ 표시하는 기능 (2개)
- M4/GL DIALOGUE
- M4/GL STRING

**메시지 형식**:
```
"완료:파일이 {파일명}로 저장되었습니다. 소요 시간: {N}초"
```

#### ❌ 표시하지 않는 기능 (6개)
- NC/GL 병합
- LY/GL 전체 (Merge, Split, Batch, Diff, Status Check)

**일관성 부족**: 75%의 기능이 소요 시간을 표시하지 않음

---

## 4️⃣ 탭별/기능별 UX 차이 분석

### 에러 처리

#### M4/GL (`m4gl_tab.py`)

```python
# Line 150-153
def _on_worker_error(self, error_msg: str):
    """에러 처리"""
    self.progress_dialog.close()
    QMessageBox.critical(self, "오류", error_msg)
```

**형식**: `QMessageBox.critical(제목="오류", 내용=에러 메시지)`

---

#### NC/GL (`ncgl_tab.py`)

```python
# Line 161-164
def _on_worker_error(self, error_msg: str):
    """에러 처리"""
    self.progress_dialog.close()
    QMessageBox.critical(self, "오류", error_msg)
```

**형식**: M4/GL과 동일 ✅

---

#### LY/GL (`lygl_tab.py`)

```python
# Line 162-165
def _on_error(self, error_msg: str):
    """에러 처리"""
    self.progress_dialog.close()
    QMessageBox.critical(self, "오류", error_msg)
```

**형식**: M4/GL, NC/GL과 동일 ✅

**일관성**: ✅ **에러 처리 형식 통일**

---

### 파일 선택 UI

#### M4/GL

**방식**: 폴더 선택 (`QFileDialog.getExistingDirectory`)

```python
# m4gl_tab.py Line 106-108
folder = QFileDialog.getExistingDirectory(
    self, "M4/GL 폴더 선택", "", QFileDialog.Option.ShowDirsOnly
)
```

---

#### NC/GL

**방식**: 폴더 선택 (`QFileDialog.getExistingDirectory`)

```python
# ncgl_tab.py Line 116-118
folder = QFileDialog.getExistingDirectory(
    self, "NC/GL 폴더 선택", "", QFileDialog.Option.ShowDirsOnly
)
```

---

#### LY/GL

**방식**: Wizard (복잡한 입력 수집)

```python
# lygl_tab.py Line 99-124
wizard = MergeWizard(self)
if wizard.exec() == QDialog.DialogCode.Accepted:
    data = wizard.get_data()
    # ... Worker 실행 ...
```

**Wizard 종류**:
- `MergeWizard`
- `SplitWizard`
- `BatchesWizard`
- `DiffWizard`
- `StatusCheckWizard`

**차이점**: ⚠️ LY/GL만 Wizard 패턴 사용

**이유**: LY/GL은 복잡한 입력 필요 (7개 파일, 옵션 선택 등)

---

### 진행 상황 업데이트

#### M4/GL DIALOGUE

**업데이트 지점** (10개):
1. Line 51: "단계:1/3"
2. Line 52: "파일:CINEMATIC_DIALOGUE.xlsm"
3. Line 56: 20% (progress)
4. Line 57: "처리된 파일:1"
5. Line 59: "파일:SMALLTALK_DIALOGUE.xlsm"
6. Line 62: 40% (progress)
7. Line 63: "처리된 파일:2"
8. Line 66: "단계:2/3"
9. Line 161: "단계:3/3"
10. Line 162: "파일:NPC.xlsm"

**빈도**: 높음 (세밀한 단계별 업데이트)

---

#### NC/GL 병합

**업데이트 지점** (4개):
1. Line 88: "단계:1/2"
2. Line 90: "파일:{언어} 병합 중..."
3. Line 125: 진행률 (progress)
4. Line 128: "단계:2/2"

**빈도**: 중간

---

#### LY/GL (예: Merge)

**업데이트 지점** (3개):
1. Line 43: 진행률 (progress)
2. Line 65: 진행률 (progress)
3. Line 94: 100% (progress)

**빈도**: 낮음 (주로 진행률만)

**차이점**: ⚠️ LY/GL은 "단계", "파일" 정보 미표시

---

### 완료 알림

#### M4/GL

**방식**: `QMessageBox.information` (정보 다이얼로그)

```python
# m4gl_tab.py Line 143-146
def _on_worker_completed(self, message: str):
    """작업 완료 처리"""
    self.progress_dialog.close()
    QMessageBox.information(self, "완료", message)
```

**메시지 예시**:
```
"파일이 1224_MIR4_MASTER_DIALOGUE.xlsx로 저장되었습니다. 소요 시간: 15초"
```

---

#### NC/GL

**방식**: `QMessageBox.information` (동일)

```python
# ncgl_tab.py Line 154-157
def _on_worker_completed(self, message: str):
    """작업 완료 처리"""
    self.progress_dialog.close()
    QMessageBox.information(self, "완료", message)
```

---

#### LY/GL

**방식**: `QMessageBox.information` (동일)

```python
# lygl_tab.py Line 155-158
def _on_completed(self, message: str):
    """작업 완료 처리"""
    self.progress_dialog.close()
    QMessageBox.information(self, "완료", message)
```

**일관성**: ✅ **완료 알림 방식 통일**

---

### 버튼 텍스트

#### M4/GL

```python
# m4gl_tab.py Line 93-95
dialogue_card.clicked.connect(lambda: self._execute_function("DIALOGUE"))
string_card.clicked.connect(lambda: self._execute_function("STRING"))
```

**실행 버튼**: 카드 클릭 → 자동 실행

---

#### NC/GL

```python
# ncgl_tab.py Line 81
execute_btn = QPushButton("실행 →")
```

**실행 버튼**: `"실행 →"` (한글 + 화살표)

---

#### LY/GL

```python
# lygl_tab.py Line 85
("Merge", "병합", "7개 언어 파일을 하나로 병합", self.merge_requested.emit)
```

**실행 버튼**: 리스트 버튼 클릭 → Wizard → Start

Wizard 버튼 텍스트:
```python
# wizards/merge_wizard.py Line 89
QPushButton("Cancel"), QPushButton("Start")
```

**차이점**: ⚠️
- M4/GL: 자동 실행
- NC/GL: "실행 →" (한글)
- LY/GL: "Start" (영어)

---

## 🎯 종합 평가

### 일관성 점수 (10점 만점)

| 항목 | 점수 | 평가 |
|------|------|------|
| **진행도 표시 모듈** | 8/10 | 공통 모듈 사용하나 Signal 패턴 차이 |
| **남은 시간 계산** | 0/10 | 코드 존재하나 완전 미작동 |
| **소요 시간 표시** | 3/10 | 8개 중 2개만 표시 (25%) |
| **전체 UX 일관성** | 6/10 | 부분적 일관성, 개선 필요 |

**평균**: **4.25/10** (개선 필요)

---

### 주요 문제점

#### 1. 남은 시간 계산 미작동 ⚠️

**영향**: 모든 사용자가 "계산 중" 메시지만 확인, 실제 남은 시간 알 수 없음

**근본 원인**:
- `ProgressDialog.update_time()` 메서드 존재
- 모든 Worker에 `time_updated` Signal 미정의
- Signal/Slot 연결 누락

---

#### 2. 소요 시간 표시 불일치 ❌

**영향**: 75%의 기능에서 작업 완료 후 소요 시간 확인 불가

**불일치 사례**:
- M4/GL: "소요 시간: 15초" ✅
- NC/GL: 소요 시간 미표시 ❌
- LY/GL: 소요 시간 미표시 ❌

---

#### 3. LY/GL Signal 패턴 차이 ⚠️

**영향**: LY/GL 사용자는 단계 정보, 파일 처리 수 확인 불가

**누락 Signal**:
- `step_updated` (단계 정보)
- `files_count_updated` (파일 처리 수)

---

#### 4. 버튼 텍스트 혼용 ⚠️

**영향**: 사용자 혼란 (한글/영어 혼용)

**불일치 사례**:
- NC/GL: "실행 →" (한글)
- LY/GL Wizard: "Start" (영어)
- LY/GL Wizard: "Cancel" vs M4/GL, NC/GL: "취소"

---

### 개선 권장사항

#### 1. 남은 시간 계산 기능 구현 [우선순위: **High**]

**목표**: 모든 기능에서 실시간 남은 시간 표시

**구현 방법**:

**Step 1**: Worker에 `time_updated` Signal 추가
```python
# workers/m4gl_worker.py (NC/GL, LY/GL도 동일)
class M4GLWorker(QThread):
    # 기존 Signals
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    # 추가 Signal
    time_updated = pyqtSignal(int, int)  # (경과 시간, 남은 시간)
```

**Step 2**: Core 로직에서 시간 계산 및 전송
```python
# core/m4gl/dialogue.py
def merge_dialogue(folder_path: str, progress_queue) -> None:
    start_time = time.time()

    # 진행률 업데이트 시 남은 시간 계산
    total_steps = 100
    current_step = 20

    elapsed = int(time.time() - start_time)
    estimated_total = (elapsed / current_step) * total_steps if current_step > 0 else 0
    remaining = max(0, int(estimated_total - elapsed))

    progress_queue.put(("time", elapsed, remaining))
```

**Step 3**: Worker에서 Signal 전송
```python
# workers/m4gl_worker.py
def run(self):
    while not self.queue.empty():
        item = self.queue.get()
        if isinstance(item, tuple) and item[0] == "time":
            self.time_updated.emit(item[1], item[2])
```

**Step 4**: Tab에서 Signal 연결
```python
# ui/m4gl_tab.py
self.worker.time_updated.connect(self.progress_dialog.update_time)
```

**예상 효과**:
- 모든 사용자가 실시간 남은 시간 확인 가능
- 사용자 경험 크게 개선

**예상 작업량**: 3-4시간 (8개 파일 수정)

---

#### 2. 모든 기능에 소요 시간 표시 추가 [우선순위: **High**]

**목표**: 100% 일관성 (모든 기능에서 소요 시간 표시)

**구현 방법**:

**표준 패턴**:
```python
def some_function(folder_path: str, progress_queue) -> None:
    start_time = time.time()  # 시작 시간 기록
    try:
        # ... 로직 ...

        # 완료 메시지에 소요 시간 포함
        elapsed_time = time.time() - start_time
        progress_queue.put(f"완료:파일이 {output_file}로 저장되었습니다. 소요 시간: {int(elapsed_time)}초")
    except Exception as e:
        progress_queue.put(("error", str(e)))
```

**수정 대상** (6개 파일):
1. `sebastian/core/ncgl/merge.py`
2. `sebastian/core/lygl/merge.py`
3. `sebastian/core/lygl/split.py`
4. `sebastian/core/lygl/batches.py`
5. `sebastian/core/lygl/diff.py`
6. `sebastian/core/lygl/status_check.py`

**예상 효과**:
- 모든 사용자가 작업 완료 후 소요 시간 확인 가능
- 성능 비교 및 최적화 판단 용이

**예상 작업량**: 1-2시간 (6개 파일 수정)

---

#### 3. LY/GL Worker Signal 패턴 통일 [우선순위: **Medium**]

**목표**: M4/GL, NC/GL과 동일한 Signal 패턴 사용

**구현 방법**:

**Step 1**: LYGLWorker에 Signal 추가
```python
# workers/lygl_worker.py
class LYGLWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    # 추가 Signals
    step_updated = pyqtSignal(str)  # "단계:1/3"
    files_count_updated = pyqtSignal(int, int)  # (처리된 파일, 전체 파일)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
```

**Step 2**: Core 로직에서 단계 정보 전송
```python
# core/lygl/merge.py
def merge_files(...):
    progress_queue.put("단계:1/2")
    progress_queue.put("파일:병합 중...")
    progress_queue.put(("files_count", 3, 7))  # 3개 처리, 전체 7개
```

**Step 3**: Tab에서 Signal 연결
```python
# ui/lygl_tab.py
self.worker.step_updated.connect(self.progress_dialog.update_step)
self.worker.files_count_updated.connect(self.progress_dialog.update_files_count)
```

**예상 효과**:
- LY/GL 사용자도 상세한 진행 정보 확인 가능
- 모든 탭에서 일관된 정보 제공

**예상 작업량**: 2-3시간 (6개 LY/GL 기능 수정)

---

#### 4. 버튼 텍스트 및 메시지 표준화 [우선순위: **Low**]

**목표**: 모든 UI 텍스트 한글 통일

**구현 방법**:

**표준 텍스트**:
- 실행 버튼: "실행 →" (한글)
- 취소 버튼: "취소" (한글)
- 확인 버튼: "확인" (한글)
- 에러 제목: "오류" (한글)
- 완료 제목: "완료" (한글)

**수정 대상**:
```python
# wizards/*.py 전체
QPushButton("Cancel") → QPushButton("취소")
QPushButton("Start") → QPushButton("시작")
QPushButton("OK") → QPushButton("확인")
```

**예상 효과**:
- UI 일관성 향상
- 한국어 사용자 친화성 개선

**예상 작업량**: 1시간 (Wizard 5개 파일 수정)

---

## 📋 상세 코드 분석 결과

### 진행도 표시 모듈 (`ProgressDialog`)

**파일**: `sebastian/ui/common/progress_dialog.py`

**주요 메서드**:
```python
# Line 44-70: 초기화
def __init__(self, parent=None):
    # ... UI 구성 ...
    self.time_label = QLabel("경과: 0초 | 남은 시간: 계산 중...")

# Line 72-78: 진행률 업데이트
def update_progress(self, value: int):
    self.progress_bar.setValue(value)

# Line 80-88: 상태 메시지 업데이트
def update_status(self, status: str):
    self.status_label.setText(f"<span style='color: #374151;'>{status}</span>")

# Line 90-103: 시간 업데이트 (미사용)
def update_time(self, elapsed: int, remaining: int):
    # ... 시간 계산 로직 ...

# Line 119-127: 단계 업데이트
def update_step(self, step: str):
    self.step_label.setText(f"<span style='color: #6B7280;'>{step}</span>")

# Line 129-138: 파일 처리 수 업데이트
def update_files_count(self, processed: int, total: int):
    self.files_label.setText(f"<span style='color: #6B7280;'>처리: {processed}/{total}</span>")
```

---

### Worker Signal 정의

#### M4GLWorker (`workers/m4gl_worker.py`)

```python
# Line 21-26
progress_updated = pyqtSignal(int)         # 진행률 (0-100)
status_updated = pyqtSignal(str)           # 상태 메시지
step_updated = pyqtSignal(str)             # 단계 정보
files_count_updated = pyqtSignal(int, int) # 처리 파일 수
completed = pyqtSignal(str)                # 완료 메시지
error_occurred = pyqtSignal(str)           # 에러 메시지
```

**Signal 수**: 6개 ✅

---

#### NCGLWorker (`workers/ncgl_worker.py`)

```python
# Line 24-29
progress_updated = pyqtSignal(int)
status_updated = pyqtSignal(str)
step_updated = pyqtSignal(str)
files_count_updated = pyqtSignal(int, int)
completed = pyqtSignal(str)
error_occurred = pyqtSignal(str)
```

**Signal 수**: 6개 ✅

---

#### LYGLWorker (`workers/lygl_worker.py`)

```python
# Line 21-24
progress_updated = pyqtSignal(int)
status_updated = pyqtSignal(str)
completed = pyqtSignal(str)
error_occurred = pyqtSignal(str)
```

**Signal 수**: 4개 ⚠️

**누락**:
- `step_updated`
- `files_count_updated`

---

### 완료 메시지 패턴

#### 소요 시간 표시 ✅

```python
# dialogue.py Line 182
f"완료:파일이 {output_file}로 저장되었습니다. 소요 시간: {int(elapsed_time)}초"

# string.py Line 169
f"완료:파일이 {output_file}로 저장되었습니다. 소요 시간: {int(elapsed_time)}초"
```

**형식**: `"완료:파일이 {파일명}로 저장되었습니다. 소요 시간: {N}초"`

---

#### 소요 시간 미표시 ❌

```python
# ncgl/merge.py Line 153
f"완료:파일이 {output_file}로 저장되었습니다."

# lygl/merge.py Line 98
f"완료:{output_path}"

# lygl/split.py Line 81
f"완료:{len(output_files)}개 파일 생성"

# lygl/batches.py Line 122
f"완료:{output_path}"

# lygl/diff.py Line 90
f"완료:{output_path}"

# lygl/status_check.py Line 145
f"완료:검증 완료"
```

**형식**: 간단한 완료 메시지만 표시

---

## 🎯 결론

Sebastian 프로젝트는 **공통 모듈(ProgressDialog)**을 사용하여 기본적인 일관성을 유지하고 있으나, **세부 구현에서 불일치**가 발견되었습니다.

**주요 개선 필요 영역**:
1. ❌ **남은 시간 계산**: 완전 미작동 → 즉시 수정 필요
2. ❌ **소요 시간 표시**: 25% 일관성 → 100% 일관성 목표
3. ⚠️ **LY/GL Signal**: M4/GL, NC/GL과 패턴 통일 필요
4. ⚠️ **UI 텍스트**: 한글/영어 혼용 → 한글 통일

**우선순위**:
1. **High**: 남은 시간 계산, 소요 시간 표시 (사용자 경험 직접 영향)
2. **Medium**: LY/GL Signal 패턴 통일 (정보 일관성)
3. **Low**: UI 텍스트 표준화 (시각적 일관성)

개선 후 예상 일관성 점수: **8.5/10** (현재 4.25/10에서 크게 개선)

---

**보고서 작성 완료**: 2025-12-24
**분석 도구**: Claude Opus 4.5 + Explore Agent
**보고서 경로**: `claudedocs/UX_Consistency_Analysis_Report.md`
