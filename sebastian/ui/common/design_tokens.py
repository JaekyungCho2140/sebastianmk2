"""
Sebastian v2 디자인 토큰

모던 미니멀 디자인 시스템의 모든 색상, 간격, 타이포그래피를 정의합니다.
"""


class DesignTokens:
    """Sebastian v2 미니멀 디자인 토큰"""

    # ===== 브랜드 색상 (통일) =====
    PRIMARY = "#5E35B1"           # Deep Purple 600
    PRIMARY_LIGHT = "#7E57C2"     # Deep Purple 400 (hover)
    PRIMARY_DARK = "#4527A0"      # Deep Purple 700 (pressed)
    PRIMARY_SURFACE = "#EDE7F6"   # Deep Purple 50 (배경)

    # ===== 중립 색상 (Neutral Gray Scale) =====
    BG_PRIMARY = "#FFFFFF"        # 메인 배경
    BG_SECONDARY = "#F8F9FA"      # 카드/패널 배경
    BG_TERTIARY = "#F3F4F6"       # 비활성 영역

    TEXT_PRIMARY = "#1F2937"      # Gray 800 - 주요 텍스트
    TEXT_SECONDARY = "#6B7280"    # Gray 500 - 보조 텍스트
    TEXT_DISABLED = "#9CA3AF"     # Gray 400 - 비활성

    BORDER = "#E5E7EB"            # Gray 200 - 기본 테두리
    BORDER_FOCUS = "#D1D5DB"      # Gray 300 - 포커스
    DIVIDER = "#F3F4F6"           # Gray 100 - 구분선

    # ===== 상태 색상 (Semantic Colors) =====
    SUCCESS = "#10B981"           # Green 500
    SUCCESS_BG = "#D1FAE5"        # Green 100

    ERROR = "#EF4444"             # Red 500
    ERROR_BG = "#FEE2E2"          # Red 100

    WARNING = "#F59E0B"           # Amber 500
    WARNING_BG = "#FEF3C7"        # Amber 100

    INFO = "#3B82F6"              # Blue 500
    INFO_BG = "#DBEAFE"           # Blue 100

    # ===== 간격 (8pt Grid System) =====
    SPACING_XXS = 2   # 극소 간격
    SPACING_XS = 4    # 아이콘 패딩
    SPACING_SM = 8    # 요소 간 최소 간격
    SPACING_MD = 16   # 컴포넌트 내부 패딩
    SPACING_LG = 24   # 컴포넌트 간 간격
    SPACING_XL = 32   # 섹션 구분
    SPACING_XXL = 48  # 메인 여백

    # ===== 타이포그래피 =====
    FONT_FAMILY = "Pretendard, Segoe UI, SF Pro, Roboto, Arial"

    FONT_SIZE_CAPTION = 11    # 힌트, 캡션
    FONT_SIZE_BODY = 13       # 본문
    FONT_SIZE_SUBHEADING = 15 # 소제목
    FONT_SIZE_HEADING = 18    # 제목
    FONT_SIZE_TITLE = 24      # 큰 제목

    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700

    LINE_HEIGHT = 1.5

    # ===== 컴포넌트 크기 =====
    BUTTON_HEIGHT = 40        # 기본 버튼
    BUTTON_LARGE = 48         # 큰 버튼 (실행)
    INPUT_HEIGHT = 40         # 입력 필드
    TAB_HEIGHT = 48           # 탭 바
    ICON_SIZE = 20            # 기본 아이콘
    BORDER_RADIUS = 8         # 기본 둥근 모서리
    BORDER_RADIUS_LG = 12     # 큰 둥근 모서리 (카드)
    MIN_TOUCH_TARGET = 44     # 최소 터치 영역 (접근성)

    # ===== 애니메이션 =====
    ANIMATION_FAST = 150      # 빠른 전환 (ms)
    ANIMATION_NORMAL = 250    # 일반 전환
    ANIMATION_SLOW = 350      # 느린 전환

    # ===== 그림자 (Elevation) =====
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1)"


# 편의를 위한 단축 별칭
DT = DesignTokens
