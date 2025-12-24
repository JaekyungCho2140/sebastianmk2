"""
Sebastian UI 색상 시스템

v2: 디자인 토큰 기반으로 통일된 색상 시스템 적용
레거시 호환성을 위해 기존 변수명 유지
"""

from .design_tokens import DesignTokens as DT

# ===== 레거시 호환성 (v1) =====
# 기존 코드와의 호환성을 위해 유지
M4GL_DIALOGUE = "#4CAF50"  # 레거시
M4GL_STRING = "#2196F3"    # 레거시
NCGL = "#00897B"           # 레거시
LYGL = "#7B1FA2"           # 레거시

# ===== v2 통일된 브랜드 색상 =====
# 모든 주요 액션 버튼에 사용
PRIMARY = DT.PRIMARY
PRIMARY_LIGHT = DT.PRIMARY_LIGHT
PRIMARY_DARK = DT.PRIMARY_DARK
PRIMARY_SURFACE = DT.PRIMARY_SURFACE

# 배경
BG_PRIMARY = DT.BG_PRIMARY
BG_SECONDARY = DT.BG_SECONDARY
BG_TERTIARY = DT.BG_TERTIARY

# 텍스트
TEXT_PRIMARY = DT.TEXT_PRIMARY
TEXT_SECONDARY = DT.TEXT_SECONDARY
TEXT_DISABLED = DT.TEXT_DISABLED

# 테두리
BORDER = DT.BORDER
BORDER_FOCUS = DT.BORDER_FOCUS
DIVIDER = DT.DIVIDER

# 상태
SUCCESS = DT.SUCCESS
ERROR = DT.ERROR
WARNING = DT.WARNING
INFO = DT.INFO

# 상태별 배경
SUCCESS_BG = DT.SUCCESS_BG
ERROR_BG = DT.ERROR_BG
WARNING_BG = DT.WARNING_BG
INFO_BG = DT.INFO_BG
