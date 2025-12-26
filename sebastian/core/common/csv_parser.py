"""Raw CSV 파서 모듈

CSV 파일을 raw text level에서 파싱하여 각 필드의 정확한 따옴표 패턴을 분석합니다.
"""

from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class CSVParseError(Exception):
    """CSV 파싱 에러"""

    pass


def parse_csv_line_raw(line: str) -> List[Tuple[str, bool, str]]:
    """CSV 라인을 수동 파싱 (상태 머신)

    CSV 라인을 파싱하여 각 필드의 값, 따옴표 유무, 원본 raw text를 반환합니다.

    상태:
        - FIELD_START: 필드 시작
        - IN_QUOTED_FIELD: 따옴표로 감싼 필드 내부
        - IN_UNQUOTED_FIELD: 따옴표 없는 필드 내부
        - AFTER_QUOTE: 따옴표 닫힌 직후

    Args:
        line: CSV 라인 (개행 문자 제거됨)

    Returns:
        [(field_value, has_quotes, raw_field_text), ...]
        - field_value: unescape된 필드 값 ("" → ")
        - has_quotes: 필드에 따옴표가 있었는지 여부
        - raw_field_text: 원본 raw text (따옴표 포함)

    Raises:
        CSVParseError: 잘못된 CSV 형식

    Examples:
        >>> parse_csv_line_raw('"field1",field2,"field3"')
        [('field1', True, '"field1"'), ('field2', False, 'field2'), ('field3', True, '"field3"')]

        >>> parse_csv_line_raw('text,"<span class=""green"">Test</span>"')
        [('text', False, 'text'), ('<span class="green">Test</span>', True, '"<span class=""green"">Test</span>"')]
    """
    STATE_FIELD_START = "field_start"
    STATE_IN_QUOTED = "in_quoted"
    STATE_IN_UNQUOTED = "in_unquoted"
    STATE_AFTER_QUOTE = "after_quote"

    fields = []
    current_field = []
    has_quotes = False
    state = STATE_FIELD_START
    field_start_pos = 0  # 필드 시작 위치

    i = 0
    while i < len(line):
        char = line[i]

        if state == STATE_FIELD_START:
            if char == '"':
                # 따옴표로 시작하는 필드
                has_quotes = True
                state = STATE_IN_QUOTED
            elif char == ",":
                # 빈 필드 (따옴표 없음)
                raw_text = line[field_start_pos:i]  # 빈 문자열
                fields.append(("", False, raw_text))
                field_start_pos = i + 1  # 다음 필드 시작
                # state는 FIELD_START 유지
            else:
                # 일반 필드 (따옴표 없음)
                current_field.append(char)
                state = STATE_IN_UNQUOTED

        elif state == STATE_IN_QUOTED:
            if char == '"':
                # 따옴표 발견 - escape인지 닫는 따옴표인지 확인
                if i + 1 < len(line) and line[i + 1] == '"':
                    # Escape된 따옴표 ("") → 단일 따옴표(")로 변환
                    current_field.append('"')
                    i += 1  # 다음 " 건너뛰기
                else:
                    # 필드 닫는 따옴표
                    state = STATE_AFTER_QUOTE
            else:
                current_field.append(char)

        elif state == STATE_IN_UNQUOTED:
            if char == ",":
                # 필드 종료
                raw_text = line[field_start_pos:i]
                fields.append(("".join(current_field), has_quotes, raw_text))
                current_field = []
                has_quotes = False
                field_start_pos = i + 1
                state = STATE_FIELD_START
            elif char == '"':
                # 따옴표 없는 필드에 따옴표가 나타남
                # RFC 4180 위반이지만, 실제 파일에서 발생할 수 있음
                # (예: HTML 태그 내 따옴표)
                # 경고만 로그하고 계속 진행
                logger.warning(
                    f"RFC 4180 위반: 따옴표 없는 필드 내부에 따옴표 발견 (위치: {i})"
                )
                current_field.append(char)
            else:
                current_field.append(char)

        elif state == STATE_AFTER_QUOTE:
            if char == ",":
                # 필드 종료
                raw_text = line[field_start_pos:i]
                fields.append(("".join(current_field), has_quotes, raw_text))
                current_field = []
                has_quotes = False
                field_start_pos = i + 1
                state = STATE_FIELD_START
            else:
                # 따옴표 닫힌 후 추가 문자가 있는 경우
                # RFC 4180 위반이지만 실제 파일에서 발생
                # 추가 문자를 필드에 포함하여 계속 읽기
                if i == len(line) - 1 or line[i] != " ":
                    # 공백이 아니면 경고 (한 번만)
                    if not current_field or current_field[-1] != " ":
                        logger.warning(
                            f"RFC 4180 위반: 따옴표 닫힌 후 추가 텍스트 (위치: {i})"
                        )
                current_field.append(char)
                # 계속 읽다가 다음 쉼표에서 종료

        i += 1

    # 마지막 필드 처리
    if state == STATE_IN_QUOTED:
        # 따옴표가 닫히지 않음 (다음 줄로 계속되는 경우)
        # 이 경우는 별도 처리 필요 (multiline field)
        raise CSVParseError("따옴표가 닫히지 않았습니다 (다중 행 필드 가능성)")
    elif state in [STATE_IN_UNQUOTED, STATE_AFTER_QUOTE, STATE_FIELD_START]:
        # 정상적으로 라인 끝에 도달
        if state != STATE_FIELD_START:
            raw_text = line[field_start_pos:]
            fields.append(("".join(current_field), has_quotes, raw_text))

    return fields


def analyze_csv_pattern(csv_path: str) -> Dict[Tuple[int, str], Dict[str, any]]:
    """CSV 파일을 raw text로 분석하여 따옴표 패턴 추출

    각 필드의 따옴표 유무와 원본 값을 저장합니다.

    Args:
        csv_path: CSV 파일 경로

    Returns:
        {
            (row_idx, column_name): {
                'has_field_quotes': bool,  # 필드에 따옴표가 있었는지
                'original_value': str,     # 원본 값 (unescape된 상태)
                'raw_field_text': str      # 원본 raw text (따옴표 포함)
            }
        }

    Raises:
        CSVParseError: CSV 파싱 실패 시

    Examples:
        >>> pattern = analyze_csv_pattern("original.csv")
        >>> pattern[(0, 'ko')]
        {'has_field_quotes': True, 'original_value': '텍스트'}
    """
    pattern = {}

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    if not lines:
        raise CSVParseError("빈 파일입니다")

    # 헤더 파싱
    header_line = lines[0].strip()
    try:
        header_fields = parse_csv_line_raw(header_line)
        headers = [field_value for field_value, _, _ in header_fields]
    except CSVParseError as e:
        raise CSVParseError(f"헤더 파싱 실패: {e}")

    logger.info(f"CSV 헤더: {headers}")

    # 데이터 파싱 (멀티라인 필드 처리)
    row_idx = 0
    line_idx = 1

    while line_idx < len(lines):
        line = lines[line_idx].rstrip("\n\r")

        # 빈 라인 무시
        if not line.strip():
            line_idx += 1
            continue

        try:
            # 단일 라인 파싱 시도
            fields = parse_csv_line_raw(line)

            # 컬럼 수 확인
            if len(fields) != len(headers):
                # 멀티라인 필드 가능성 - 다음 줄과 병합
                line = _read_multiline_field(lines, line_idx)
                fields = parse_csv_line_raw(line)
                # line_idx는 _read_multiline_field에서 업데이트됨

            # 패턴 저장
            for col_idx, (field_value, has_quotes, raw_text) in enumerate(fields):
                col_name = headers[col_idx]
                pattern[(row_idx, col_name)] = {
                    "has_field_quotes": has_quotes,
                    "original_value": field_value,
                    "raw_field_text": raw_text,
                }

            row_idx += 1
            line_idx += 1

        except CSVParseError as e:
            logger.warning(f"라인 {line_idx} 파싱 실패: {e}")
            # 멀티라인 필드일 가능성
            line_idx += 1
            continue

    logger.info(f"총 {row_idx}개 행 파싱 완료")

    return pattern


def _read_multiline_field(lines: List[str], start_idx: int) -> str:
    """멀티라인 필드 읽기

    따옴표로 감싼 필드 내부에 줄바꿈이 있는 경우,
    여러 줄을 합쳐서 하나의 라인으로 만듭니다.

    Args:
        lines: 전체 라인 리스트
        start_idx: 시작 라인 인덱스

    Returns:
        병합된 라인 (줄바꿈 포함)

    Note:
        현재 단순 구현으로는 멀티라인 필드를 완벽히 처리하기 어려움.
        향후 개선 필요.
    """
    # TODO: 멀티라인 필드 처리 개선
    # 현재는 단일 라인만 처리
    return lines[start_idx].rstrip("\n\r")


def save_csv_with_pattern(
    df,  # pd.DataFrame
    output_path: str,
    original_pattern: Dict[Tuple[int, str], Dict[str, any]],
    original_df=None,  # pd.DataFrame (내용 비교용)
) -> Dict[Tuple[int, str], str]:
    """DataFrame을 원본 raw text 패턴으로 CSV 저장

    **핵심**: RFC 4180 완전 무시! 원본 raw text를 그대로 재현합니다.

    Args:
        df: 저장할 DataFrame (export 데이터)
        output_path: 출력 경로
        original_pattern: analyze_csv_pattern()의 반환값
        original_df: 원본 DataFrame (내용 비교용, optional)

    Returns:
        {(row_idx, col): restored_raw_text} 딕셔너리
        각 필드에 저장한 raw text

    Examples:
        >>> pattern = analyze_csv_pattern("original.csv")
        >>> restored_pattern = save_csv_with_pattern(export_df, "restored.csv", pattern, original_df)
    """
    restored_pattern = {}  # 저장한 raw text 기록

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        # 헤더 작성 (따옴표 없이)
        f.write(",".join(df.columns) + "\n")

        # 데이터 작성
        for row_idx in range(len(df)):
            row_parts = []

            for col in df.columns:
                export_value = str(df.iloc[row_idx][col])

                # 원본 패턴 확인
                pattern_key = (row_idx, col)
                if pattern_key in original_pattern:
                    original_value = original_pattern[pattern_key]["original_value"]
                    original_raw = original_pattern[pattern_key]["raw_field_text"]

                    # 내용 비교
                    if export_value == original_value:
                        # 내용 동일 → 원본 raw text 그대로!
                        formatted = original_raw
                    else:
                        # 내용 변경됨 → Export 값 사용
                        formatted = export_value
                else:
                    # 패턴 정보 없으면 그대로
                    formatted = export_value

                row_parts.append(formatted)
                restored_pattern[(row_idx, col)] = formatted  # 저장한 raw text 기록

            # Raw text를 직접 쓰기 (RFC 4180 무시!)
            f.write(",".join(row_parts) + "\n")

    logger.info(f"CSV 저장 완료 (원본 raw text 패턴, RFC 4180 무시): {output_path}")

    return restored_pattern


def _needs_quotes_rfc4180(field: str) -> bool:
    """RFC 4180 규칙으로 따옴표 필요 여부 판단

    Args:
        field: 필드 값

    Returns:
        True if 따옴표 필요, False otherwise
    """
    if not field:
        return False

    # RFC 4180 특수 문자
    special_chars = [",", "\n", "\r", '"']
    return any(char in field for char in special_chars)
