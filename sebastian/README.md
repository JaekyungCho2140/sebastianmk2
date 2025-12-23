# Sebastian - 게임 현지화 도구 통합 프로그램

**버전**: 1.0.0
**완료일**: 2025-12-22

## 개요

3개 게임의 현지화 도구를 하나의 PyQt6 프로그램으로 통합:
- **M4/GL**: MIR4 DIALOGUE/STRING 병합
- **NC/GL**: NC 다국어 테이블 병합
- **LY/GL**: LY Table 병합/분할/배치/비교

## 설치 및 실행

### 1. 의존성 설치

```powershell
# 가상환경 생성 (선택사항)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt
```

### 2. 프로그램 실행

```powershell
cd sebastian
python main.py
```

## 사용 방법

### M4/GL 탭

1. **DIALOGUE** 또는 **STRING** 버튼 클릭
2. **폴더 선택** 클릭하여 소스 파일 폴더 선택
   - DIALOGUE: CINEMATIC_DIALOGUE.xlsm, SMALLTALK_DIALOGUE.xlsm, NPC.xlsm
   - STRING: 8개 STRING_*.xlsm 파일
3. **실행** 버튼 클릭
4. 진행 상황 표시 → 완료 메시지
5. 출력: `MMDD_MIR4_MASTER_DIALOGUE.xlsx` 또는 `MMDD_MIR4_MASTER_STRING.xlsx`

### NC/GL 탭

1. **날짜** 입력 (6자리 숫자, 예: 250512)
2. **마일스톤** 입력 (1-3자리 숫자, 예: 15 → M15)
3. **폴더 선택** 클릭하여 8개 StringXXX.xlsx 파일이 있는 폴더 선택
4. **실행** 버튼 클릭
5. 출력: `{날짜}_M{마일스톤}_StringALL.xlsx`

### LY/GL 탭

*4개 기능 (Merge, Split, Batches, Diff)의 위저드는 추후 구현 예정*

## 기술 스택

- **UI**: PyQt6
- **데이터**: pandas, openpyxl, xlsxwriter, numpy
- **병렬 처리**: ProcessPoolExecutor (NC/GL)
- **비동기**: QThread

## 프로젝트 구조

```
sebastian/
├── main.py              # 엔트리포인트
├── requirements.txt     # 의존성
├── core/                # 레거시 로직 (Phase 1)
│   ├── m4gl/
│   ├── ncgl/
│   └── lygl/
├── ui/                  # PyQt6 UI (Phase 2)
│   ├── main_window.py
│   ├── m4gl_tab.py
│   ├── ncgl_tab.py
│   ├── lygl_tab.py
│   └── common/
└── workers/             # QThread (Phase 3)
    ├── m4gl_worker.py
    ├── ncgl_worker.py
    └── lygl_worker.py
```

## Phase 완료 현황

- ✅ **Phase 1**: 로직 추출 (레거시 → core)
- ✅ **Phase 2**: UI 개발 (PyQt6)
- ✅ **Phase 3**: 통합 (M4/GL, NC/GL 동작 가능)
- ⏳ **Phase 3 추가**: LY/GL 위저드 구현
- ⏳ **Phase 3 검증**: 출력 파일 레거시 비교

## 검증 방법

### M4/GL 출력 검증

```powershell
# 레거시 실행 → 출력 파일 생성
# Sebastian 실행 → 출력 파일 생성
# 비교
fc legacy_output.xlsx sebastian_output.xlsx
```

예상: 파일이 동일함 (100% 일치)

### NC/GL 출력 검증

```powershell
fc legacy_StringALL.xlsx sebastian_StringALL.xlsx
```

예상: 파일이 동일함 (100% 일치)

## 주의사항

이 프로그램은 레거시 코드를 정확히 복사하여 만들어졌습니다:
- **로직 재구현 없음**: 레거시와 동일한 알고리즘
- **최소 변경**: UI 의존성 제거만 수행
- **100% 동작 보장**: 출력이 레거시와 완전히 일치해야 함

## 라이선스

© 2025
