# Sebastian PRD - 전체 개요

**프로젝트명**: Sebastian
**버전**: v0.1.1
**작성일**: 2025-12-24
**상태**: Production

---

## 문서 구조

이 PRD는 모듈화된 구조로 작성되었습니다:

| 문서 | 역할 |
|------|------|
| **PRD-Overview.md** (이 문서) | 프로젝트 전체 개요 및 아키텍처 |
| **PRD-M4GL.md** | M4/GL 기능 상세 스펙 (DIALOGUE/STRING 병합) |
| **PRD-NCGL.md** | NC/GL 기능 상세 스펙 (8개 언어 병합) |
| **PRD-LYGL.md** | LY/GL 기능 상세 스펙 (Merge/Split/Batches/Diff/StatusCheck) |
| **PRD-UI-Design.md** | UI/UX v2 디자인 시스템 및 컴포넌트 |

---

## 프로젝트 목적

### 핵심 목표

**3개 게임의 현지화 테이블 관리 도구를 단일 통합 프로그램으로 통합**

게임 퍼블리셔 L10n(Localization)팀에서 실무에 사용하는 현지화 도구들을 통합하여, 사용자 경험을 개선하고 유지보수 효율성을 높입니다.

### 해결하려는 문제

1. **도구 분산**: 3개 게임 각각의 독립 Python 스크립트 실행 → 번거로움
2. **기술 스택 불일치**: tkinter/customtkinter 혼재 → 비일관적 사용자 경험
3. **중복 코드**: 진행도 표시, 파일 선택, 검증 로직 중복 → 유지보수 부담
4. **확장성 부족**: 새 게임 추가 시 새로운 독립 도구 개발 필요

### 달성 기준

- ✅ 단일 실행 파일(.exe)로 3개 게임 기능 제공
- ✅ 통합된 PyQt6 기반 모던 미니멀 UI/UX
- ✅ 레거시 기능 100% 동작 보장 (출력 파일 일치)
- ✅ 공통 컴포넌트 재사용으로 중복 코드 제거
- ✅ 빌드 크기 최적화 (2.7GB → 89MB, 96.7% 감소)

---

## 지원 게임 및 기능

### 1. M4/GL (MIR4 Global)

**기능**:
- **DIALOGUE 병합**: 3개 파일 → 1개 통합 (23개 컬럼)
- **STRING 병합**: 8개 파일 → 1개 통합 (15개 컬럼)

**특징**:
- NPC 매핑 기능 (NPC ID → Speaker Name)
- Excel 서식 지정 (폰트, 색상, 테두리)
- 진행 상황 실시간 표시

**상세 문서**: [PRD-M4GL.md](PRD-M4GL.md)

### 2. NC/GL (NC Global)

**기능**:
- **8개 언어 병합**: 언어별 8개 파일 → 1개 통합

**특징**:
- 병렬 처리 (ProcessPoolExecutor)
- 날짜/마일스톤 입력 (실시간 검증)
- xlsxwriter 기반 고속 저장
- 자동 셀 서식 지정

**상세 문서**: [PRD-NCGL.md](PRD-NCGL.md)

### 3. LY/GL (LY Table)

**기능**:
- **Merge**: 7개 언어 파일 → 1개 통합
- **Split**: 1개 통합 파일 → 7개 언어 분리
- **Batches**: 배치 병합 + Status 자동 완료 처리
- **Diff**: 두 버전 비교 → 변경 사항 추적
- **Status Check**: 언어별 Status 일치 검증

**특징**:
- Round-trip 무결성 보장 (Merge → Split → Merge)
- 데이터 검증 (KEY, Table, Source 일치)
- 37개 단위 테스트 통과

**상세 문서**: [PRD-LYGL.md](PRD-LYGL.md)

---

## 전체 아키텍처

### 3계층 구조 (UI/Worker/Core)

```
┌─────────────────────────────────────────┐
│         UI Layer (PyQt6)                 │
│  - MainWindow (탭 시스템)                │
│  - M4GLTab, NCGLTab, LYGLTab            │
│  - 공통 컴포넌트 (ProgressDialog, etc)   │
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

**핵심 원칙**:
- ✅ UI는 Worker만 호출 (Core 직접 호출 금지)
- ✅ Worker는 Core 로직 호출 후 Signal로 UI 업데이트
- ✅ Core는 UI/Worker 의존성 없음 (순수 로직)

### 디렉토리 구조

```
sebastian/
├── main.py                    # 엔트리포인트
├── requirements.txt           # 의존성 목록
├── build.spec                 # PyInstaller 빌드 스펙
│
├── ui/                        # UI Layer
│   ├── main_window.py         # 메인 창
│   ├── m4gl_tab.py            # M4/GL 탭
│   ├── ncgl_tab.py            # NC/GL 탭
│   ├── lygl_tab.py            # LY/GL 탭
│   │
│   ├── common/                # 공통 컴포넌트
│   │   ├── design_tokens.py  # 디자인 토큰
│   │   ├── colors.py         # 색상 정의
│   │   ├── progress_dialog.py # 진행 Dialog
│   │   └── log_viewer.py     # 로그 뷰어
│   │
│   ├── wizards/               # LY/GL Wizard들
│   │   ├── merge_wizard.py
│   │   ├── split_wizard.py
│   │   ├── batch_wizard.py
│   │   ├── diff_wizard.py
│   │   └── status_check_wizard.py
│   │
│   └── styles/
│       └── minimal.qss        # QSS 스타일시트
│
├── workers/                   # Worker Layer
│   ├── m4gl_worker.py         # M4/GL Worker
│   ├── ncgl_worker.py         # NC/GL Worker
│   └── lygl_worker.py         # LY/GL Workers
│
├── core/                      # Core Layer
│   ├── m4gl/                  # M4/GL 비즈니스 로직
│   │   ├── dialogue.py
│   │   └── string.py
│   │
│   ├── ncgl/                  # NC/GL 비즈니스 로직
│   │   └── merger.py
│   │
│   └── lygl/                  # LY/GL 비즈니스 로직
│       ├── merge.py
│       ├── split.py
│       ├── batch_merger.py
│       ├── legacy_diff.py
│       ├── status_check.py
│       ├── validator.py
│       ├── excel_format.py
│       └── error_messages.py
│
└── tests/                     # 테스트
    └── test_lygl_roundtrip.py # LY/GL Round-trip 테스트
```

---

## 기술 스택

### UI 프레임워크

**PyQt6** (v6.4.0+)
- 이유: 크로스 플랫폼, 성능, 네이티브 룩앤필
- Signal/Slot 패턴으로 비동기 처리
- QSS 스타일시트로 모던 UI

### Excel 처리

**pandas** (v1.3.0+)
- DataFrame 기반 데이터 처리
- 강력한 데이터 검증 및 변환

**openpyxl** (v3.0.0+)
- Excel 파일 읽기/쓰기
- 셀 서식 지정 (Font, PatternFill, Border)

**xlsxwriter** (NC/GL 전용)
- 고속 Excel 쓰기
- 대용량 파일 최적화

### 비동기 처리

**QThread**
- UI 블로킹 방지
- Signal/Slot으로 진행 상황 업데이트
- 레거시의 threading/ProcessPoolExecutor 대체

### 배포

**PyInstaller**
- 단일 실행 파일(.exe) 생성
- --onefile 옵션으로 배포 간소화
- 최적화: 2.7GB → 89MB (96.7% 감소)

### 테스팅

**pytest** (v7.0.0+)
- 단위 테스트 (LY/GL 37개)
- Round-trip 무결성 검증

---

## UI/UX 디자인

### 디자인 철학

**모던 미니멀** (Material Design 3.0 기반)

- **Less is More**: 불필요한 요소 제거
- **명확한 계층**: 타이포그래피, 간격, 색상으로 계층 구분
- **충분한 여백**: 8pt Grid System (8px, 16px, 24px, 48px)
- **일관된 브랜드 색상**: Deep Purple (#5E35B1)

### 디자인 토큰

**색상**:
- Primary: `#5E35B1` (Deep Purple 600)
- Background: `#FFFFFF`, `#F8F9FA`, `#F3F4F6`
- Text: `#1F2937` (Gray 800), `#6B7280` (Gray 500)
- Semantic: Success `#10B981`, Error `#EF4444`

**간격**: 8pt Grid System
- XXS: 2px, XS: 4px, SM: 8px, MD: 16px, LG: 24px, XL: 32px, XXL: 48px

**타이포그래피**:
- Font: Pretendard, Segoe UI, SF Pro
- Size: 11px (caption), 13px (body), 15px (subheading), 18px (heading)

**상세 문서**: [PRD-UI-Design.md](PRD-UI-Design.md)

---

## Signal/Slot 패턴

### 표준 Signal 체계

모든 Worker는 다음 Signal을 구현:

```python
class SomeWorker(QThread):
    # 필수 Signals
    progress_updated = pyqtSignal(int)        # 0-100 진행률
    status_updated = pyqtSignal(str)          # 상태 메시지
    completed = pyqtSignal(str)               # 완료 메시지
    error_occurred = pyqtSignal(str)          # 에러 메시지

    # 옵션 Signals (기능별)
    step_updated = pyqtSignal(str)            # 단계 정보 (예: "1/3")
    file_updated = pyqtSignal(str)            # 처리 중인 파일명
    files_count_updated = pyqtSignal(int)     # 처리된 파일 수
```

### Queue 기반 진행 상황 업데이트

Core 로직은 `progress_queue`를 통해 진행 상황 전달:

```python
def some_core_function(folder_path: str, progress_queue: queue.Queue):
    progress_queue.put(0)                    # 진행률 (int)
    progress_queue.put("단계:1/3")           # 단계 정보 (str)
    progress_queue.put("파일:example.xlsx")  # 파일명 (str)
    progress_queue.put(50)                   # 진행률 업데이트
    progress_queue.put(100)                  # 완료
```

Worker는 Queue를 폴링하여 Signal 발생:

```python
def _process_queue(self):
    while not self.progress_queue.empty():
        msg = self.progress_queue.get_nowait()

        if isinstance(msg, int):
            self.progress_updated.emit(msg)
        elif isinstance(msg, str):
            if msg.startswith("단계:"):
                self.step_updated.emit(msg[3:])
            elif msg.startswith("파일:"):
                self.file_updated.emit(msg[3:])
```

---

## 데이터 검증

### 공통 검증 규칙

1. **파일 존재 확인**
   - FileNotFoundError 발생 시 사용자 친화적 메시지

2. **헤더 검증**
   - 대소문자 구분
   - 필수 컬럼 누락 시 ValidationError

3. **KEY 검증**
   - None/빈 값 체크
   - 중복 KEY 체크

4. **데이터 일치 검증** (LY/GL)
   - Table 값 일치
   - Source 값 일치
   - 행 수 일치

### 에러 메시지

**사용자 친화적 메시지** (error_messages.py):

```python
def get_user_friendly_message(error_type: str, **kwargs) -> str:
    messages = {
        'FILE_NOT_FOUND': "파일을 찾을 수 없습니다:\n{path}",
        'INVALID_HEADER': "엑셀 헤더가 올바르지 않습니다:\n기대: {expected}\n실제: {actual}",
        'KEY_MISMATCH': "KEY가 일치하지 않습니다:\n파일: {file}\n행: {row}",
        # ...
    }
    return messages[error_type].format(**kwargs)
```

---

## 성능 최적화

### 빌드 크기 최적화

**기존**: 2.7GB
**최적화 후**: 89MB
**감소율**: 96.7%

**방법**:
- pandas 최적화: 불필요한 모듈 제외
- PyInstaller --exclude-module 옵션 활용
- 의존성 최소화

### 병렬 처리 (NC/GL)

**ProcessPoolExecutor**로 8개 언어 파일 병렬 읽기:
- 순차 처리 대비 약 3배 속도 향상
- 메모리 사용량 최적화

### 청크 읽기 (대용량 파일)

향후 대용량 파일 지원 시:
```python
df = pd.read_excel(file_path, chunksize=10000)
for chunk in df:
    process_chunk(chunk)
```

---

## 배포 및 빌드

### PyInstaller 빌드

**build.spec** 설정:

```python
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ui/styles/minimal.qss', 'ui/styles')],
    hiddenimports=['openpyxl', 'xlsxwriter'],
    excludes=['matplotlib', 'scipy', 'numpy.testing'],
    # ...
)
```

**빌드 명령**:
```bash
cd sebastian
pyinstaller build.spec --clean
```

**결과**: `sebastian/dist/Sebastian.exe` (89MB)

### GitHub Releases

**최신 릴리즈**: v0.1.1 (2025-12-23)
- URL: https://github.com/JaekyungCho2140/sebastianmk2/releases/tag/v0.1.1
- 포함: Sebastian.exe (89MB)

---

## 테스트

### LY/GL Round-trip 테스트 (37개)

**tests/test_lygl_roundtrip.py**:

```python
def test_merge_split_roundtrip():
    """Merge → Split → Merge 무결성 검증"""
    # 1. 7개 언어 → 1개 병합
    merged_wb = merge(language_files)

    # 2. 1개 → 7개 분리
    split_files = split(merged_wb)

    # 3. 재병합
    remerged_wb = merge(split_files)

    # 4. 원본과 비교
    assert_dataframes_equal(merged_wb, remerged_wb)
```

**결과**: 37개 테스트 모두 통과 ✅

### 레거시 출력 비교

M4/GL, NC/GL은 레거시 출력 파일과 100% 일치 검증:
- Excel 값 비교 (셀별)
- 서식 비교 (Font, Fill, Border)
- 행/열 수 비교

---

## 향후 계획

### 단기 (1개월 내)

1. **타입 힌트 완성**: 전체 코드베이스에 타입 힌트 추가
2. **mypy 검증 도입**: 타입 안정성 향상
3. **M4/GL, NC/GL 테스트**: 자동화된 출력 비교 테스트
4. **설정 파일**: config.json으로 최근 폴더, 테마 저장

### 중기 (3개월 내)

1. **다국어 지원**: 영어 UI (i18n 시스템)
2. **테마 시스템**: 다크 모드 지원
3. **성능 최적화**: M4/GL, LY/GL 병렬 처리
4. **대용량 파일**: 청크 읽기 지원

### 장기 (6개월 내)

1. **새 게임 추가**: 플러그인 시스템
2. **클라우드 연동**: Google Sheets, OneDrive
3. **버전 관리**: Git 통합
4. **협업 기능**: 변경 사항 추적, 댓글

---

## 라이선스 및 연락처

**개발자**: Jaekyung Cho
**저장소**: https://github.com/JaekyungCho2140/sebastianmk2
**라이선스**: (명시 필요)

---

**문서 버전**: 1.0.0
**최종 수정**: 2025-12-24
