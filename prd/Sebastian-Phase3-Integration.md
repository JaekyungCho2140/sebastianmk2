# Sebastian Phase 3: Integration Guide

**버전**: 1.0.0
**작성일**: 2025-12-19
**Phase 목표**: UI와 로직 연결 및 레거시와의 동작 일치 검증

---

## 📋 Phase 3 개요

### 목표

Phase 1의 Core 로직과 Phase 2의 UI를 QThread/Signal/Slot으로 연결하고,
레거시와 100% 동일하게 동작하는지 검증합니다.

### 핵심 원칙

1. **QThread 비동기**: UI 프리징 방지
2. **Queue 기반 통신**: 레거시 인터페이스 유지
3. **출력 파일 검증**: pandas.DataFrame.equals()
4. **Round-trip 무결성**: LY/GL 병합→분할→원본 일치

### 산출물

```
sebastian/
├── core/           # Phase 1 결과물
├── ui/             # Phase 2 결과물
├── workers/        # 신규: QThread Workers
│   ├── __init__.py
│   ├── m4gl_worker.py
│   ├── ncgl_worker.py
│   └── lygl_worker.py
├── tests/          # 신규: 검증 테스트
│   ├── test_m4gl.py
│   ├── test_ncgl.py
│   └── test_lygl.py
└── main.py         # 진입점
```

---

## 🎯 우선순위 순서

### 1. Worker 클래스 구현
- QThread 기반 비동기 처리
- Queue → Signal 변환
- 예상 시간: 2-3일

### 2. UI 연결
- 버튼 클릭 → Worker 실행
- ProgressDialog 업데이트
- 예상 시간: 2-3일

### 3. 검증
- 출력 파일 비교
- Round-trip 테스트
- 예상 시간: 3-4일

---

## 📦 Task 1: Worker 클래스

### 1.1 M4GL Worker

**Claude Code 지시**:
```
"sebastian/workers/m4gl_worker.py를 작성해줘.

요구사항:
1. QThread 상속
2. Signal 정의:
   - progress_updated(int)
   - status_updated(str)
   - file_updated(str)
   - finished(str)
   - error(str)
3. __init__(self, folder_path, operation):
   - operation: 'dialogue' 또는 'string'
4. run() 메서드:
   - Queue 생성
   - operation에 따라 core.m4gl.merge_dialogue() 또는 merge_string() 호출
   - queue.get() → Signal.emit() 변환
   - 에러 처리

예시 코드:
```python
from PyQt6.QtCore import QThread, pyqtSignal
from queue import Queue
from core.m4gl import merge_dialogue, merge_string

class M4GLWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_updated = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, folder_path, operation):
        super().__init__()
        self.folder_path = folder_path
        self.operation = operation

    def run(self):
        try:
            queue = Queue()

            if self.operation == 'dialogue':
                merge_dialogue(self.folder_path, queue)
            elif self.operation == 'string':
                merge_string(self.folder_path, queue)

            # Queue 메시지 처리
            while True:
                msg = queue.get()
                if isinstance(msg, int):
                    self.progress_updated.emit(msg)
                elif isinstance(msg, tuple) and msg[0] == "error":
                    self.error.emit(msg[1])
                    break
                elif isinstance(msg, str):
                    if msg.startswith("완료:"):
                        self.finished.emit(msg[3:])
                        break
                    elif msg.startswith("파일:"):
                        self.file_updated.emit(msg[3:])
                    elif msg.startswith("단계:"):
                        self.status_updated.emit(msg)
                    else:
                        self.status_updated.emit(msg)
        except Exception as e:
            self.error.emit(str(e))
```
"
```

### 1.2 NCGL Worker

**Claude Code 지시**:
```
"sebastian/workers/ncgl_worker.py를 작성해줘.

M4GLWorker와 동일한 구조이지만:
- __init__(self, folder_path, date, milestone)
- core.ncgl.merge_ncgl(folder_path, date, milestone, queue) 호출
"
```

### 1.3 LYGL Worker

**Claude Code 지시**:
```
"sebastian/workers/lygl_worker.py를 작성해줘.

요구사항:
- __init__(self, operation, **kwargs)
- operation: 'merge', 'split', 'batches', 'diff'
- kwargs: 각 operation별 필요한 인자
  - merge: files, output_path
  - split: input_file, output_folder
  - batches: batch_folders, output_path, auto_complete
  - diff: folder1, folder2, output_path
- core.lygl의 해당 함수 호출
"
```

---

## 📦 Task 2: UI 연결

### 2.1 M4GL 탭 연결

**Claude Code 지시**:
```
"sebastian/ui/m4gl_tab.py를 수정해줘.

DIALOGUE 버튼 클릭 시:
1. QFileDialog로 폴더 선택
2. ProgressDialog 생성
3. M4GLWorker('dialogue') 시작
4. Worker Signal → ProgressDialog Slot 연결
5. finished Signal → 결과 메시지 박스
6. error Signal → 에러 메시지 박스

예시 코드:
```python
def on_dialogue_click(self):
    folder = QFileDialog.getExistingDirectory(self, "DIALOGUE 파일 폴더 선택")
    if not folder:
        return

    # ProgressDialog 생성
    self.progress_dialog = ProgressDialog(self)
    self.progress_dialog.setWindowTitle("M4/GL DIALOGUE 병합 중")

    # Worker 생성
    self.worker = M4GLWorker(folder, 'dialogue')

    # Signal 연결
    self.worker.progress_updated.connect(self.progress_dialog.update_progress)
    self.worker.status_updated.connect(self.progress_dialog.update_status)
    self.worker.file_updated.connect(self.progress_dialog.update_file)
    self.worker.finished.connect(self.on_finished)
    self.worker.error.connect(self.on_error)

    # Worker 시작
    self.worker.start()
    self.progress_dialog.show()

def on_finished(self, message):
    self.progress_dialog.close()
    QMessageBox.information(self, "완료", message)

def on_error(self, error_message):
    self.progress_dialog.close()
    QMessageBox.critical(self, "오류", error_message)
```
"
```

### 2.2 NCGL 탭 연결

**Claude Code 지시**:
```
"sebastian/ui/ncgl_tab.py를 수정해줘.

실행 버튼 클릭 시:
1. 날짜, 마일스톤 검증 확인
2. 폴더 선택
3. ProgressDialog 생성
4. NCGLWorker(folder, date, milestone) 시작
5. Signal 연결 (M4GL과 동일)
"
```

### 2.3 LYGL 탭 연결

**Claude Code 지시**:
```
"sebastian/ui/lygl_tab.py를 수정해줘.

각 버튼 클릭 시 위저드 Dialog 표시:
1. Merge 버튼 → MergeWizardDialog
2. Split 버튼 → SplitWizardDialog
3. Batches 버튼 → BatchesWizardDialog
4. Diff 버튼 → DiffWizardDialog

각 위저드 Dialog:
- wireframe의 해당 섹션 참조
- 입력 수집 후 LYGLWorker 시작
- ProgressDialog 연결
"
```

**참고**: 위저드 Dialog 구현은 별도 Task로 분리 가능

---

## 📦 Task 3: 출력 파일 검증

### 3.1 M4GL 검증

**검증 절차**:
```python
# tests/test_m4gl.py

import pandas as pd
import os
from pathlib import Path

def test_dialogue_output():
    """
    레거시 vs 신규 DIALOGUE 병합 결과 비교
    """
    # 1. 레거시 실행 (사전 준비)
    legacy_output = "legacy/M4/1219_MIR4_MASTER_DIALOGUE.xlsx"

    # 2. 신규 실행
    # sebastian.exe 실행 → M4/GL 탭 → DIALOGUE 버튼
    new_output = "1219_MIR4_MASTER_DIALOGUE.xlsx"

    # 3. 비교
    df_legacy = pd.read_excel(legacy_output)
    df_new = pd.read_excel(new_output)

    # 데이터 일치 확인
    assert df_legacy.equals(df_new), "데이터 불일치!"

    # 서식 일치 확인 (openpyxl)
    from openpyxl import load_workbook

    wb_legacy = load_workbook(legacy_output)
    wb_new = load_workbook(new_output)

    ws_legacy = wb_legacy.active
    ws_new = wb_new.active

    # 헤더 폰트 확인
    assert ws_legacy['A1'].font.name == ws_new['A1'].font.name
    assert ws_legacy['A1'].font.size == ws_new['A1'].font.size
    assert ws_legacy['A1'].font.color.rgb == ws_new['A1'].font.color.rgb

    # 헤더 fill 확인
    assert ws_legacy['A1'].fill.start_color.rgb == ws_new['A1'].fill.start_color.rgb

    print("✅ DIALOGUE 병합 검증 통과!")

def test_string_output():
    """
    레거시 vs 신규 STRING 병합 결과 비교
    """
    # 동일한 검증 로직
    pass
```

**Claude Code 지시**:
```
"tests/test_m4gl.py를 작성해줘.
위 코드를 참조하여 test_dialogue_output()과 test_string_output() 함수를 작성하세요."
```

### 3.2 NCGL 검증

**Claude Code 지시**:
```
"tests/test_ncgl.py를 작성해줘.
M4GL과 동일한 방식으로 레거시와 신규 출력 파일을 비교하세요."
```

### 3.3 LYGL 검증

**Claude Code 지시**:
```
"tests/test_lygl.py를 작성해줘.

1. Merge 검증: 레거시 vs 신규 출력 파일 비교
2. Split 검증: 레거시 vs 신규 출력 파일 비교
3. Round-trip 검증:
   - 원본 파일 7개 준비
   - Merge → 통합 파일 생성
   - Split → 7개 파일 복원
   - 원본 vs 복원 파일 100% 일치 확인
4. 단위 테스트 마이그레이션:
   - legacy/LY/src/test_*.py 복사
   - sebastian/core/lygl/ 경로 수정
   - pytest 실행 → 37개 테스트 통과 확인
"
```

---

## 📦 Task 4: 위저드 Dialog (LY/GL)

### 4.1 Merge Wizard

**참조**: `prd/Sebastian-UI-Wireframes.md` → "LY/GL Merge 위저드"

**Claude Code 지시**:
```
"sebastian/ui/wizards/merge_wizard.py를 작성해줘.

요구사항:
1. QDialog 상속 (600x500px)
2. 7개 파일 선택 (QFileDialog.getOpenFileNames)
3. 선택된 파일 목록 표시 (QListWidget)
4. 저장 위치 선택
5. [실행 →] 버튼 → LYGLWorker('merge') 시작
6. ProgressDialog 연결
"
```

### 4.2 Split Wizard

**참조**: `prd/Sebastian-UI-Wireframes.md` → "LY/GL Split 위저드"

**Claude Code 지시**:
```
"sebastian/ui/wizards/split_wizard.py를 작성해줘.

요구사항:
1. 통합 파일 선택 (YYMMDD_LYGL_StringALL.xlsx)
2. 저장 폴더 선택
3. 생성될 파일 미리보기
4. [실행 →] 버튼 → LYGLWorker('split') 시작
"
```

### 4.3 Batches Wizard

**참조**: `prd/Sebastian-UI-Wireframes.md` → "LY/GL Merge Batches 위저드"

**Claude Code 지시**:
```
"sebastian/ui/wizards/batches_wizard.py를 작성해줘.

요구사항:
1. 배치 폴더 목록 (QListWidget)
2. [+ 배치 폴더 추가] 버튼
3. 순서 변경 ([↑][↓] 버튼)
4. 기준 배치 선택 (라디오 버튼)
5. Status 자동 완료 체크박스
6. [실행 →] 버튼 → LYGLWorker('batches') 시작
"
```

### 4.4 Diff Wizard

**참조**: `prd/Sebastian-UI-Wireframes.md` → "LY/GL Legacy Diff 위저드"

**Claude Code 지시**:
```
"sebastian/ui/wizards/diff_wizard.py를 작성해줘.

요구사항:
1. 비교1 폴더 선택 (이전 버전)
2. 비교2 폴더 선택 (현재 버전)
3. 저장 위치 선택
4. 생성 파일명 미리보기 (YYYYMMDDHHMMSS_DIFF.xlsx)
5. [실행 →] 버튼 → LYGLWorker('diff') 시작
"
```

---

## 📦 Task 5: 메인 진입점

**Claude Code 지시**:
```
"sebastian/main.py를 작성해줘.

```python
import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow

def main():
    app = QApplication(sys.argv)

    # 전역 스타일시트 설정 (wireframe 색상 시스템)
    app.setStyleSheet('''
        QWidget {
            font-family: "Pretendard", "맑은 고딕", sans-serif;
            font-size: 13px;
            color: #212121;
        }
        /* ... wireframe의 스타일시트 예시 참조 ... */
    ''')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```
"
```

---

## 🧪 Phase 3 검증

### 검증 1: 기능 동작

**테스트 시나리오**:
```
1. sebastian.exe 실행
2. M4/GL 탭:
   - DIALOGUE 버튼 → 폴더 선택 → 실행 → 결과 파일 확인
   - STRING 버튼 → 폴더 선택 → 실행 → 결과 파일 확인
3. NC/GL 탭:
   - 날짜/마일스톤 입력 → 폴더 선택 → 실행 → 결과 파일 확인
4. LY/GL 탭:
   - Merge → 7개 파일 선택 → 실행 → 결과 파일 확인
   - Split → 통합 파일 선택 → 실행 → 7개 파일 확인
   - Batches → 배치 폴더 추가 → 실행 → 결과 파일 확인
   - Diff → 2개 폴더 선택 → 실행 → DIFF 파일 확인
```

### 검증 2: 출력 파일 일치

**자동 테스트**:
```bash
pytest tests/test_m4gl.py
pytest tests/test_ncgl.py
pytest tests/test_lygl.py
```

**예상 결과**:
```
tests/test_m4gl.py::test_dialogue_output PASSED
tests/test_m4gl.py::test_string_output PASSED
tests/test_ncgl.py::test_ncgl_output PASSED
tests/test_lygl.py::test_merge_output PASSED
tests/test_lygl.py::test_split_output PASSED
tests/test_lygl.py::test_round_trip PASSED
tests/test_lygl.py::test_unit_tests PASSED (37개 테스트)
```

### 검증 3: UI 반응성

**테스트 항목**:
- [ ] ProgressDialog 실시간 업데이트
- [ ] LogViewer에 로그 기록
- [ ] 에러 발생 시 에러 탭 자동 전환
- [ ] 작업 중 UI 프리징 없음
- [ ] 취소 버튼 동작 (선택적)

---

## 📊 Phase 3 완료 체크리스트

### Worker 클래스
- [ ] M4GLWorker 구현 및 테스트
- [ ] NCGLWorker 구현 및 테스트
- [ ] LYGLWorker 구현 및 테스트

### UI 연결
- [ ] M4GL 탭 연결
- [ ] NCGL 탭 연결
- [ ] LYGL 탭 연결
- [ ] 4개 위저드 Dialog 구현

### 검증
- [ ] M4GL 출력 파일 100% 일치
- [ ] NCGL 출력 파일 100% 일치
- [ ] LYGL Merge 출력 파일 100% 일치
- [ ] LYGL Split 출력 파일 100% 일치
- [ ] LYGL Round-trip 무결성 100%
- [ ] LYGL 37개 단위 테스트 통과

### 통합
- [ ] main.py 작성
- [ ] 전역 스타일시트 적용
- [ ] 모든 기능 정상 동작

---

## 📅 다음 단계

Phase 3 완료 후:

1. **PyInstaller 빌드**: sebastian.exe 생성
2. **사용자 문서 작성**: README.md
3. **배포 패키지 생성**: sebastian.exe + README.md

---

## 📚 참고 자료

- [Sebastian-Migration-Guide.md](Sebastian-Migration-Guide.md) - 전체 마이그레이션 개요
- [Sebastian-Phase1-Logic-Extraction.md](Sebastian-Phase1-Logic-Extraction.md)
- [Sebastian-Phase2-UI-Development.md](Sebastian-Phase2-UI-Development.md)
- PyQt6 QThread: https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html
