# M4_Merged-Office-
M4_Merged(Office)

- Released V1.1 - 2025. 4. 10
-- Changes
  언어 지원 중단에 따른 테이블 열 수정

- Released v1.0 - 2024. 5. 20

# M4/GL Merger 개선된 진행도 표시 창

## 개요
M4/GL Merger 애플리케이션의 진행도 표시 창을 개선하고 모듈화했습니다. 이 모듈은 다양한 프로젝트에서 재사용 가능하며, 모던한 디자인과 향상된 기능을 제공합니다.

## 주요 개선 사항

### 디자인 개선
- **플랫 디자인 적용**: 현대적인 UI 트렌드에 맞는 플랫 디자인을 적용했습니다.
- **그라데이션 효과**: ttk 스타일을 사용하여 프로그레스 바에 시각적 향상을 적용했습니다.
- **시각적 일관성**: 전체 애플리케이션에서 일관된 폰트와 색상 스키마를 사용합니다.

### 기능 개선
- **세부 진행 정보 표시**: 현재 처리 중인 파일명과 진행 단계를 표시합니다.
- **작업 취소 기능**: 사용자가 진행 중인 작업을 취소할 수 있습니다.
- **더 정확한 남은 시간 계산**: 개선된 알고리즘으로 남은 시간을 더 정확하게 예측합니다.
- **처리된 파일 수 표시**: 현재까지 처리된 파일과 전체 파일 수를 표시합니다.

### UX 개선
- **진행 상태 애니메이션**: 애니메이션 효과로 진행 중임을 시각적으로 표시합니다.
- **향상된 사용자 피드백**: 작업 완료/취소/오류 상황에 대한 명확한 피드백을 제공합니다.

## 사용 방법

### 모듈 가져오기
```python
from progress_window import ProgressWindow
```

### 진행 창 생성
```python
progress_window = ProgressWindow(
    parent_window,
    title="작업 진행 중",
    theme_color="#4CAF50",
    font_family="맑은 고딕"
)
```

### 작업 시작
```python
progress_window.start(
    worker_function,
    args=(additional_args,),
    total_steps=3,
    total_files=5
)
```

### 작업자 함수 예제
```python
def worker_function(queue, *args):
    # 진행 상태 업데이트
    queue.put("단계:1/3")
    queue.put("파일:file1.xlsx")
    
    # 진행률 업데이트 (0-100)
    queue.put(25)
    
    # 처리된 파일 수 업데이트
    queue.put("처리된 파일:1")
    
    # 완료 메시지
    queue.put("완료:작업이 성공적으로 완료되었습니다!")
    
    # 오류 메시지 (필요시)
    # queue.put(("error", "오류 메시지"))
```

## 메시지 형식
진행 창에 전달할 수 있는 메시지 형식:

1. **정수 값(0-100)**: 진행률 업데이트
2. **문자열 메시지**:
   - `"단계:N/M"`: 현재 단계 (예: "단계:1/3")
   - `"파일:파일명"`: 현재 처리 중인 파일
   - `"처리된 파일:N"`: 처리된 파일 수
   - `"완료:메시지"`: 작업 완료 메시지
3. **오류 메시지**: `("error", "오류 내용")`

## 테스트
기본 테스트 실행:
```
python test_progress.py
```

## 커스터마이징
진행 창의 색상, 크기, 폰트 등을 변경하여 다양한 애플리케이션에 맞게 조정할 수 있습니다.

```python
# 색상 테마 변경 예제
progress_window = ProgressWindow(
    parent_window,
    title="데이터 처리 중",
    width=600,
    height=350,
    theme_color="#2196F3",
    font_family="나눔고딕"
)
```
