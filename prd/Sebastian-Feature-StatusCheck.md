# LY/GL Status Check 기능 설계서

**작성일**: 2025-12-23
**버전**: 1.0.0
**프로젝트**: Sebastian - LY Table 현지화 도구

---

## 1. 기능 개요

### 1.1 목적
언어별 파일의 **Status 값 통일 여부**를 검증하여, 모든 언어에서 일관된 번역 상태를 유지하도록 지원합니다.

### 1.2 핵심 요구사항
- 7개 언어 파일(EN, CT, CS, JA, TH, PT-BR, RU)의 Status 비교
- EN 파일을 기준으로 다른 6개 언어와 비교
- Status 불일치 키만 보고
- Legacy Diff와 유사한 Excel 출력 형식

### 1.3 사용 시나리오
```
1. 사용자가 LY/GL 탭 중앙의 "Status Check" 버튼 클릭
2. 7개 언어 파일 선택 다이얼로그 표시
3. 사용자가 EN, CT, CS, JA, TH, PT-BR, RU 파일 선택
4. EN 파일 기준으로 Status 비교
5. Status 불일치 키만 Overview 시트에 출력
6. Excel 파일로 결과 저장
```

---

## 2. UI 설계

### 2.1 버튼 배치

**위치**: LY/GL 탭 중앙 (2×2 그리드 중심)

```
┌────────────────────────────────────┐
│         LY/GL 탭 (보라색)          │
├─────────────┬─────────────┐
│   Merge     │    Split    │
│  (240×180)  │  (240×180)  │
├─────────────┼─────────────┤
│   Batch     │    Diff     │
│  (240×180)  │  (240×180)  │
└─────────────┴─────────────┘

        [Status Check]
         (120×40)
```

**버튼 스타일**:
```python
- 크기: 120 × 40
- 배경: #BA68C8 (보라)
- 텍스트: "Status Check"
- 폰트: Pretendard 11pt, bold
- 테두리: 1px solid #9C27B0
```

### 2.2 파일 선택 다이얼로그

**Wizard 스타일** (기존 Merge/Split/Batch/Diff와 동일)

```python
class StatusCheckWizard(QDialog):
    """7개 언어 파일 선택 위저드"""

    # 페이지 구성
    - 단일 페이지 (파일 선택만)

    # UI 요소
    - 타이틀: "Status Check - 언어 파일 선택"
    - 설명: "7개 언어 파일을 모두 선택해주세요"
    - 파일 선택 버튼 × 7:
      [EN 파일 선택] [파일명 표시]
      [CT 파일 선택] [파일명 표시]
      [CS 파일 선택] [파일명 표시]
      [JA 파일 선택] [파일명 표시]
      [TH 파일 선택] [파일명 표시]
      [PT-BR 파일 선택] [파일명 표시]
      [RU 파일 선택] [파일명 표시]
    - 출력 파일 선택: [Browse...]
    - 버튼: [Cancel] [Start]
```

**검증 규칙**:
- 7개 파일이 모두 선택되어야 함
- 각 파일은 xlsx 형식이어야 함
- 출력 파일 경로가 지정되어야 함

---

## 3. 핵심 로직 설계

### 3.1 데이터 구조

**입력**:
```python
{
    'EN': Path('251201_EN.xlsx'),
    'CT': Path('251201_CT.xlsx'),
    'CS': Path('251201_CS.xlsx'),
    'JA': Path('251201_JA.xlsx'),
    'TH': Path('251201_TH.xlsx'),
    'PT-BR': Path('251201_PT-BR.xlsx'),
    'RU': Path('251201_RU.xlsx')
}
```

**각 파일 구조** (LY Table Split 파일):
```
| KEY        | Source | Target | Status   |
|------------|--------|--------|----------|
| KEY_001    | Hello  | 안녕    | 완료     |
| KEY_002    | World  | 세계    | 번역필요  |
```

**Status 값**:
- "번역필요" (Translation Needed)
- "완료" (Completed)
- "수정" (Revised)
- "기존" (Existing)

### 3.2 비교 알고리즘

```python
def check_status_consistency(
    files: Dict[str, Path],
    progress_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Status 통일 여부 검증

    Args:
        files: {언어코드: Path}
        progress_callback: (percent, message)

    Returns:
        [
            {
                'key': 'KEY_001',
                'statuses': {
                    'EN': '완료',
                    'CT': '완료',
                    'CS': '번역필요',  # 불일치!
                    'JA': '완료',
                    'TH': '완료',
                    'PT-BR': '완료',
                    'RU': '완료'
                },
                'is_consistent': False
            },
            ...
        ]
    """

    # Step 1: EN 파일 읽기 (기준)
    en_data = read_excel_file(files['EN'])
    en_keys = {row['KEY']: row['Status'] for row in en_data}

    # Step 2: 다른 언어 파일 읽기
    all_data = {'EN': en_data}
    for lang in ['CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']:
        all_data[lang] = read_excel_file(files[lang])

    # Step 3: 각 KEY별 Status 비교
    results = []
    for key in en_keys.keys():
        statuses = {}
        for lang in VALID_LANGUAGES:
            # 해당 언어 파일에서 KEY 찾기
            row = find_row_by_key(all_data[lang], key)
            statuses[lang] = row['Status'] if row else 'Missing'

        # 일치 여부 확인
        unique_statuses = set(statuses.values())
        is_consistent = len(unique_statuses) == 1

        # 불일치하는 경우만 결과에 추가
        if not is_consistent:
            results.append({
                'key': key,
                'statuses': statuses,
                'is_consistent': False
            })

    return results
```

### 3.3 출력 형식

**Excel 파일 구조**:
- **시트**: Overview만 (언어별 시트 없음)

**Overview 시트**:
```
| #  | KEY     | EN      | CT      | CS       | JA     | TH     | PT-BR  | RU     |
|----|---------|---------|---------|----------|--------|--------|--------|--------|
| 1  | KEY_001 | 완료    | 완료    | 번역필요 | 완료   | 완료   | 완료   | 완료   |
| 2  | KEY_005 | 수정    | 완료    | 완료     | 완료   | 완료   | 완료   | 완료   |
| 3  | KEY_012 | 기존    | 기존    | 기존     | 기존   | 기존   | Missing| 기존   |
```

**스타일 지정**:
- 헤더: 파란색 배경 (#DBEEF4), Bold
- 일치하지 않는 셀: 노란색 배경 (#FFEB3B)
- Missing 셀: 빨간색 배경 (#FFCDD2)
- 폰트: Calibri 11pt
- 정렬: 중앙 정렬

**컬럼 너비**:
```python
ws.column_dimensions['A'].width = 6   # #
ws.column_dimensions['B'].width = 50  # KEY
ws.column_dimensions['C'].width = 12  # EN
ws.column_dimensions['D'].width = 12  # CT
ws.column_dimensions['E'].width = 12  # CS
ws.column_dimensions['F'].width = 12  # JA
ws.column_dimensions['G'].width = 12  # TH
ws.column_dimensions['H'].width = 14  # PT-BR
ws.column_dimensions['I'].width = 12  # RU
```

---

## 4. 구현 파일 설계

### 4.1 파일 구조

```
sebastian/
├── core/
│   └── lygl/
│       ├── status_check.py          # 신규: Status 검증 로직
│       └── __init__.py               # 업데이트: status_check export
├── ui/
│   ├── lygl_tab.py                   # 업데이트: Status Check 버튼 추가
│   └── wizards/
│       ├── status_check_wizard.py    # 신규: 7개 파일 선택 위저드
│       └── __init__.py               # 업데이트: StatusCheckWizard export
└── workers/
    ├── lygl_worker.py                # 업데이트: LYGLStatusCheckWorker 추가
    └── __init__.py                   # 업데이트: Worker export
```

### 4.2 핵심 모듈

#### `core/lygl/status_check.py`

```python
"""
Status Check 모듈

7개 언어 파일의 Status 통일 여부를 검증합니다.
"""

from pathlib import Path
from typing import Dict, List, Optional, Callable
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font, Alignment

VALID_LANGUAGES = ['EN', 'CT', 'CS', 'JA', 'TH', 'PT-BR', 'RU']


def read_language_file(file_path: Path) -> List[Dict]:
    """
    언어 파일 읽기

    Returns:
        [{'KEY': '...', 'Source': '...', 'Target': '...', 'Status': '...'}]
    """
    pass


def check_status_consistency(
    files: Dict[str, Path],
    progress_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Status 통일 여부 검증
    """
    pass


def create_status_check_output(
    inconsistencies: List[Dict],
    output_path: Path,
    progress_callback: Optional[Callable] = None
) -> None:
    """
    Status Check 결과를 Excel로 출력

    Args:
        inconsistencies: check_status_consistency() 결과
        output_path: 출력 파일 경로
    """
    pass
```

#### `ui/wizards/status_check_wizard.py`

```python
"""
Status Check 위저드

7개 언어 파일을 선택하고 출력 파일을 지정합니다.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from pathlib import Path


class StatusCheckWizard(QDialog):
    """Status Check 파일 선택 위저드"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Status Check - 언어 파일 선택")
        self.resize(600, 500)
        self._setup_ui()

    def _setup_ui(self):
        """UI 설정"""
        pass

    def get_data(self) -> Dict:
        """
        선택된 파일 정보 반환

        Returns:
            {
                'files': {
                    'EN': Path,
                    'CT': Path,
                    ...
                },
                'output': Path
            }
        """
        pass
```

#### `workers/lygl_worker.py` (업데이트)

```python
class LYGLStatusCheckWorker(QThread):
    """Status Check Worker"""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, files: Dict[str, Path], output: Path):
        super().__init__()
        self.files = files
        self.output = output

    def run(self):
        """Status Check 실행"""
        try:
            from core.lygl import check_status_consistency, create_status_check_output

            # Step 1: Status 검증
            self.status_updated.emit("Status 검증 중...")
            inconsistencies = check_status_consistency(
                self.files,
                self._progress_callback
            )

            # Step 2: 결과 출력
            self.status_updated.emit("결과 파일 생성 중...")
            create_status_check_output(
                inconsistencies,
                self.output,
                self._progress_callback
            )

            self.finished.emit(True, f"완료! 불일치 키: {len(inconsistencies)}개")

        except Exception as e:
            self.finished.emit(False, str(e))

    def _progress_callback(self, percent: int, message: str):
        """진행 상황 콜백"""
        self.progress_updated.emit(percent)
        self.status_updated.emit(message)
```

#### `ui/lygl_tab.py` (업데이트)

```python
class LYGLTab(QWidget):
    """LY/GL 탭"""

    # Signal 추가
    status_check_requested = pyqtSignal()

    def _setup_ui(self):
        """UI 설정"""
        # ... 기존 코드 ...

        # Status Check 버튼 추가 (중앙 하단)
        status_check_btn = QPushButton("Status Check")
        status_check_btn.setFixedSize(120, 40)
        status_check_btn.setFont(QFont("Pretendard", 11, QFont.Weight.Bold))
        status_check_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #BA68C8,
                    stop:1 #9C27B0
                );
                color: white;
                border: 1px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #CE93D8,
                    stop:1 #BA68C8
                );
            }}
        """)
        status_check_btn.clicked.connect(self.status_check_requested.emit)

        # ... 레이아웃에 추가 ...

    def _connect_signals(self):
        """Signal 연결"""
        # ... 기존 코드 ...
        self.status_check_requested.connect(self._show_status_check_wizard)

    def _show_status_check_wizard(self):
        """Status Check 위저드 표시"""
        from .wizards import StatusCheckWizard

        wizard = StatusCheckWizard(self)
        if wizard.exec():
            data = wizard.get_data()
            # Worker 실행
            self.worker = LYGLStatusCheckWorker(data['files'], data['output'])
            self._run_worker(self.worker, "LY/GL Status Check")
```

---

## 5. 구현 순서

### Phase 1: 핵심 로직 (core)
1. ✅ `core/lygl/status_check.py` 생성
   - `read_language_file()` 구현
   - `check_status_consistency()` 구현
   - `create_status_check_output()` 구현

2. ✅ `core/lygl/__init__.py` 업데이트
   - `status_check` 함수들 export

### Phase 2: UI (wizards)
3. ✅ `ui/wizards/status_check_wizard.py` 생성
   - 7개 파일 선택 UI
   - 출력 파일 선택 UI
   - 검증 로직

4. ✅ `ui/wizards/__init__.py` 업데이트
   - `StatusCheckWizard` export

### Phase 3: Worker
5. ✅ `workers/lygl_worker.py` 업데이트
   - `LYGLStatusCheckWorker` 클래스 추가

6. ✅ `workers/__init__.py` 업데이트
   - Worker export

### Phase 4: 탭 통합
7. ✅ `ui/lygl_tab.py` 업데이트
   - Status Check 버튼 추가
   - Signal/Slot 연결
   - Worker 실행

### Phase 5: 테스트
8. ✅ 실제 데이터로 테스트
   - 7개 언어 파일 준비
   - Status 불일치 시나리오 테스트
   - 출력 파일 검증

---

## 6. 테스트 시나리오

### 6.1 정상 케이스

**입력**:
- 7개 언어 파일 모두 선택됨
- 모든 파일이 유효한 xlsx 형식
- 출력 경로 지정됨

**예상 결과**:
- Status 불일치 키만 Overview에 표시
- 각 언어별 Status 값이 정확히 표시됨
- 스타일이 올바르게 적용됨

### 6.2 엣지 케이스

**Case 1: 파일 누락**
- 입력: 6개 파일만 선택
- 예상: Wizard에서 "7개 파일이 모두 필요합니다" 경고

**Case 2: KEY 누락**
- 입력: 특정 언어 파일에 KEY가 없음
- 예상: 해당 언어 컬럼에 "Missing" 표시

**Case 3: 모든 Status 일치**
- 입력: 모든 KEY의 Status가 일치
- 예상: "Status 불일치가 없습니다" 메시지, 빈 Overview 시트

### 6.3 성능 테스트

**대용량 파일**:
- KEY 10,000개 파일
- 목표: 30초 이내 처리
- 진행 상황 실시간 업데이트

---

## 7. 예상 이슈 및 해결 방안

### Issue 1: KEY 순서 불일치
**문제**: 언어별 파일의 KEY 순서가 다를 수 있음
**해결**: 딕셔너리로 KEY 매핑하여 순서 무관하게 비교

### Issue 2: Status 값 대소문자
**문제**: "완료" vs "Complete" 같은 다국어 Status
**해결**: EN 파일 기준으로 통일, 또는 Status 값 정규화

### Issue 3: 파일 형식 차이
**문제**: 컬럼명이 다를 수 있음
**해결**: 첫 행에서 KEY, Source, Target, Status 컬럼 위치 자동 감지

---

## 8. 향후 확장 가능성

### 8.1 자동 수정 기능
- Status 불일치 키에 대해 EN 기준으로 자동 통일
- "Apply EN Status to All" 버튼

### 8.2 상세 보고서
- 각 언어별 불일치 통계
- Status 값 분포 차트

### 8.3 Batch 통합
- Batch 단위로 Status Check 실행
- 여러 배치의 Status 비교

---

## 9. 완료 기준

### ✅ 기능 완성
- [ ] 7개 파일 선택 다이얼로그 동작
- [ ] Status 비교 로직 정상 동작
- [ ] Excel 출력 형식 정확
- [ ] 스타일 적용 완료

### ✅ 품질 검증
- [ ] 실제 데이터 테스트 성공
- [ ] 엣지 케이스 처리 확인
- [ ] 성능 목표 달성 (10,000개 KEY < 30초)

### ✅ 문서화
- [ ] 설계서 작성 완료 (본 문서)
- [ ] 사용자 가이드 작성
- [ ] 코드 주석 추가

---

**설계 완료일**: 2025-12-23
**설계자**: Claude Code
**승인**: [대기]
