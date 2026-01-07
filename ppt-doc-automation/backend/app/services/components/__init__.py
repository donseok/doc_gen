"""
PPT 컴포넌트 라이브러리

재사용 가능한 PPT 슬라이드 및 시각 요소 컴포넌트들을 제공합니다.

Modules:
    - base: 기본 컴포넌트 인터페이스
    - theme: 테마 및 색상 설정
    - factory: 컴포넌트 팩토리
    - slides: 슬라이드 컴포넌트들
    - visual: 시각 요소 컴포넌트들
    - layout: 레이아웃 컴포넌트들
"""

from .base import BaseComponent, BaseSlideComponent, RenderContext
from .theme import ThemeConfig, ColorPalette, FontSettings, DongkukTheme

__all__ = [
    'BaseComponent',
    'BaseSlideComponent', 
    'RenderContext',
    'ThemeConfig',
    'ColorPalette',
    'FontSettings',
    'DongkukTheme',
]
