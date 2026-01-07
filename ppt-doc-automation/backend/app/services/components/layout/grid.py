"""
그리드 레이아웃 컴포넌트

슬라이드를 rows x cols 격자로 분할하여 컴포넌트를 배치합니다.
"""

from typing import Dict, Any, List, Optional
from pptx.slide import Slide
from pptx.util import Emu, Pt, Cm

from ..base import BaseComponent, RenderContext
from ..factory import register_component, VisualComponentFactory


@register_component('grid', category='layout')
class GridLayout(BaseComponent):
    """그리드 레이아웃 컴포넌트
    
    슬라이드를 rows x cols 격자로 분할하여 컴포넌트를 배치합니다.
    
    Data Schema:
        {
            "rows": 2,
            "cols": 3,
            "gap": 0.3,  # 셀 간격 (cm)
            "cells": [
                {
                    "row": 0, "col": 0,
                    "rowspan": 1, "colspan": 1,  # 선택적
                    "element": {"type": "table", "data": {...}}
                },
                ...
            ]
        }
    """
    
    DEFAULT_GAP = Emu(Cm(0.3))
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """그리드 레이아웃 렌더링
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            data: 레이아웃 데이터
            top: 시작 Y 위치
            
        Returns:
            사용된 높이
        """
        rows = data.get('rows', 2)
        cols = data.get('cols', 2)
        gap = Emu(Cm(data.get('gap', 0.3)))
        cells = data.get('cells', [])
        
        if not cells:
            return Emu(0)
        
        # 셀 크기 계산
        total_h_gap = Emu(int(gap) * (cols - 1))
        total_v_gap = Emu(int(gap) * (rows - 1))
        
        cell_width = Emu((int(context.content_width) - int(total_h_gap)) // cols)
        
        # 기본 셀 높이 (가용 공간 기준)
        available_height = Emu(int(context.content_height) - int(top) + int(context.margin_top))
        cell_height = Emu((int(available_height) - int(total_v_gap)) // rows)
        
        left_start = context.get_content_start_x()
        
        max_used_height = Emu(0)
        
        for cell in cells:
            row = cell.get('row', 0)
            col = cell.get('col', 0)
            rowspan = cell.get('rowspan', 1)
            colspan = cell.get('colspan', 1)
            
            element = cell.get('element', {})
            
            # 셀 위치 계산
            cell_left = Emu(int(left_start) + col * (int(cell_width) + int(gap)))
            cell_top = Emu(int(top) + row * (int(cell_height) + int(gap)))
            
            # 병합된 셀 크기
            merged_width = Emu(colspan * int(cell_width) + (colspan - 1) * int(gap))
            merged_height = Emu(rowspan * int(cell_height) + (rowspan - 1) * int(gap))
            
            # 요소 렌더링
            height_used = self._render_cell(
                slide, context, element,
                cell_left, cell_top, merged_width, merged_height
            )
            
            # 최대 높이 추적
            cell_bottom = Emu(int(cell_top) + int(height_used) - int(top))
            if int(cell_bottom) > int(max_used_height):
                max_used_height = cell_bottom
        
        return max_used_height
    
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산"""
        rows = data.get('rows', 2)
        gap = Emu(Cm(data.get('gap', 0.3)))
        
        # 간단히 행 수 기반으로 계산
        cell_height = Emu(Cm(3))  # 기본 셀 높이
        total_v_gap = Emu(int(gap) * (rows - 1))
        
        return Emu(rows * int(cell_height) + int(total_v_gap))
    
    def _render_cell(
        self,
        slide: Slide,
        context: RenderContext,
        element: Dict[str, Any],
        left: Emu,
        top: Emu,
        width: Emu,
        height: Emu
    ) -> Emu:
        """셀 내 요소 렌더링
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            element: 요소 데이터
            left, top, width, height: 셀 위치 및 크기
            
        Returns:
            사용된 높이
        """
        element_type = element.get('type', '')
        element_data = element.get('data', element)
        
        if not element_type or not VisualComponentFactory.has_type(element_type):
            return Emu(0)
        
        # 셀 전용 컨텍스트 생성
        cell_context = RenderContext(
            theme=context.theme,
            slide_width=context.slide_width,
            slide_height=context.slide_height,
            margin_left=left,
            margin_right=Emu(int(context.slide_width) - int(left) - int(width)),
            margin_top=context.margin_top,
            margin_bottom=context.margin_bottom,
        )
        
        try:
            component = VisualComponentFactory.create(element_type)
            return component.render(slide, cell_context, element_data, top)
        except Exception as e:
            print(f"Warning: Failed to render cell element {element_type}: {e}")
            return Emu(0)
