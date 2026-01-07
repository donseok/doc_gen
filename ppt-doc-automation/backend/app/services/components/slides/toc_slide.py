"""
목차 슬라이드 컴포넌트

PPT 목차 슬라이드를 생성합니다.
동국제강 템플릿 Layout 2 (간지 1) 기반입니다.

레이아웃:
    - "Contents" 제목 (28pt, 본고딕 Bold, 네이비)
    - 3열 구조: 번호(01~05) | 목차 제목 | 페이지 범위
    - 오른쪽 배경 이미지/색상 영역
    - 하단 로고
"""

from typing import Dict, Any, List, Optional
from pptx.slide import Slide
from pptx.util import Emu, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from ..base import BaseSlideComponent, RenderContext
from ..factory import register_component


@register_component('toc', category='slide')
class TOCSlideComponent(BaseSlideComponent):
    """목차 슬라이드 컴포넌트
    
    템플릿 Layout 2 (간지 1) 기반:
        - "Contents" 제목
        - 3열 구조: 번호 | 목차 제목 | 페이지 범위
        - 오른쪽 배경 영역
        - 하단 로고
        
    Data Schema:
        {
            "title": "Contents",  # 선택적, 기본값 "Contents"
            "items": [
                {
                    "number": "01",
                    "title": "프로젝트 개요",
                    "page_range": "03-05"
                },
                ...
            ]
        }
    """
    
    # 레이아웃 상수 (PPT기본양식 분석 결과 기반)
    CONTENTS_TITLE_LEFT = Emu(892948)
    CONTENTS_TITLE_TOP = Emu(1683187)
    CONTENTS_TITLE_WIDTH = Emu(3341001)
    CONTENTS_TITLE_HEIGHT = Emu(329059)
    
    # 목차 항목 영역
    ITEMS_TOP = Emu(2276475)
    ITEMS_HEIGHT = Emu(3242876)
    
    # 번호 열 (ID:22)
    NUMBER_COL_LEFT = Emu(857551)
    NUMBER_COL_WIDTH = Emu(632205)
    
    # 제목 열 (ID:20)
    TITLE_COL_LEFT = Emu(1505513)
    TITLE_COL_WIDTH = Emu(3447487)
    
    # 페이지 범위 열 (ID:17)
    PAGE_COL_LEFT = Emu(6772319)
    PAGE_COL_WIDTH = Emu(938297)
    
    # 오른쪽 배경 영역
    RIGHT_BG_LEFT = Emu(7715250)
    RIGHT_BG_WIDTH = Emu(2190750)
    
    # 로고 위치
    LOGO_LEFT = Emu(270064)
    LOGO_TOP = Emu(6579886)
    LOGO_WIDTH = Emu(1215734)
    LOGO_HEIGHT = Emu(181025)
    
    # 항목별 높이 및 줄간격
    ITEM_HEIGHT = Emu(400000)  # 항목 하나당 높이
    LINE_SPACING_RATIO = 2.0  # 200% 줄간격
    
    MAX_ITEMS = 5  # 최대 목차 항목 수
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any]
    ) -> None:
        """목차 슬라이드 렌더링
        
        Args:
            slide: 렌더링할 슬라이드 객체
            context: 렌더링 컨텍스트
            data: 슬라이드 데이터 (title, items)
        """
        # 1. 상단 그라데이션 바
        self._add_header_bar(slide, context)
        
        # 2. "Contents" 제목
        title = data.get('title', 'Contents')
        self._add_contents_title(slide, context, title)
        
        # 3. 오른쪽 배경 영역
        self._add_right_background(slide, context)
        
        # 4. 목차 항목들
        items = data.get('items', [])
        self._add_toc_items(slide, context, items)
        
        # 5. 로고
        if context.theme.logo_path:
            self._add_logo(slide, context, context.theme.logo_path)
    
    def _add_contents_title(
        self,
        slide: Slide,
        context: RenderContext,
        title: str
    ) -> None:
        """Contents 제목 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            title: 제목 텍스트 (기본: "Contents")
        """
        shape = slide.shapes.add_textbox(
            self.CONTENTS_TITLE_LEFT,
            self.CONTENTS_TITLE_TOP,
            self.CONTENTS_TITLE_WIDTH,
            self.CONTENTS_TITLE_HEIGHT
        )
        
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.title_font
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = context.theme.colors.primary
    
    def _add_right_background(
        self,
        slide: Slide,
        context: RenderContext
    ) -> None:
        """오른쪽 배경 영역 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
        """
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            self.RIGHT_BG_LEFT,
            Emu(0),
            self.RIGHT_BG_WIDTH,
            context.slide_height
        )
        
        # 배경색 설정 (primary 색상의 밝은 버전)
        shape.fill.solid()
        shape.fill.fore_color.rgb = context.theme.colors.accent3  # 연한 청록색
        shape.line.fill.background()  # 테두리 없음
    
    def _add_toc_items(
        self,
        slide: Slide,
        context: RenderContext,
        items: List[Dict[str, Any]]
    ) -> None:
        """목차 항목들 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            items: 목차 항목 리스트
        """
        # 최대 항목 수 제한
        items = items[:self.MAX_ITEMS]
        
        if not items:
            return
        
        # 각 항목의 높이 계산
        total_height = int(self.ITEMS_HEIGHT)
        item_spacing = total_height // max(len(items), 1)
        
        for i, item in enumerate(items):
            current_top = Emu(int(self.ITEMS_TOP) + i * item_spacing)
            item_height = Emu(item_spacing)
            
            # 번호 열
            number = item.get('number', f"{i+1:02d}")
            self._add_number_cell(slide, context, number, current_top, item_height)
            
            # 제목 열
            title = item.get('title', '')
            self._add_title_cell(slide, context, title, current_top, item_height)
            
            # 페이지 범위 열
            page_range = item.get('page_range', '')
            if page_range:
                self._add_page_cell(slide, context, page_range, current_top, item_height)
    
    def _add_number_cell(
        self,
        slide: Slide,
        context: RenderContext,
        number: str,
        top: Emu,
        height: Emu
    ) -> None:
        """번호 셀 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            number: 번호 텍스트
            top: Y 위치
            height: 높이
        """
        shape = slide.shapes.add_textbox(
            self.NUMBER_COL_LEFT,
            top,
            self.NUMBER_COL_WIDTH,
            height
        )
        
        tf = shape.text_frame
        tf.word_wrap = False
        
        p = tf.paragraphs[0]
        p.text = number
        p.alignment = PP_ALIGN.RIGHT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.body_font
        run.font.size = Pt(16)
        run.font.color.rgb = context.theme.colors.primary
    
    def _add_title_cell(
        self,
        slide: Slide,
        context: RenderContext,
        title: str,
        top: Emu,
        height: Emu
    ) -> None:
        """제목 셀 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            title: 제목 텍스트
            top: Y 위치
            height: 높이
        """
        shape = slide.shapes.add_textbox(
            self.TITLE_COL_LEFT,
            top,
            self.TITLE_COL_WIDTH,
            height
        )
        
        tf = shape.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.body_font
        run.font.size = Pt(16)
        run.font.color.rgb = context.theme.colors.text_primary
    
    def _add_page_cell(
        self,
        slide: Slide,
        context: RenderContext,
        page_range: str,
        top: Emu,
        height: Emu
    ) -> None:
        """페이지 범위 셀 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            page_range: 페이지 범위 텍스트 (예: "01-05")
            top: Y 위치
            height: 높이
        """
        shape = slide.shapes.add_textbox(
            self.PAGE_COL_LEFT,
            top,
            self.PAGE_COL_WIDTH,
            height
        )
        
        tf = shape.text_frame
        tf.word_wrap = False
        
        p = tf.paragraphs[0]
        p.text = page_range
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.caption_font
        run.font.size = Pt(14)
        run.font.color.rgb = context.theme.colors.text_secondary
    
    def _add_logo(
        self,
        slide: Slide,
        context: RenderContext,
        logo_path: str
    ) -> None:
        """로고 이미지 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            logo_path: 로고 이미지 경로
        """
        import os
        
        if not os.path.exists(logo_path):
            return
        
        slide.shapes.add_picture(
            logo_path,
            self.LOGO_LEFT,
            self.LOGO_TOP,
            self.LOGO_WIDTH,
            self.LOGO_HEIGHT
        )
