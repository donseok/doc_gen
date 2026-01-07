"""
표 컴포넌트

PPT 슬라이드에 표를 생성합니다.

지원 스타일:
    - default: 기본 표
    - header_highlight: 헤더 강조 표
    - alternate_rows: 교차 행 색상 표
"""

from typing import Dict, Any, List, Optional
from pptx.slide import Slide
from pptx.util import Emu, Pt, Cm, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.table import Table

from ..base import BaseComponent, RenderContext
from ..factory import register_component


@register_component('table', category='visual')
class TableComponent(BaseComponent):
    """표 컴포넌트
    
    PPT 슬라이드에 표를 생성합니다.
    
    지원 스타일:
        - default: 기본 표
        - header_highlight: 헤더 강조 (배경색)
        - alternate_rows: 교차 행 색상
        - minimal: 최소화된 스타일 (테두리만)
        
    Data Schema:
        {
            "headers": ["열1", "열2", "열3"],
            "rows": [
                ["데이터1", "데이터2", "데이터3"],
                ["데이터4", "데이터5", "데이터6"],
            ],
            "style": "header_highlight",  # 선택적
            "column_widths": [0.3, 0.4, 0.3],  # 비율, 선택적
            "max_rows": 6  # 최대 행 수, 선택적
        }
    """
    
    DEFAULT_ROW_HEIGHT = Emu(Cm(0.8))
    HEADER_ROW_HEIGHT = Emu(Cm(1.0))
    MAX_ROWS = 10
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """표 렌더링
        
        Args:
            slide: 슬라이드 객체
            context: 렌더링 컨텍스트
            data: 표 데이터
            top: 시작 Y 위치
            
        Returns:
            사용된 높이 (EMU)
        """
        headers = data.get('headers', [])
        rows = data.get('rows', [])
        style = data.get('style', 'header_highlight')
        column_widths = data.get('column_widths', None)
        max_rows = data.get('max_rows', self.MAX_ROWS)
        
        # 빈 데이터 체크
        if not headers and not rows:
            return Emu(0)
        
        # 행 수 제한
        rows = rows[:max_rows]
        
        # 열 수 결정
        num_cols = len(headers) if headers else (len(rows[0]) if rows else 0)
        num_rows = (1 if headers else 0) + len(rows)
        
        if num_cols == 0 or num_rows == 0:
            return Emu(0)
        
        # 표 크기 계산
        table_width = context.content_width
        table_height = self._calculate_table_height(num_rows, headers)
        
        # 열 너비 계산
        if column_widths:
            col_widths = [Emu(int(table_width) * w) for w in column_widths]
        else:
            col_width = Emu(int(table_width) // num_cols)
            col_widths = [col_width] * num_cols
        
        # 표 생성
        left = context.get_content_start_x()
        table_shape = slide.shapes.add_table(
            num_rows, num_cols,
            left, top, table_width, table_height
        )
        table = table_shape.table
        
        # 열 너비 설정
        for i, width in enumerate(col_widths):
            table.columns[i].width = width
        
        # 헤더 행 채우기
        row_idx = 0
        if headers:
            self._fill_header_row(table, headers, context, style)
            row_idx = 1
        
        # 데이터 행 채우기
        for i, row_data in enumerate(rows):
            self._fill_data_row(table, row_idx, row_data, context, style, i)
            row_idx += 1
        
        return table_height
    
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산
        
        Args:
            context: 렌더링 컨텍스트
            data: 표 데이터
            
        Returns:
            필요한 높이 (EMU)
        """
        headers = data.get('headers', [])
        rows = data.get('rows', [])
        max_rows = data.get('max_rows', self.MAX_ROWS)
        
        rows = rows[:max_rows]
        num_rows = (1 if headers else 0) + len(rows)
        
        return self._calculate_table_height(num_rows, headers)
    
    def _calculate_table_height(self, num_rows: int, headers: List) -> Emu:
        """표 높이 계산
        
        Args:
            num_rows: 총 행 수
            headers: 헤더 리스트
            
        Returns:
            표 높이 (EMU)
        """
        if headers:
            header_height = int(self.HEADER_ROW_HEIGHT)
            data_height = int(self.DEFAULT_ROW_HEIGHT) * (num_rows - 1)
            return Emu(header_height + data_height)
        else:
            return Emu(int(self.DEFAULT_ROW_HEIGHT) * num_rows)
    
    def _fill_header_row(
        self,
        table: Table,
        headers: List[str],
        context: RenderContext,
        style: str
    ) -> None:
        """헤더 행 채우기
        
        Args:
            table: 표 객체
            headers: 헤더 리스트
            context: 렌더링 컨텍스트
            style: 표 스타일
        """
        for col_idx, header_text in enumerate(headers):
            cell = table.cell(0, col_idx)
            cell.text = str(header_text)
            
            # 텍스트 정렬 및 폰트
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.CENTER
            
            for run in para.runs:
                run.font.name = context.theme.fonts.body_font
                run.font.size = Pt(12)
                run.font.bold = True
                run.font.color.rgb = context.theme.colors.text_on_dark if style == 'header_highlight' else context.theme.colors.text_primary
            
            # 셀 배경색 (스타일별)
            if style == 'header_highlight':
                cell.fill.solid()
                cell.fill.fore_color.rgb = context.theme.colors.primary
            elif style == 'minimal':
                cell.fill.background()
            
            # 세로 정렬
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    
    def _fill_data_row(
        self,
        table: Table,
        row_idx: int,
        row_data: List,
        context: RenderContext,
        style: str,
        data_row_idx: int
    ) -> None:
        """데이터 행 채우기
        
        Args:
            table: 표 객체
            row_idx: 표에서의 행 인덱스
            row_data: 행 데이터 리스트
            context: 렌더링 컨텍스트
            style: 표 스타일
            data_row_idx: 데이터 행 인덱스 (0부터)
        """
        for col_idx, cell_data in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(cell_data)
            
            # 텍스트 정렬 및 폰트
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.CENTER
            
            for run in para.runs:
                run.font.name = context.theme.fonts.body_font
                run.font.size = Pt(11)
                run.font.color.rgb = context.theme.colors.text_primary
            
            # 교차 행 색상 (스타일별)
            if style == 'alternate_rows' and data_row_idx % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = context.theme.colors.accent3  # 연한 색상
            elif style != 'minimal':
                cell.fill.background()
            
            # 세로 정렬
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
