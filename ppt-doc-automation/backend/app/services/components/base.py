"""
컴포넌트 기본 인터페이스

모든 PPT 컴포넌트의 기본 클래스와 렌더링 컨텍스트를 정의합니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from pptx.slide import Slide
from pptx.util import Emu, Pt, Inches, Cm
from pptx.dml.color import RGBColor

if TYPE_CHECKING:
    from .theme import ThemeConfig


@dataclass
class RenderContext:
    """렌더링 컨텍스트: 테마, 폰트, 색상 등 공유 설정
    
    모든 컴포넌트가 렌더링 시 참조하는 공통 설정입니다.
    
    Attributes:
        theme: 적용할 테마 설정
        slide_width: 슬라이드 너비 (EMU)
        slide_height: 슬라이드 높이 (EMU)
        margin_left: 좌측 여백 (EMU)
        margin_right: 우측 여백 (EMU)
        margin_top: 상단 여백 (EMU)
        margin_bottom: 하단 여백 (EMU)
        content_width: 콘텐츠 영역 너비 (EMU)
        content_height: 콘텐츠 영역 높이 (EMU)
        current_y: 현재 Y 위치 (렌더링 진행 추적용)
    """
    theme: 'ThemeConfig'
    slide_width: Emu = field(default_factory=lambda: Emu(9906000))   # A4 가로
    slide_height: Emu = field(default_factory=lambda: Emu(6858000))  # A4 가로
    margin_left: Emu = field(default_factory=lambda: Emu(270064))    # 약 0.75cm
    margin_right: Emu = field(default_factory=lambda: Emu(270064))
    margin_top: Emu = field(default_factory=lambda: Emu(171278))     # 약 0.48cm
    margin_bottom: Emu = field(default_factory=lambda: Emu(250000))
    
    @property
    def content_width(self) -> Emu:
        """콘텐츠 영역 너비 계산"""
        return Emu(int(self.slide_width) - int(self.margin_left) - int(self.margin_right))
    
    @property
    def content_height(self) -> Emu:
        """콘텐츠 영역 높이 계산"""
        return Emu(int(self.slide_height) - int(self.margin_top) - int(self.margin_bottom))
    
    def get_content_start_x(self) -> Emu:
        """콘텐츠 시작 X 좌표"""
        return self.margin_left
    
    def get_content_start_y(self) -> Emu:
        """콘텐츠 시작 Y 좌표"""
        return self.margin_top


class BaseComponent(ABC):
    """모든 컴포넌트의 기본 추상 클래스
    
    PPT 슬라이드에 렌더링되는 모든 요소의 기본 인터페이스입니다.
    
    Methods:
        render: 컴포넌트를 슬라이드에 렌더링
        get_required_height: 필요한 높이 계산
    """
    
    @abstractmethod
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """컴포넌트를 슬라이드에 렌더링
        
        Args:
            slide: 렌더링할 슬라이드 객체
            context: 렌더링 컨텍스트 (테마, 설정 등)
            data: 컴포넌트 데이터
            top: 시작 Y 위치 (EMU)
            **kwargs: 추가 옵션
            
        Returns:
            사용된 높이 (EMU) - 다음 컴포넌트의 시작 위치 계산용
        """
        pass
    
    @abstractmethod
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산 (레이아웃 계획용)
        
        Args:
            context: 렌더링 컨텍스트
            data: 컴포넌트 데이터
            **kwargs: 추가 옵션
            
        Returns:
            필요한 높이 (EMU)
        """
        pass
    
    def _create_textbox(
        self,
        slide: Slide,
        left: Emu,
        top: Emu,
        width: Emu,
        height: Emu,
        text: str,
        font_name: str = "본고딕 Medium",
        font_size: Pt = Pt(12),
        font_color: Optional[RGBColor] = None,
        bold: bool = False,
        align: str = "left"
    ):
        """텍스트 박스 생성 헬퍼
        
        Args:
            slide: 슬라이드 객체
            left, top, width, height: 위치 및 크기 (EMU)
            text: 텍스트 내용
            font_name: 폰트 이름
            font_size: 폰트 크기
            font_color: 폰트 색상 (RGBColor)
            bold: 굵게 여부
            align: 정렬 (left, center, right)
            
        Returns:
            생성된 shape 객체
        """
        from pptx.enum.text import PP_ALIGN
        
        shape = slide.shapes.add_textbox(left, top, width, height)
        tf = shape.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = text
        
        # 정렬 설정
        align_map = {
            "left": PP_ALIGN.LEFT,
            "center": PP_ALIGN.CENTER,
            "right": PP_ALIGN.RIGHT,
        }
        p.alignment = align_map.get(align, PP_ALIGN.LEFT)
        
        # 폰트 설정
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = font_name
        run.font.size = font_size
        run.font.bold = bold
        if font_color:
            run.font.color.rgb = font_color
            
        return shape
    
    def _create_rectangle(
        self,
        slide: Slide,
        left: Emu,
        top: Emu,
        width: Emu,
        height: Emu,
        fill_color: Optional[RGBColor] = None,
        line_color: Optional[RGBColor] = None,
        line_width: Optional[Pt] = None
    ):
        """사각형 도형 생성 헬퍼
        
        Args:
            slide: 슬라이드 객체
            left, top, width, height: 위치 및 크기 (EMU)
            fill_color: 채우기 색상
            line_color: 테두리 색상
            line_width: 테두리 두께
            
        Returns:
            생성된 shape 객체
        """
        from pptx.enum.shapes import MSO_SHAPE
        
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left, top, width, height
        )
        
        if fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = fill_color
        else:
            shape.fill.background()  # 투명
            
        if line_color and line_width:
            shape.line.color.rgb = line_color
            shape.line.width = line_width
        else:
            shape.line.fill.background()  # 테두리 없음
            
        return shape


class BaseSlideComponent(ABC):
    """슬라이드 전체를 구성하는 컴포넌트의 기본 클래스
    
    표지, 목차, 본문 등 슬라이드 전체를 담당하는 컴포넌트입니다.
    일반 BaseComponent와 달리 슬라이드 생성부터 담당합니다.
    
    Methods:
        render: 슬라이드 전체를 렌더링
    """
    
    @abstractmethod
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any]
    ) -> None:
        """슬라이드 전체를 렌더링
        
        Args:
            slide: 렌더링할 슬라이드 객체
            context: 렌더링 컨텍스트
            data: 슬라이드 데이터
        """
        pass
    
    def _add_header_bar(
        self, 
        slide: Slide, 
        context: RenderContext
    ) -> None:
        """상단 그라데이션 바 추가 (공통 요소)
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
        """
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.oxml.ns import nsmap
        from pptx.oxml import parse_xml
        
        bar_height = Emu(36000)  # 약 0.1cm
        
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Emu(0),
            Emu(0),
            context.slide_width,
            bar_height
        )
        shape.line.fill.background()  # 테두리 없음
        
        # 그라데이션 적용 (빨강 → 네이비)
        fill = shape.fill
        fill.gradient()
        fill.gradient_angle = 0  # 좌→우
        fill.gradient_stops[0].color.rgb = context.theme.colors.accent  # 빨강
        fill.gradient_stops[1].color.rgb = context.theme.colors.primary  # 네이비
    
    def _add_footer(
        self, 
        slide: Slide, 
        context: RenderContext,
        slide_number: Optional[int] = None,
        footer_text: str = ""
    ) -> None:
        """바닥글 및 슬라이드 번호 추가 (공통 요소)
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            slide_number: 슬라이드 번호 (None이면 표시 안함)
            footer_text: 바닥글 텍스트
        """
        from pptx.enum.text import PP_ALIGN
        
        footer_y = Emu(6601746)  # 하단 고정 위치
        footer_height = Emu(147600)
        
        # 바닥글 텍스트
        if footer_text:
            footer_left = Emu(7788317)
            footer_width = Emu(1534561)
            
            shape = slide.shapes.add_textbox(
                footer_left, footer_y, footer_width, footer_height
            )
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.text = footer_text
            p.alignment = PP_ALIGN.RIGHT
            
            run = p.runs[0]
            run.font.size = Pt(8)
            run.font.name = "본고딕 Normal"
            run.font.color.rgb = context.theme.colors.text_secondary
        
        # 슬라이드 번호
        if slide_number is not None:
            num_left = Emu(9264136)
            num_width = Emu(374513)
            
            shape = slide.shapes.add_textbox(
                num_left, footer_y, num_width, footer_height
            )
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.text = str(slide_number)
            p.alignment = PP_ALIGN.RIGHT
            
            run = p.runs[0]
            run.font.size = Pt(8)
            run.font.name = "본고딕 Normal"
            run.font.color.rgb = context.theme.colors.text_secondary
    
    def _add_logo(
        self,
        slide: Slide,
        context: RenderContext,
        logo_path: Optional[str] = None
    ) -> None:
        """로고 이미지 추가 (공통 요소)
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            logo_path: 로고 이미지 경로 (None이면 스킵)
        """
        import os
        
        if not logo_path or not os.path.exists(logo_path):
            return
            
        logo_left = Emu(270064)
        logo_top = Emu(6579886)
        logo_width = Emu(1215734)
        logo_height = Emu(181025)
        
        slide.shapes.add_picture(
            logo_path,
            logo_left, logo_top,
            logo_width, logo_height
        )
