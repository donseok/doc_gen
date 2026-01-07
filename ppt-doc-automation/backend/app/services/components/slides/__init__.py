"""
슬라이드 컴포넌트 패키지

슬라이드 전체를 구성하는 컴포넌트들을 제공합니다.

Modules:
    - title_slide: 표지 슬라이드
    - toc_slide: 목차 슬라이드
    - content_slide: 본문 슬라이드
    - section_slide: 섹션 구분 슬라이드
"""

from .title_slide import TitleSlideComponent
from .toc_slide import TOCSlideComponent
from .content_slide import ContentSlideComponent
from .section_slide import SectionSlideComponent

__all__ = [
    'TitleSlideComponent',
    'TOCSlideComponent',
    'ContentSlideComponent',
    'SectionSlideComponent',
]
