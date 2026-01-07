"""
2열 레이아웃 컴포넌트

슬라이드를 좌/우 2개 열로 분할하여 컴포넌트를 배치합니다.
"""

from typing import Dict, Any, List, Optional
from pptx.slide import Slide
from pptx.util import Emu, Pt, Cm

from ..base import BaseComponent, RenderContext
from ..factory import register_component, VisualComponentFactory


@register_component('two_column', category='layout')
class TwoColumnLayout(BaseComponent):
    """2열 레이아웃 컴포넌트
    
    슬라이드를 좌/우 2개 열로 분할하여 컴포넌트를 배치합니다.
    
    Data Schema:
        {
            "ratio": [0.5, 0.5],  # 좌/우 비율 (기본: 50:50)
            "gap": 0.5,  # 열 간격 (cm)
            "left": {
                "elements": [
                    {"type": "table", "data": {...}},
                    ...
                ]
            },
            "right": {
                "elements": [
                    {"type": "big_numbers", "data": {...}},
                    ...
                ]
            }
        }
    """
    
    DEFAULT_GAP = Emu(Cm(0.5))
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """2열 레이아웃 렌더링
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            data: 레이아웃 데이터
            top: 시작 Y 위치
            
        Returns:
            사용된 높이 (좌/우 중 더 큰 높이)
        """
        ratio = data.get('ratio', [0.5, 0.5])
        gap = Emu(Cm(data.get('gap', 0.5)))
        
        left_data = data.get('left', {})
        right_data = data.get('right', {})
        
        # 열 너비 계산
        available_width = Emu(int(context.content_width) - int(gap))
        left_width = Emu(int(available_width) * ratio[0])
        right_width = Emu(int(available_width) * ratio[1])
        
        # 열 시작 위치
        left_start = context.get_content_start_x()
        right_start = Emu(int(left_start) + int(left_width) + int(gap))
        
        # 왼쪽 열 렌더링
        left_height = self._render_column(
            slide, context, left_data, 
            left_start, top, left_width
        )
        
        # 오른쪽 열 렌더링
        right_height = self._render_column(
            slide, context, right_data,
            right_start, top, right_width
        )
        
        # 더 큰 높이 반환
        return Emu(max(int(left_height), int(right_height)))
    
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산"""
        left_data = data.get('left', {})
        right_data = data.get('right', {})
        
        left_height = self._calculate_column_height(context, left_data)
        right_height = self._calculate_column_height(context, right_data)
        
        return Emu(max(int(left_height), int(right_height)))
    
    def _render_column(
        self,
        slide: Slide,
        context: RenderContext,
        column_data: Dict[str, Any],
        left: Emu,
        top: Emu,
        width: Emu
    ) -> Emu:
        """단일 열 렌더링
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            column_data: 열 데이터
            left: 열 시작 X 위치
            top: 시작 Y 위치
            width: 열 너비
            
        Returns:
            사용된 높이
        """
        elements = column_data.get('elements', [])
        
        if not elements:
            return Emu(0)
        
        # 열 전용 컨텍스트 생성 (너비 조정)
        column_context = RenderContext(
            theme=context.theme,
            slide_width=context.slide_width,
            slide_height=context.slide_height,
            margin_left=left,
            margin_right=Emu(int(context.slide_width) - int(left) - int(width)),
            margin_top=context.margin_top,
            margin_bottom=context.margin_bottom,
        )
        
        current_top = top
        element_gap = Emu(Cm(0.3))
        
        for element in elements:
            element_type = element.get('type', '')
            element_data = element.get('data', element)
            
            if not VisualComponentFactory.has_type(element_type):
                continue
            
            try:
                component = VisualComponentFactory.create(element_type)
                height_used = component.render(slide, column_context, element_data, current_top)
                current_top = Emu(int(current_top) + int(height_used) + int(element_gap))
            except Exception as e:
                print(f"Warning: Failed to render {element_type}: {e}")
                continue
        
        return Emu(int(current_top) - int(top))
    
    def _calculate_column_height(
        self,
        context: RenderContext,
        column_data: Dict[str, Any]
    ) -> Emu:
        """열 높이 계산"""
        elements = column_data.get('elements', [])
        
        if not elements:
            return Emu(0)
        
        total_height = Emu(0)
        element_gap = Emu(Cm(0.3))
        
        for element in elements:
            element_type = element.get('type', '')
            element_data = element.get('data', element)
            
            if not VisualComponentFactory.has_type(element_type):
                continue
            
            try:
                component = VisualComponentFactory.create(element_type)
                height = component.get_required_height(context, element_data)
                total_height = Emu(int(total_height) + int(height) + int(element_gap))
            except Exception:
                continue
        
        return total_height
