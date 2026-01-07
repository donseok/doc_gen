"""
테마 및 색상 설정

PPT 컴포넌트에서 사용하는 테마, 색상 팔레트, 폰트 설정을 정의합니다.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from pptx.dml.color import RGBColor


def hex_to_rgb(hex_color: str) -> RGBColor:
    """HEX 색상을 RGBColor로 변환
    
    Args:
        hex_color: HEX 색상 문자열 (예: "#002452" 또는 "002452")
        
    Returns:
        RGBColor 객체
    """
    hex_color = hex_color.lstrip('#')
    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


@dataclass
class ColorPalette:
    """색상 팔레트
    
    PPT 문서 전반에 사용되는 색상 정의입니다.
    동국제강 테마 기준으로 설계되었습니다.
    
    Attributes:
        primary: 주 색상 (네이비 #002452)
        secondary: 보조 색상 (회색)
        accent: 강조 색상 (빨강 #C51F2A)
        background: 배경색 (흰색)
        text_primary: 기본 텍스트 색상 (어두운 회색)
        text_secondary: 보조 텍스트 색상 (밝은 회색)
        text_on_dark: 어두운 배경 위 텍스트 (흰색)
        
        # 추가 악센트 색상들
        accent1: 회색 강조
        accent2: 청회색
        accent3: 연한 청록색
        accent4: 빨강 (accent와 동일)
        accent5: 주황-빨강
        accent6: 금색/황토색
    """
    primary: RGBColor = field(default_factory=lambda: hex_to_rgb("#002452"))
    secondary: RGBColor = field(default_factory=lambda: hex_to_rgb("#B6B6B6"))
    accent: RGBColor = field(default_factory=lambda: hex_to_rgb("#C51F2A"))
    background: RGBColor = field(default_factory=lambda: hex_to_rgb("#FFFFFF"))
    text_primary: RGBColor = field(default_factory=lambda: hex_to_rgb("#262626"))
    text_secondary: RGBColor = field(default_factory=lambda: hex_to_rgb("#757575"))
    text_on_dark: RGBColor = field(default_factory=lambda: hex_to_rgb("#FFFFFF"))
    
    # 추가 악센트 색상 (동국제강 테마 기준)
    accent1: RGBColor = field(default_factory=lambda: hex_to_rgb("#757575"))
    accent2: RGBColor = field(default_factory=lambda: hex_to_rgb("#4B6580"))
    accent3: RGBColor = field(default_factory=lambda: hex_to_rgb("#B7D0D4"))
    accent4: RGBColor = field(default_factory=lambda: hex_to_rgb("#C51F2A"))
    accent5: RGBColor = field(default_factory=lambda: hex_to_rgb("#D55633"))
    accent6: RGBColor = field(default_factory=lambda: hex_to_rgb("#E9B86E"))


@dataclass
class FontSettings:
    """폰트 설정
    
    PPT 문서에서 사용하는 폰트 정의입니다.
    
    Attributes:
        title_font: 제목용 폰트 (굵은 폰트)
        body_font: 본문용 폰트 (중간 굵기)
        caption_font: 캡션/작은 텍스트용 폰트
        en_font: 영문 전용 폰트
        
        title_size: 제목 폰트 크기 (pt)
        subtitle_size: 부제목 폰트 크기 (pt)
        body_size: 본문 폰트 크기 (pt)
        caption_size: 캡션 폰트 크기 (pt)
    """
    title_font: str = "본고딕 Bold"
    body_font: str = "본고딕 Medium"
    caption_font: str = "본고딕 Normal"
    en_font: str = "본고딕 Normal"
    
    # 폰트 크기 (pt)
    title_size: int = 32
    subtitle_size: int = 17
    body_size: int = 16
    caption_size: int = 12
    slide_number_size: int = 8
    
    # Action Title 관련
    main_title_size: int = 19
    action_title_size: int = 17


@dataclass
class ThemeConfig:
    """테마 설정
    
    PPT 문서 전체에 적용되는 테마 설정입니다.
    색상 팔레트와 폰트 설정을 포함합니다.
    
    Attributes:
        name: 테마 이름
        colors: 색상 팔레트
        fonts: 폰트 설정
        logo_path: 로고 이미지 경로 (선택적)
    """
    name: str = "dongkuk"
    colors: ColorPalette = field(default_factory=ColorPalette)
    fonts: FontSettings = field(default_factory=FontSettings)
    logo_path: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThemeConfig':
        """딕셔너리에서 ThemeConfig 생성
        
        Args:
            data: 테마 설정 딕셔너리
            
        Returns:
            ThemeConfig 인스턴스
        """
        colors_data = data.get('colors', {})
        fonts_data = data.get('fonts', {})
        
        colors = ColorPalette(
            primary=hex_to_rgb(colors_data.get('primary', '#002452')),
            secondary=hex_to_rgb(colors_data.get('secondary', '#B6B6B6')),
            accent=hex_to_rgb(colors_data.get('accent', '#C51F2A')),
            background=hex_to_rgb(colors_data.get('background', '#FFFFFF')),
            text_primary=hex_to_rgb(colors_data.get('text_primary', '#262626')),
            text_secondary=hex_to_rgb(colors_data.get('text_secondary', '#757575')),
        )
        
        fonts = FontSettings(
            title_font=fonts_data.get('title_font', '본고딕 Bold'),
            body_font=fonts_data.get('body_font', '본고딕 Medium'),
            caption_font=fonts_data.get('caption_font', '본고딕 Normal'),
        )
        
        return cls(
            name=data.get('name', 'custom'),
            colors=colors,
            fonts=fonts,
            logo_path=data.get('logo_path'),
        )


# 사전 정의된 테마들
class DongkukTheme(ThemeConfig):
    """동국제강 브랜드 테마
    
    동국제강 PPT 템플릿 분석 결과를 기반으로 한 테마입니다.
    
    색상 스킴:
        - Primary (네이비): #002452
        - Accent (빨강): #C51F2A
        - Secondary (회색): #B6B6B6
        
    폰트:
        - 제목: 본고딕 Bold/Medium
        - 본문: 본고딕 Medium/Normal
    """
    
    def __init__(self, logo_path: Optional[str] = None):
        super().__init__(
            name="dongkuk",
            colors=ColorPalette(
                primary=hex_to_rgb("#002452"),      # 네이비
                secondary=hex_to_rgb("#B6B6B6"),    # 밝은 회색
                accent=hex_to_rgb("#C51F2A"),       # 빨강
                background=hex_to_rgb("#FFFFFF"),   # 흰색
                text_primary=hex_to_rgb("#262626"), # 어두운 회색
                text_secondary=hex_to_rgb("#757575"), # 중간 회색
                text_on_dark=hex_to_rgb("#FFFFFF"), # 흰색
                
                accent1=hex_to_rgb("#757575"),
                accent2=hex_to_rgb("#4B6580"),
                accent3=hex_to_rgb("#B7D0D4"),
                accent4=hex_to_rgb("#C51F2A"),
                accent5=hex_to_rgb("#D55633"),
                accent6=hex_to_rgb("#E9B86E"),
            ),
            fonts=FontSettings(
                title_font="본고딕 Bold",
                body_font="본고딕 Medium",
                caption_font="본고딕 Normal",
                en_font="본고딕 Normal",
                title_size=32,
                subtitle_size=14,
                body_size=16,
                caption_size=12,
                main_title_size=19,
                action_title_size=17,
            ),
            logo_path=logo_path,
        )


class ModernBlueTheme(ThemeConfig):
    """모던 블루 테마
    
    깔끔한 비즈니스 스타일의 파란색 계열 테마입니다.
    """
    
    def __init__(self, logo_path: Optional[str] = None):
        super().__init__(
            name="modern_blue",
            colors=ColorPalette(
                primary=hex_to_rgb("#1E3A8A"),
                secondary=hex_to_rgb("#64748B"),
                accent=hex_to_rgb("#3B82F6"),
                background=hex_to_rgb("#FFFFFF"),
                text_primary=hex_to_rgb("#1E293B"),
                text_secondary=hex_to_rgb("#64748B"),
                text_on_dark=hex_to_rgb("#FFFFFF"),
            ),
            fonts=FontSettings(
                title_font="맑은 고딕",
                body_font="맑은 고딕",
                caption_font="맑은 고딕",
            ),
            logo_path=logo_path,
        )


class CorporateTheme(ThemeConfig):
    """코퍼레이트 테마
    
    전통적인 기업 스타일의 차분한 색상 테마입니다.
    """
    
    def __init__(self, logo_path: Optional[str] = None):
        super().__init__(
            name="corporate",
            colors=ColorPalette(
                primary=hex_to_rgb("#1F2937"),
                secondary=hex_to_rgb("#6B7280"),
                accent=hex_to_rgb("#059669"),
                background=hex_to_rgb("#FFFFFF"),
                text_primary=hex_to_rgb("#111827"),
                text_secondary=hex_to_rgb("#6B7280"),
                text_on_dark=hex_to_rgb("#FFFFFF"),
            ),
            fonts=FontSettings(
                title_font="맑은 고딕",
                body_font="맑은 고딕",
                caption_font="맑은 고딕",
            ),
            logo_path=logo_path,
        )


class DarkTheme(ThemeConfig):
    """다크 테마
    
    어두운 배경의 프레젠테이션 테마입니다.
    """
    
    def __init__(self, logo_path: Optional[str] = None):
        super().__init__(
            name="dark",
            colors=ColorPalette(
                primary=hex_to_rgb("#111827"),
                secondary=hex_to_rgb("#374151"),
                accent=hex_to_rgb("#F59E0B"),
                background=hex_to_rgb("#1F2937"),
                text_primary=hex_to_rgb("#F9FAFB"),
                text_secondary=hex_to_rgb("#9CA3AF"),
                text_on_dark=hex_to_rgb("#FFFFFF"),
            ),
            fonts=FontSettings(
                title_font="맑은 고딕",
                body_font="맑은 고딕",
                caption_font="맑은 고딕",
            ),
            logo_path=logo_path,
        )


# 테마 레지스트리
THEME_REGISTRY: Dict[str, type] = {
    "dongkuk": DongkukTheme,
    "modern_blue": ModernBlueTheme,
    "corporate": CorporateTheme,
    "dark": DarkTheme,
}


def get_theme(theme_name: str, logo_path: Optional[str] = None) -> ThemeConfig:
    """테마 이름으로 ThemeConfig 인스턴스 생성
    
    Args:
        theme_name: 테마 이름 (dongkuk, modern_blue, corporate, dark)
        logo_path: 로고 이미지 경로 (선택적)
        
    Returns:
        ThemeConfig 인스턴스
        
    Raises:
        ValueError: 알 수 없는 테마 이름인 경우
    """
    if theme_name not in THEME_REGISTRY:
        raise ValueError(f"Unknown theme: {theme_name}. Available: {list(THEME_REGISTRY.keys())}")
    
    theme_class = THEME_REGISTRY[theme_name]
    return theme_class(logo_path=logo_path)
