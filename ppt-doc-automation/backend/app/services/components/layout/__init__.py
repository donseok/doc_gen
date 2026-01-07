"""
레이아웃 컴포넌트 패키지

슬라이드 내부의 컴포넌트 배치를 담당하는 레이아웃 컴포넌트들을 제공합니다.

Modules:
    - two_column: 2열 레이아웃
    - grid: 그리드 레이아웃
"""

from .two_column import TwoColumnLayout
from .grid import GridLayout

__all__ = [
    'TwoColumnLayout',
    'GridLayout',
]
