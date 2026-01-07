"""
섹션 구분 슬라이드 컴포넌트

PPT 섹션 구분 슬라이드를 생성합니다.
챕터/섹션 시작을 표시하는 간단한 슬라이드입니다.
"""

from typing import Dict, Any, Optional
from pptx.slide import Slide
from pptx.util import Emu, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from ..base import BaseSlideComponent, RenderContext
from ..factory import register_component


@register_component('section', category='slide')
class SectionSlideComponent(BaseSlideComponent):
    """섹션 구분 슬라이드 컴포넌트
    
    챕터/섹션 시작을 표시하는 슬라이드입니다.
    화면 중앙에 큰 섹션 번호와 제목을 표시합니다.
        
    Data Schema:
        {
            "section_number": "01",
            "title": "프로젝트 개요",
            "subtitle": "Project Overview"  # 선택적
        }
    """
    
    # 슬라이드 중앙 배치를 위한 상수
    CENTER_Y = Emu(2800000)  # 세로 중앙 근처
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any]
    ) -> None:
        """섹션 슬라이드 렌더링
        
        Args:
            slide: 렌더링할 슬라이드 객체
            context: 렌더링 컨텍스트
            data: 슬라이드 데이터
        """
        # 1. 상단 그라데이션 바
        self._add_header_bar(slide, context)
        
        # 2. 배경 색상 영역 (선택적)
        self._add_background_accent(slide, context)
        
        # 3. 섹션 번호 (큰 텍스트)
        section_number = data.get('section_number', '')
        if section_number:
            self._add_section_number(slide, context, section_number)
        
        # 4. 섹션 제목
        title = data.get('title', '')
        self._add_section_title(slide, context, title, has_number=bool(section_number))
        
        # 5. 부제목 (선택적)
        subtitle = data.get('subtitle', '')
        if subtitle:
            self._add_section_subtitle(slide, context, subtitle)
        
        # 6. 로고
        if context.theme.logo_path:
            self._add_logo(slide, context, context.theme.logo_path)
    
    def _add_background_accent(
        self,
        slide: Slide,
        context: RenderContext
    ) -> None:
        """배경 강조 영역 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
        """
        # 오른쪽에 강조 색상 영역
        accent_width = Emu(int(context.slide_width) // 3)
        
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Emu(int(context.slide_width) - int(accent_width)),
            Emu(0),
            accent_width,
            context.slide_height
        )
        
        shape.fill.solid()
        shape.fill.fore_color.rgb = context.theme.colors.primary
        shape.line.fill.background()
    
    def _add_section_number(
        self,
        slide: Slide,
        context: RenderContext,
        number: str
    ) -> None:
        """섹션 번호 추가 (큰 텍스트)
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            number: 섹션 번호
        """
        left = Emu(int(context.margin_left))
        top = Emu(int(self.CENTER_Y) - Emu(Cm(2)))
        width = Emu(int(context.content_width) * 2 // 3)
        height = Emu(Cm(2))
        
        shape = slide.shapes.add_textbox(left, top, width, height)
        
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = number
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.title_font
        run.font.size = Pt(72)
        run.font.bold = True
        run.font.color.rgb = context.theme.colors.accent
    
    def _add_section_title(
        self,
        slide: Slide,
        context: RenderContext,
        title: str,
        has_number: bool = False
    ) -> None:
        """섹션 제목 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            title: 제목 텍스트
            has_number: 섹션 번호 존재 여부
        """
        left = Emu(int(context.margin_left))
        top = self.CENTER_Y if has_number else Emu(int(self.CENTER_Y) - Emu(Cm(1)))
        width = Emu(int(context.content_width) * 2 // 3)
        height = Emu(Cm(1.5))
        
        shape = slide.shapes.add_textbox(left, top, width, height)
        
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.title_font
        run.font.size = Pt(36)
        run.font.bold = True
        run.font.color.rgb = context.theme.colors.primary
    
    def _add_section_subtitle(
        self,
        slide: Slide,
        context: RenderContext,
        subtitle: str
    ) -> None:
        """섹션 부제목 추가
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            subtitle: 부제목 텍스트
        """
        left = Emu(int(context.margin_left))
        top = Emu(int(self.CENTER_Y) + Emu(Cm(1.5)))
        width = Emu(int(context.content_width) * 2 // 3)
        height = Emu(Cm(1))
        
        shape = slide.shapes.add_textbox(left, top, width, height)
        
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = subtitle
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.body_font
        run.font.size = Pt(18)
        run.font.color.rgb = context.theme.colors.text_secondary
