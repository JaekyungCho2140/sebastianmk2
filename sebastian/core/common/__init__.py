"""공통 Core 모듈

이 모듈은 여러 게임에 공통으로 사용되는 기능을 제공합니다.

Modules:
    csv_validator: CSV 파일 구조 검증
    csv_parser: Raw CSV 파싱 (상태 머신)
    csv_restore: CSV 따옴표 복원 및 보고서 생성
"""

from sebastian.core.common.csv_validator import (
    validate_csv_structure,
    CSVValidationError,
)
from sebastian.core.common.csv_parser import (
    parse_csv_line_raw,
    analyze_csv_pattern,
    save_csv_with_pattern,
    CSVParseError,
)
from sebastian.core.common.csv_restore import (
    restore_csv_quotes,
    generate_diff_report,
)

__all__ = [
    "validate_csv_structure",
    "CSVValidationError",
    "parse_csv_line_raw",
    "analyze_csv_pattern",
    "save_csv_with_pattern",
    "CSVParseError",
    "restore_csv_quotes",
    "generate_diff_report",
]
