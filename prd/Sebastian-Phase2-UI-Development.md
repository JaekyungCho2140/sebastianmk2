# Sebastian Phase 2: UI Development Guide

**버전**: 1.0.0
**작성일**: 2025-12-19
**Phase 목표**: PyQt6 기반 통합 UI 구축 (wireframe 기반)

---

## 📋 Phase 2 개요

### 목표

Sebastian-UI-Wireframes.md를 기반으로 PyQt6 통합 UI를 구축합니다.

### 핵심 원칙

1. **Wireframe 준수**: 디자인 스펙 100% 구현
2. **공통 컴포넌트 재사용**: ProgressDialog, LogViewer
3. **레거시 UI 참조 금지**: 새로운 디자인으로 구축
4. **Signal/Slot 패턴**: PyQt6 표준 패턴 사용

### 산출물

```
sebastian/ui/
├── __init__.py
├── main_window.py       # 메인 창 + 탭
├── m4gl_tab.py          # M4/GL 탭
├── ncgl_tab.py          # NC/GL 탭
├── lygl_tab.py          # LY/GL 탭
└── common/
    ├── __init__.py
    ├── progress_dialog.py
    └── log_viewer.py
```

---

## 🎨 우선순위 순서

### 1. 공통 컴포넌트 (선행 작업)
- ProgressDialog
- LogViewer
- 예상 시간: 2-3일

### 2. 메인 창 + 탭 구조
- QMainWindow 기본 틀
- QTabWidget 3개 탭
- 예상 시간: 1-2일

### 3. 게임별 탭 (병렬 가능)
- LY/GL 탭 (가장 간단)
- M4/GL 탭
- NC/GL 탭 (입력 검증)
- 예상 시간: 4-6일

---

## 📦 Task 1: 공통 컴포넌트

### 1.1 ProgressDialog 구현

**참조**: `prd/Sebastian-UI-Wireframes.md` → "ProgressDialog" 섹션

**Claude Code 지시**:
```
"sebastian/ui/common/progress_dialog.py를 작성해줘.
wireframe의 'ProgressDialog' 섹션을 참조하세요.

요구사항:
1. QDialog 상속
2. QProgressBar (0-100%)
3. Signal:
   - progress_updated(int)
   - status_updated(str)
   - file_updated(str)
4. Slot:
   - update_progress(int)
   - update_status(str)
   - update_file(str)
5. 모달 창 (500x280px)
6. 취소, 최소화 버튼
7. 단계 정보 (예: 2/3)
8. 처리 파일명 표시
9. 프로그레스 바 (32px 높이, 그라데이션)
10. 남은 시간 계산 (선택적)
"
```

**검증**:
```python
# 테스트 코드
from PyQt6.QtWidgets import QApplication
from ui.common.progress_dialog import ProgressDialog

app = QApplication([])
dialog = ProgressDialog()
dialog.update_status("테스트 중...")
dialog.update_progress(50)
dialog.show()
app.exec()
```

### 1.2 LogViewer 구현

**참조**: `prd/Sebastian-UI-Wireframes.md` → "LogViewer" 섹션

**Claude Code 지시**:
```
"sebastian/ui/common/log_viewer.py를 작성해줘.
wireframe의 'LogViewer' 섹션을 참조하세요.

요구사항:
1. QWidget 상속
2. 접기/펴기 기능 (애니메이션 0.3s)
3. 3개 탭: 로그, 에러, 경고
4. QPlainTextEdit (1000줄 제한)
5. [지우기] 버튼
6. 에러 발생 시 에러 탭 자동 전환
7. 메시지 형식: [timestamp] message
8. 탭별 배경색:
   - 로그: #FAFAFA
   - 에러: #FFEBEE
   - 경고: #FFF3E0
"
```

---

## 📦 Task 2: 메인 창 + 탭 구조

### 2.1 메인 창 구현

**참조**: `prd/Sebastian-UI-Wireframes.md` → "메인 창 구조" 섹션

**Claude Code 지시**:
```
"sebastian/ui/main_window.py를 작성해줘.
wireframe의 '메인 창 구조' 섹션을 참조하세요.

요구사항:
1. QMainWindow 상속
2. 창 크기: 기본 1000x700, 최소 800x600
3. 메뉴바:
   - 파일(F): 로그 저장, 종료(Ctrl+Q)
   - 도움말(H): 사용자 가이드, Sebastian 정보
4. QTabWidget (M4/GL, NC/GL, LY/GL)
5. LogViewer (하단, 접기/펴기)
6. 상태바 (24px)
7. 전역 스타일시트 적용 (wireframe 색상 시스템)
"
```

### 2.2 탭 추가

**Claude Code 지시**:
```
"main_window.py에 3개 탭을 추가해줘:

1. M4/GL 탭:
   from ui.m4gl_tab import M4GLTab
   self.tab_widget.addTab(M4GLTab(self), "M4/GL")

2. NC/GL 탭:
   from ui.ncgl_tab import NCGLTab
   self.tab_widget.addTab(NCGLTab(self), "NC/GL")

3. LY/GL 탭:
   from ui.lygl_tab import LYGLTab
   self.tab_widget.addTab(LYGLTab(self), "LY/GL")

탭 스타일:
- 활성 인디케이터: 3px, 프로젝트 색상
- M4/GL: #4CAF50
- NC/GL: #00897B
- LY/GL: #7B1FA2
"
```

---

## 📦 Task 3: M4/GL 탭

**참조**: `prd/Sebastian-UI-Wireframes.md` → "M4/GL 탭" 섹션

**Claude Code 지시**:
```
"sebastian/ui/m4gl_tab.py를 작성해줘.
wireframe의 'M4/GL 탭' 섹션을 참조하세요.

요구사항:
1. QWidget 상속
2. QVBoxLayout
3. 2개 기능 버튼 (280x200):
   - DIALOGUE 병합 (녹색 그라데이션)
   - STRING 병합 (파란색 그라데이션)
4. 폴더 선택:
   - QLineEdit (읽기 전용)
   - QPushButton "폴더 선택"
5. 실행 버튼 (160x48):
   - 비활성: #F5F5F5
   - 활성: 프로젝트 색상
6. 버튼 클릭 시 임시 메시지 (Phase 3에서 연결)

스타일:
- DIALOGUE 배경: linear-gradient(135deg, #E8F5E9, #C8E6C9)
- STRING 배경: linear-gradient(135deg, #E3F2FD, #BBDEFB)
- 선택 시: 테두리 2px solid
- Radius: 12px
"
```

---

## 📦 Task 4: NC/GL 탭

**참조**: `prd/Sebastian-UI-Wireframes.md` → "NC/GL 탭" 섹션

**Claude Code 지시**:
```
"sebastian/ui/ncgl_tab.py를 작성해줘.
wireframe의 'NC/GL 탭' 섹션을 참조하세요.

요구사항:
1. QWidget 상속
2. QVBoxLayout
3. 날짜 입력 (QLineEdit + 검증):
   - 6자리 숫자 (YYMMDD)
   - 실시간 검증 아이콘 (✓/✗)
   - 유효: #4CAF50, 무효: #F44336
4. 마일스톤 입력 (QLineEdit + 검증):
   - 1-3자리 숫자
   - 실시간 검증
5. 폴더 선택
6. 실행 버튼 (모든 입력 유효할 때만 활성화)

검증 로직:
- 날짜: r'^[0-9]{6}$'
- 마일스톤: r'^[0-9]{1,3}$'
- 유효성 변경 시 테두리 색상 변경
"
```

---

## 📦 Task 5: LY/GL 탭

**참조**: `prd/Sebastian-UI-Wireframes.md` → "LY/GL 탭" 섹션

**Claude Code 지시**:
```
"sebastian/ui/lygl_tab.py를 작성해줘.
wireframe의 'LY/GL 탭' 섹션을 참조하세요.

요구사항:
1. QWidget 상속
2. QGridLayout (2x2 그리드)
3. 4개 기능 버튼 (240x180):
   - Merge (7 → 1)
   - Split (1 → 7)
   - Batches (배치 병합)
   - Diff (버전 비교)
4. 버튼 클릭 시 해당 위저드 Dialog 표시 (Phase 3에서 구현)

스타일:
- 배경: linear-gradient(135deg, #F3E5F5, #E1BEE7)
- 테두리: 2px solid #BA68C8
- Hover: linear-gradient(135deg, #E1BEE7, #CE93D8)
- Radius: 12px
- 간격: 24px
"
```

---

## 🧪 Phase 2 검증

### 검증 1: 디자인 스펙 준수

**체크리스트**:
- [ ] 메인 창 크기 (1000x700, 최소 800x600)
- [ ] 색상 시스템 (wireframe 색상 코드)
- [ ] 타이포그래피 (Pretendard, 맑은 고딕)
- [ ] 간격 시스템 (XS 4px, SM 8px, MD 16px, LG 24px, XL 32px)
- [ ] Border Radius (SM 4px, MD 8px, LG 12px)

### 검증 2: 기능 동작

**테스트**:
```python
# sebastian/ui/__init__.py 작성
from .main_window import MainWindow

__all__ = ['MainWindow']

# 테스트 실행
python -c "
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
"
```

### 검증 3: UI 반응성

**테스트 항목**:
- [ ] 창 크기 조절 시 레이아웃 유지
- [ ] 탭 전환 동작
- [ ] 버튼 Hover/Press 효과
- [ ] LogViewer 접기/펴기 애니메이션
- [ ] 입력 필드 검증 (NC/GL)

---

## 📊 Phase 2 완료 체크리스트

### 공통 컴포넌트
- [ ] ProgressDialog 구현 및 테스트
- [ ] LogViewer 구현 및 테스트

### 메인 창
- [ ] MainWindow 구현
- [ ] 메뉴바 (파일, 도움말)
- [ ] 탭 구조
- [ ] 상태바

### 게임별 탭
- [ ] M4GLTab 구현
- [ ] NCGLTab 구현 (입력 검증 포함)
- [ ] LYGLTab 구현

### 디자인
- [ ] 전역 스타일시트 적용
- [ ] wireframe 디자인 100% 준수
- [ ] 반응형 레이아웃

---

## 🚨 주의사항

### 절대 하지 말 것

1. ❌ 레거시 UI 참조: 이미지 버튼, 절대 좌표 등
2. ❌ 임의 디자인: wireframe 외 디자인 추가
3. ❌ 로직 포함: UI에 비즈니스 로직 작성 (Phase 3에서)

### 허용되는 작업

1. ✅ wireframe 디자인 구현
2. ✅ Signal/Slot 정의
3. ✅ 입력 검증 (UI 레벨)
4. ✅ 임시 메시지 박스 (기능 연결 전)

---

## 📅 다음 단계

Phase 2 완료 후:

1. **Phase 3 시작**: [Sebastian-Phase3-Integration.md](Sebastian-Phase3-Integration.md)
2. **UI와 로직 연결**: QThread, Signal/Slot
3. **레거시 동작 검증**: 출력 파일 비교

---

## 📚 참고 자료

- [Sebastian-UI-Wireframes.md](Sebastian-UI-Wireframes.md) - UI 디자인 스펙
- [Sebastian-Migration-Guide.md](Sebastian-Migration-Guide.md) - 전체 마이그레이션 개요
- PyQt6 공식 문서: https://doc.qt.io/qtforpython-6/
