# Sebastian Project

**프로젝트**: 3개 게임 현지화 도구 통합 (M4/GL, NC/GL, LY/GL)
**버전**: v0.2.0 (2025-12-24 UI/UX 개선 완료)

---

## 🎯 프로젝트 현황

### 📊 코드베이스 규모

- **총 파일**: 40개 Python 파일 (~8,500 lines)
- **Core 로직**: ~3,500 lines (비즈니스 로직)
- **UI 코드**: ~2,800 lines (PyQt6 v2 디자인)
- **Workers**: ~1,000 lines (비동기 처리)
- **테스트**: ~1,000 lines (LY/GL 37개)
- **디자인 시스템**: ~200 lines (design_tokens.py + minimal.qss)

---

## 🏗️ 아키텍처 원칙

### 1. 3계층 구조 (UI/Worker/Core)

```
┌─────────────────────────────────────────┐
│         UI Layer (PyQt6 v2)              │
│  - MainWindow (탭 시스템)                │
│  - M4GLTab, NCGLTab, LYGLTab            │
│  - 공통 컴포넌트 (ProgressDialog, etc)   │
│  - 디자인 토큰 + QSS 스타일시트          │
└──────────────┬──────────────────────────┘
               │ Signal/Slot
               ▼
┌─────────────────────────────────────────┐
│      Worker Layer (QThread)              │
│  - M4GLWorker, NCGLWorker, LYGLWorker   │
│  - 비동기 작업, 진행 상황 업데이트        │
└──────────────┬──────────────────────────┘
               │ progress_queue
               ▼
┌─────────────────────────────────────────┐
│       Core Layer (Business Logic)        │
│  - core/m4gl/, core/ncgl/, core/lygl/   │
│  - 데이터 처리, 검증, Excel I/O           │
└─────────────────────────────────────────┘
```

**핵심 규칙**:
- ✅ UI는 Worker만 호출 (Core 직접 호출 금지)
- ✅ Worker는 Core 로직 호출 후 Signal로 UI 업데이트
- ✅ Core는 UI/Worker 의존성 없음 (순수 로직)

### 2. UI/UX v2 디자인 시스템

**디자인 철학**: Less is More, 명확한 계층, 충분한 여백

**디자인 토큰 (`sebastian/ui/common/design_tokens.py`)**:
```python
class DesignTokens:
    # 브랜드 색상 (통일)
    PRIMARY = "#5E35B1"           # Deep Purple 600
    PRIMARY_LIGHT = "#7E57C2"     # hover
    PRIMARY_DARK = "#4527A0"      # pressed

    # 중립 색상
    BG_PRIMARY = "#FFFFFF"
    TEXT_PRIMARY = "#1F2937"
    BORDER = "#E5E7EB"

    # 상태 색상
    SUCCESS = "#10B981"
    ERROR = "#EF4444"
    WARNING = "#F59E0B"

    # 간격 (8pt Grid)
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XXL = 48
```

**QSS 스타일시트 (`sebastian/ui/styles/minimal.qss`)**:
- Material Design 3.0 기반
- 모든 위젯 스타일 중앙 관리
- objectName 기반 스타일 변형

### 3. Signal/Slot 패턴

**표준 Signal 체계**:
```python
class SomeWorker(QThread):
    # 필수 Signals
    progress_updated = pyqtSignal(int)        # 0-100 진행률
    status_updated = pyqtSignal(str)          # 상태 메시지
    completed = pyqtSignal(str)               # 완료 메시지
    error_occurred = pyqtSignal(str)          # 에러 메시지
```

**금지 사항**:
- ❌ Signal 체인 깊이 >3 (디버깅 어려움)
- ❌ UI 스레드에서 긴 작업 (블로킹 발생)

### 4. Wizard 패턴 (복잡한 입력 흐름)

**적용 대상**: LY/GL 전용 (Merge, Split, Batch, Diff, StatusCheck)

**표준 구조**:
```python
class SomeWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)  # 모달 Dialog
        self._setup_ui()
        self._connect_signals()

    def get_data(self) -> Dict[str, Any]:
        """선택된 데이터 반환"""
        return {
            'input_files': self.selected_files,
            'output_path': self.output_path,
        }
```

---

## 📝 코딩 표준

### 1. 타입 힌트 필수

```python
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd

def merge_dialogue(
    folder_path: str,
    progress_queue: queue.Queue
) -> Tuple[pd.DataFrame, str]:
    """M4/GL DIALOGUE 3개 파일 병합

    Args:
        folder_path: 폴더 경로
        progress_queue: 진행 상황 Queue

    Returns:
        (병합 DataFrame, 출력 파일 경로)

    Raises:
        ValidationError: 파일 수 부족 시
        IOError: 파일 읽기/쓰기 실패 시
    """
```

### 2. UI 스타일 작성 규칙 (v2)

**QSS 우선 사용**:
```python
# ✅ 권장: QSS objectName 사용
btn = QPushButton()
btn.setObjectName("cardButton")  # QSS에서 스타일 정의

# ❌ 비권장: 인라인 setStyleSheet()
btn.setStyleSheet("background-color: #5E35B1;")
```

**동적 스타일 변경 (property 활용)**:
```python
# 선택 상태 변경
btn.setProperty("selected", True)
btn.style().unpolish(btn)  # 스타일 새로고침
btn.style().polish(btn)
```

### 3. 네이밍 컨벤션

| 항목 | 패턴 | 예시 |
|------|------|------|
| 파일명 | snake_case | `merge_wizard.py` |
| 클래스 | PascalCase + 접미사 | `M4GLWorker`, `MergeWizard` |
| 함수 | snake_case | `merge_dialogue()` |
| 상수 | UPPER_CASE | `MAX_FILES = 7` |
| Private | `_` 접두사 | `_setup_ui()` |
| objectName | camelCase | `cardButton`, `listItemButton` |

---

## 🚫 금지 사항

### 1. 아키텍처 위반

❌ **UI에서 Core 직접 호출**
```python
# 잘못된 예
def on_button_click(self):
    result = merge_dialogue(folder_path)  # ❌ UI 블로킹!
```

✅ **올바른 예**
```python
def on_button_click(self):
    worker = M4GLWorker(folder_path)
    worker.completed.connect(self._on_completed)
    worker.start()  # ✅ 비동기 실행
```

### 2. UI 스타일 작성 방식

❌ **비권장: 인라인 스타일**
```python
btn.setStyleSheet("background-color: #5E35B1; border-radius: 8px;")
```

✅ **권장: QSS objectName**
```python
btn.setObjectName("secondaryButton")  # minimal.qss에서 정의됨
```

---

## 🎨 UI/UX 디자인 가이드

### 탭별 UI 특징

**M4/GL 탭**:
- 카드 스타일 버튼 (240×200px)
- objectName: `cardButton`
- 선택 시: property `selected=true`
- 간격: 48px (카드 간)

**NC/GL 탭**:
- 실시간 입력 검증
- objectName: `validInput` / `invalidInput`
- 검증 아이콘: ✓ (초록) / ✗ (빨강)
- 입력 필드 높이: 48px

**LY/GL 탭**:
- 수직 리스트 (64px × 5개)
- objectName: `listItemButton`
- 화살표 아이콘: `→`
- 간격: 12px (버튼 간)
- **확장성**: 새 기능 추가 시 동일 스타일로 하단에 추가

### 공통 컴포넌트

**ProgressDialog**:
- 크기: 500 × 280px
- 진행 바: 높이 8px, Primary 색상
- 버튼: 취소, 최소화 (secondaryButton)

**LogViewer**:
- 펼침: 200px, 접힘: 32px
- 탭: 로그, 에러, 경고
- 최대 1000줄 (초과 시 자동 삭제)

---

## 🔧 개발 가이드라인

### 새 게임 추가 (예: XYZ/GL)

**체크리스트**:

1. **Core 로직** (`core/xyzgl/`)
2. **Worker** (`workers/xyzgl_worker.py`)
3. **탭** (`ui/xyzgl_tab.py`)
4. **MainWindow 통합**
5. **QSS 스타일 추가** (필요시)

### 새 기능 추가

**예시**: LY/GL에 "Validate" 기능 추가

**체크리스트**:

1. **Core 로직** (`core/lygl/validate.py`)
2. **Worker** (`workers/lygl_worker.py` - ValidateWorker 추가)
3. **Wizard** (`ui/wizards/validate_wizard.py`)
4. **탭 통합** (`ui/lygl_tab.py` - 버튼 1개 추가)

```python
# ui/lygl_tab.py의 _setup_ui()
functions = [
    # ... 기존 5개 ...
    ("Validate", "파일 검증", "컬럼 및 데이터 형식 검사", self.validate_requested.emit),
]
```

### UI 스타일 변경

**1단계**: `sebastian/ui/common/design_tokens.py` 수정
```python
PRIMARY = "#YOUR_COLOR"  # 브랜드 색상 변경
```

**2단계**: `sebastian/ui/styles/minimal.qss` 수정 (필요시)
```css
QPushButton {
    border-radius: 12px;  /* 둥근 모서리 조정 */
}
```

**3단계**: Python 코드 수정 **불필요** (QSS 재로드 자동)

---

## 📚 참고 문서

### PRD (Product Requirements Document)

**위치**: `prd/` 디렉토리

| 파일 | 용도 |
|------|------|
| **PRD-Overview.md** | 전체 개요, 아키텍처, 기술 스택 |
| **PRD-M4GL.md** | M4/GL 상세 (DIALOGUE/STRING) |
| **PRD-NCGL.md** | NC/GL 상세 (8개 언어, 병렬 처리) |
| **PRD-LYGL.md** | LY/GL 상세 (5개 기능) |
| **PRD-UI-Design.md** | UI/UX 디자인 시스템 |

### 사용자 가이드

**위치**: `docs/user-guide.html`
- Confluence 게시용 HTML
- PM/기획자 타겟 (비기술직)
- 단계별 사용법, FAQ 포함

### 레거시 참조

**위치**: `legacy/` 디렉토리 (읽기 전용)
- M4/Merged_M4.py: M4/GL 원본 로직
- NC/NC 파일 통합.py: NC/GL 원본 로직
- LY/LY_Table/: LY/GL 원본 로직

**주의**: 레거시 코드는 읽기 전용! 수정 금지.

---

## 🔄 작업 흐름

### 일반적인 개발 프로세스

```
1. 요구사항 분석
   - PRD 확인
   - 기존 패턴 참조 (3계층, Signal/Slot, Wizard)
   - 정보 수집 후 → Serena의 think_about_collected_information 호출
   ↓
2. 설계
   - 아키텍처 결정 (3계층 준수)
   - Signal/Slot 정의
   - UI 디자인 (objectName 정의)
   ↓
3. 구현
   - 코드 작성 전 → Serena의 think_about_task_adherence 호출
   - Core 로직 작성 (타입 힌트 + Docstring)
   - Worker 작성 (QThread)
   - UI 작성 (objectName, QSS 활용)
   - 작업 완료 시 → Serena의 think_about_whether_you_are_done 호출
   ↓
4. 테스트
   - 단위 테스트 작성
   - 통합 테스트
   - 출력 파일 검증 (레거시 비교)
   ↓
5. 검증
   - pytest 실행
   - 수동 UI 테스트
   - 레거시 비교 (출력 파일)
   ↓
6. 문서화
   - Docstring 업데이트
   - PRD 업데이트 (필요 시)
```

### Git 워크플로우

```bash
# 1. Feature 브랜치 생성
git checkout -b feature/새기능명

# 2. 개발 및 커밋
git add .
git commit -m "feat: 새 기능 설명"

# 3. 테스트
pytest tests/

# 4. Push & PR
git push origin feature/새기능명
```

---

## 💡 모범 사례 (Best Practices)

### 1. UI 컴포넌트 작성 (v2 스타일)

```python
def _create_custom_button(self):
    """커스텀 버튼 생성 - QSS 기반"""
    btn = QPushButton("버튼 텍스트")
    btn.setObjectName("customButton")  # QSS에서 정의
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn
```

### 2. 동적 스타일 변경

```python
def _update_state(self, is_selected: bool):
    """상태 변경 - property 활용"""
    self.btn.setProperty("selected", is_selected)
    self.btn.style().unpolish(self.btn)
    self.btn.style().polish(self.btn)
```

### 3. Worker 작성 패턴

```python
class SomeWorker(QThread):
    """작업 Worker

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

    def run(self):
        """QThread.run 오버라이드"""
        try:
            result = some_core_function()
            self.completed.emit(f"완료: {result}")
        except Exception as e:
            self.error_occurred.emit(f"실패: {e}")
```

---

## 🔍 문제 해결 가이드

### UI가 멈춤 (블로킹)

**원인**: UI 스레드에서 긴 작업 실행
**해결**: Worker로 분리

```python
# ✅ 올바른 예
def on_click(self):
    worker = ProcessWorker()
    worker.start()  # 별도 스레드
```

### QSS 스타일이 적용 안 됨

**원인 1**: objectName 누락
**해결**: `setObjectName()` 호출

**원인 2**: 스타일 새로고침 필요
**해결**: `style().unpolish()` + `polish()` 호출

### 출력 파일이 레거시와 다름

**원인**: Core 로직 수정
**해결**:
1. git diff로 변경사항 확인
2. 레거시 로직 복원
3. 새 기능은 별도 함수로

---

## 📊 성공 기준

### 코드 품질

- [ ] 모든 함수에 타입 힌트
- [ ] 모든 클래스/함수에 Docstring
- [ ] 테스트 커버리지 ≥80%
- [ ] QSS 기반 스타일 (인라인 최소화)

### 아키텍처

- [ ] 3계층 구조 준수 (UI/Worker/Core)
- [ ] Signal/Slot 패턴 일관성
- [ ] UI 스레드 블로킹 없음
- [ ] 레거시 로직 보존

### UI/UX

- [ ] 디자인 토큰 일관성
- [ ] Primary 색상 통일 (#5E35B1)
- [ ] 8pt Grid System 준수
- [ ] 접근성 (WCAG AA)

### 검증

- [ ] 출력 파일 = 레거시 출력 (기존 기능)
- [ ] 단위 테스트 통과
- [ ] UI 테스트 완료

---

## 📞 프로젝트 정보

**저장소**: https://github.com/JaekyungCho2140/sebastianmk2
**최신 릴리즈**: v0.2.0 (2025-12-24, UI/UX v2)
**라이선스**: (명시 필요)
**개발자**: Jaekyung Cho

**문서**:
- PRD: `prd/` 디렉토리 (5개)
- 사용자 가이드: `docs/user-guide.html`
- 레거시 백업: `prd_backup/` 디렉토리

**로깅 시스템**:
- **로그 위치**: `logs/sebastian.log` (현재 월)
- **로테이션**: 매월 1일 자정 (sebastian.log.YYYYMM)
- **보관 정책**: 무제한 (삭제 안 함)
- **형식**: `시간 - 모듈 - 레벨 - 메시지`
- **설정**: `sebastian/main.py` - `setup_logging()`

---

**이 문서는 Sebastian v0.2.0 (UI/UX) 기준으로 작성되었습니다.**
**PRD 및 사용자 가이드를 참고하여 프로젝트를 확장해주세요!**
