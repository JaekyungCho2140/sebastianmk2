# Sebastian PRD - UI/UX v2 디자인 시스템

**버전**: v2.0.0
**디자인 방향**: 모던 미니멀 (Material Design 3.0 기반)
**타겟 사용자**: PM/기획자 (비기술직)
**디자인 철학**: Less is More, 명확한 계층, 충분한 여백

---

## 목차

1. [디자인 토큰](#디자인-토큰)
2. [컴포넌트 라이브러리](#컴포넌트-라이브러리)
3. [레이아웃 시스템](#레이아웃-시스템)
4. [타이포그래피](#타이포그래피)
5. [색상 시스템](#색상-시스템)
6. [간격 시스템](#간격-시스템)
7. [애니메이션](#애니메이션)

---

## 디자인 토큰

### 개요

**디자인 토큰**은 디자인 시스템의 원자적 요소입니다.

모든 UI 컴포넌트는 이 토큰을 기반으로 구성됩니다.

**파일 경로**: `sebastian/ui/common/design_tokens.py`

### 브랜드 색상

**Primary (주 색상)**:

```python
PRIMARY = "#5E35B1"           # Deep Purple 600
PRIMARY_LIGHT = "#7E57C2"     # Deep Purple 400 (hover)
PRIMARY_DARK = "#4527A0"      # Deep Purple 700 (pressed)
PRIMARY_SURFACE = "#EDE7F6"   # Deep Purple 50 (배경)
```

**사용처**:
- 주요 액션 버튼 (실행, 확인)
- 탭 선택 상태
- 포커스 테두리
- 진행 바

### 중립 색상 (Neutral Gray Scale)

**배경**:
```python
BG_PRIMARY = "#FFFFFF"        # 메인 배경
BG_SECONDARY = "#F8F9FA"      # 카드/패널 배경
BG_TERTIARY = "#F3F4F6"       # 비활성 영역
```

**텍스트**:
```python
TEXT_PRIMARY = "#1F2937"      # Gray 800 - 주요 텍스트
TEXT_SECONDARY = "#6B7280"    # Gray 500 - 보조 텍스트
TEXT_DISABLED = "#9CA3AF"     # Gray 400 - 비활성
```

**테두리**:
```python
BORDER = "#E5E7EB"            # Gray 200 - 기본 테두리
BORDER_FOCUS = "#D1D5DB"      # Gray 300 - 포커스
DIVIDER = "#F3F4F6"           # Gray 100 - 구분선
```

### 상태 색상 (Semantic Colors)

**Success (성공)**:
```python
SUCCESS = "#10B981"           # Green 500
SUCCESS_BG = "#D1FAE5"        # Green 100
```

**Error (에러)**:
```python
ERROR = "#EF4444"             # Red 500
ERROR_BG = "#FEE2E2"          # Red 100
```

**Warning (경고)**:
```python
WARNING = "#F59E0B"           # Amber 500
WARNING_BG = "#FEF3C7"        # Amber 100
```

**Info (정보)**:
```python
INFO = "#3B82F6"              # Blue 500
INFO_BG = "#DBEAFE"           # Blue 100
```

### 간격 (8pt Grid System)

```python
SPACING_XXS = 2   # 극소 간격
SPACING_XS = 4    # 아이콘 패딩
SPACING_SM = 8    # 요소 간 최소 간격
SPACING_MD = 16   # 컴포넌트 내부 패딩
SPACING_LG = 24   # 컴포넌트 간 간격
SPACING_XL = 32   # 섹션 구분
SPACING_XXL = 48  # 메인 여백
```

**사용 예시**:
- 버튼 패딩: `SPACING_MD` (16px)
- 카드 간격: `SPACING_LG` (24px)
- 탭 컨텐츠 여백: `SPACING_XXL` (48px)

### 타이포그래피

**폰트 패밀리**:
```python
FONT_FAMILY = "Pretendard, Segoe UI, SF Pro, Roboto, Arial"
```

**폰트 크기**:
```python
FONT_SIZE_CAPTION = 11    # 힌트, 캡션
FONT_SIZE_BODY = 13       # 본문
FONT_SIZE_SUBHEADING = 15 # 소제목
FONT_SIZE_HEADING = 18    # 제목
FONT_SIZE_TITLE = 24      # 큰 제목
```

**폰트 굵기**:
```python
FONT_WEIGHT_REGULAR = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700
```

**행간**:
```python
LINE_HEIGHT = 1.5
```

### 컴포넌트 크기

```python
BUTTON_HEIGHT = 40        # 기본 버튼
BUTTON_LARGE = 48         # 큰 버튼 (실행)
INPUT_HEIGHT = 40         # 입력 필드
TAB_HEIGHT = 48           # 탭 바
ICON_SIZE = 20            # 기본 아이콘
BORDER_RADIUS = 8         # 기본 둥근 모서리
BORDER_RADIUS_LG = 12     # 큰 둥근 모서리 (카드)
MIN_TOUCH_TARGET = 44     # 최소 터치 영역 (접근성)
```

### 애니메이션

```python
ANIMATION_FAST = 150      # 빠른 전환 (ms)
ANIMATION_NORMAL = 250    # 일반 전환
ANIMATION_SLOW = 350      # 느린 전환
```

### 그림자 (Elevation)

```python
SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
```

---

## 컴포넌트 라이브러리

### 버튼

#### Primary 버튼

**스타일**:
```python
background-color: {PRIMARY}      # #5E35B1
color: white
border: none
border-radius: 8px
padding: 10px 20px
font-weight: 600
min-height: 40px
```

**상태**:
- Hover: `background-color: {PRIMARY_LIGHT}` (#7E57C2)
- Pressed: `background-color: {PRIMARY_DARK}` (#4527A0)
- Disabled: `background-color: #F3F4F6`, `color: #9CA3AF`

**사용처**:
- 실행 버튼
- 확인 버튼

#### Secondary 버튼

**스타일**:
```python
background-color: {BG_SECONDARY}  # #F8F9FA
color: {TEXT_PRIMARY}             # #1F2937
border: 1px solid {BORDER}        # #E5E7EB
border-radius: 8px
padding: 10px 20px
min-height: 40px
```

**상태**:
- Hover: `background-color: {BG_TERTIARY}` (#F3F4F6)
- Pressed: `background-color: {BORDER}` (#E5E7EB)

**사용처**:
- 취소 버튼
- 폴더 선택 버튼

#### Card 버튼 (M4/GL)

**크기**: 240 × 200px

**스타일**:
```python
background-color: {BG_PRIMARY}    # #FFFFFF
border: 2px solid {BORDER}        # #E5E7EB
border-radius: 12px
padding: 16px
cursor: pointer
```

**선택 상태**:
```python
background-color: {PRIMARY_SURFACE}  # #EDE7F6
border: 3px solid {PRIMARY}          # #5E35B1
```

#### List Item 버튼 (LY/GL)

**크기**: 최소 높이 64px

**스타일**:
```python
background-color: {BG_PRIMARY}    # #FFFFFF
border: 1px solid {BORDER}        # #E5E7EB
border-radius: 8px
padding: 10px 16px
text-align: left
min-height: 64px
```

**Hover**:
```python
background-color: {BG_SECONDARY}  # #F8F9FA
border-color: {PRIMARY}           # #5E35B1
```

### 입력 필드

#### 텍스트 입력

**스타일**:
```python
background-color: {BG_PRIMARY}    # #FFFFFF
border: 2px solid {BORDER}        # #E5E7EB
border-radius: 8px
padding: 10px 12px
min-height: 40px
font-size: 13px
```

**포커스**:
```python
border-color: {PRIMARY}           # #5E35B1
```

**읽기 전용**:
```python
background-color: {BG_SECONDARY}  # #F8F9FA
color: {TEXT_SECONDARY}           # #6B7280
```

#### 검증 상태 (NC/GL)

**유효**:
```python
border: 2px solid {SUCCESS}       # #10B981
```

**무효**:
```python
border: 2px solid {ERROR}         # #EF4444
```

### 탭

**탭 바**:
```python
background-color: {BG_SECONDARY}  # #F8F9FA
height: 48px
```

**탭 아이템**:
```python
# 기본
background-color: {BG_SECONDARY}  # #F8F9FA
color: {TEXT_SECONDARY}           # #6B7280
padding: 12px 24px
border-bottom: 2px solid transparent

# 선택
background-color: {BG_PRIMARY}    # #FFFFFF
color: {PRIMARY}                  # #5E35B1
border-bottom: 2px solid {PRIMARY}

# Hover
background-color: {BG_TERTIARY}   # #F3F4F6
```

### 진행 Dialog (ProgressDialog)

**구조**:
```
┌─────────────────────────────────────┐
│ M4/GL DIALOGUE 병합                 │ ← 제목
├─────────────────────────────────────┤
│                                     │
│ 단계: 1/3                           │ ← 단계 정보
│ 처리 중: CINEMATIC_DIALOGUE.xlsm    │ ← 파일명
│                                     │
│ ████████░░░░░░░░░░░░ 40%            │ ← 진행바
│                                     │
│     [취소]         [최소화]         │ ← 버튼
│                                     │
└─────────────────────────────────────┘
```

**스타일**:
- 크기: 500 × 250px
- 진행바: `background-color: {PRIMARY}`
- 취소 버튼: Secondary 스타일
- 최소화 버튼: Secondary 스타일

### 로그 뷰어 (LogViewer)

**펼침 상태**: 200px 높이
**접힘 상태**: 32px 높이

**스타일**:
```python
background-color: {BG_SECONDARY}  # #F8F9FA
border-top: 1px solid {BORDER}    # #E5E7EB
font-family: "Courier New"
font-size: 12px
```

**토글 버튼**:
- 펼침: "▼ 로그 보기"
- 접힘: "▲ 로그 숨기기"

---

## 레이아웃 시스템

### Main Window

**크기**:
- 기본: 1000 × 700px
- 최소: 800 × 600px

**구조**:
```
┌─────────────────────────────────────┐
│ Title Bar                           │ 타이틀 바
├─────────────────────────────────────┤
│ Menu Bar (32px)                     │ 메뉴바
├─────────────────────────────────────┤
│ Tab Bar (48px)                      │ 탭바
├─────────────────────────────────────┤
│                                     │
│ Main Content (flexible)             │ 메인 컨텐츠
│                                     │
├─────────────────────────────────────┤
│ Log Viewer (200px / 32px)           │ 로그 뷰어
├─────────────────────────────────────┤
│ Status Bar (24px)                   │ 상태바
└─────────────────────────────────────┘
```

### 탭 컨텐츠 여백

**모든 탭 공통**:
```python
layout.setContentsMargins(48, 48, 48, 48)  # 상하좌우 48px
layout.setSpacing(24)                       # 컴포넌트 간 24px
```

### 반응형 레이아웃

**원칙**: 고정 크기보다는 flexible 사용

**예시**:
```python
# 가로 중앙 정렬
execute_layout = QHBoxLayout()
execute_layout.addStretch()        # 왼쪽 여백
execute_layout.addWidget(btn)      # 버튼
execute_layout.addStretch()        # 오른쪽 여백 (선택)
```

---

## 타이포그래피

### 폰트 계층

| 레벨 | 크기 | 굵기 | 용도 | 예시 |
|------|------|------|------|------|
| Title | 24px | Bold (700) | 메인 제목 | Dialog 제목 |
| Heading | 18px | Bold (700) | 섹션 제목 | 카드 제목 |
| Subheading | 15px | Medium (500) | 소제목 | 카드 부제목 |
| Body | 13px | Regular (400) | 본문 | 일반 텍스트 |
| Caption | 11px | Regular (400) | 힌트, 설명 | 입력 필드 힌트 |

### 사용 예시

**카드 버튼 (M4/GL)**:
```
DIALOGUE          ← 18px Bold (Heading)
병합              ← 15px Regular (Subheading)
대화 데이터       ← 13px Regular (Body)
3개 파일          ← 13px Regular (Body)
```

**입력 필드 레이블**:
```
날짜 (YYMMDD)     ← 12px Medium (레이블)
[250512]          ← 13px Regular (입력값)
6자리 숫자 (예: 250512)  ← 11px Regular (Caption)
```

---

## 색상 시스템

### 색상 사용 가이드

**Primary 색상** (`#5E35B1`):
- 주요 액션 버튼
- 탭 선택 상태
- 포커스 테두리
- 진행 바

**Neutral 색상**:
- 배경: White (`#FFFFFF`), Light Gray (`#F8F9FA`)
- 텍스트: Dark Gray (`#1F2937`), Medium Gray (`#6B7280`)
- 테두리: Light Gray (`#E5E7EB`)

**Semantic 색상**:
- Success (`#10B981`): 검증 성공, 완료 메시지
- Error (`#EF4444`): 검증 실패, 에러 메시지
- Warning (`#F59E0B`): 경고 메시지
- Info (`#3B82F6`): 정보 메시지

### 색상 대비

**WCAG AA 준수**:
- Primary Text (`#1F2937`) on White (`#FFFFFF`): 14.3:1 ✅
- Secondary Text (`#6B7280`) on White (`#FFFFFF`): 4.8:1 ✅
- Primary Button (`#5E35B1`) on White Text: 7.2:1 ✅

---

## 간격 시스템

### 8pt Grid System

**기본 단위**: 8px

**배수 사용**:
- 2px (XXS): 극소 간격
- 4px (XS): 아이콘 패딩
- 8px (SM): 요소 간 최소 간격
- 16px (MD): 컴포넌트 내부 패딩
- 24px (LG): 컴포넌트 간 간격
- 32px (XL): 섹션 구분
- 48px (XXL): 메인 여백

### 적용 예시

**버튼**:
- Padding: 10px 20px (예외: 8의 배수 아님, 시각적 균형 우선)
- 간격: 8px (버튼 간)

**카드**:
- Padding: 16px
- 간격: 24px (카드 간)

**탭 컨텐츠**:
- Margin: 48px (상하좌우)

---

## 애니메이션

### 전환 속도

**빠른 전환** (150ms):
- Hover 상태 변화
- 포커스 이동

**일반 전환** (250ms):
- 탭 전환
- Dialog 열기/닫기

**느린 전환** (350ms):
- 로그 뷰어 펼치기/접기

### 가속도 곡선

**ease-out**: 대부분의 전환에 사용

```python
# QSS에서 사용 불가, PyQt6 QPropertyAnimation 사용 시
animation = QPropertyAnimation(widget, b"geometry")
animation.setDuration(250)
animation.setEasingCurve(QEasingCurve.Type.OutCubic)
```

---

## 구현 파일

### QSS 스타일시트

**파일 경로**: `sebastian/ui/styles/minimal.qss`

**적용 방법**:
```python
def _load_stylesheet(self):
    from pathlib import Path

    current_dir = Path(__file__).parent
    qss_path = current_dir / "styles" / "minimal.qss"

    if qss_path.exists():
        with open(qss_path, 'r', encoding='utf-8') as f:
            stylesheet = f.read()
            self.setStyleSheet(stylesheet)
```

### Design Tokens

**파일 경로**: `sebastian/ui/common/design_tokens.py`

**사용 방법**:
```python
from .common.design_tokens import DesignTokens as DT

# 직접 사용
btn.setStyleSheet(f"background-color: {DT.PRIMARY};")

# 또는 import
from .common.design_tokens import DT

label.setStyleSheet(f"color: {DT.TEXT_PRIMARY};")
```

---

**문서 버전**: 1.0.0
**최종 수정**: 2025-12-24
