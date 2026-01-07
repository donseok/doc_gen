"""
타임라인 컴포넌트

PPT 슬라이드에 타임라인, 간트 차트, 마일스톤을 생성합니다.

컴포넌트:
    - TimelineComponent: 가로 타임라인
    - GanttComponent: 간트 차트
    - MilestoneComponent: 마일스톤 카드
"""

from typing import Dict, Any, List, Optional
from pptx.slide import Slide
from pptx.util import Emu, Pt, Cm, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from ..base import BaseComponent, RenderContext
from ..factory import register_component


@register_component('timeline', category='visual')
class TimelineComponent(BaseComponent):
    """가로 타임라인 컴포넌트
    
    단계별 프로세스를 가로 타임라인으로 표시합니다.
    
    Data Schema:
        {
            "steps": [
                {
                    "title": "착수",
                    "period": "1월",
                    "description": "킥오프, 환경구축"
                },
                ...
            ]
        }
    """
    
    TIMELINE_HEIGHT = Emu(Cm(3.5))
    STEP_MARGIN = Emu(Cm(0.2))
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """타임라인 렌더링"""
        steps = data.get('steps', [])
        
        if not steps:
            return Emu(0)
        
        num_steps = len(steps)
        total_margin = int(self.STEP_MARGIN) * (num_steps - 1)
        step_width = Emu((int(context.content_width) - total_margin) // num_steps)
        
        left_start = context.get_content_start_x()
        line_y = Emu(int(top) + Emu(Cm(1.5)))
        
        # 연결 라인 (메인 라인)
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left_start,
            line_y,
            context.content_width,
            Emu(Pt(3))
        )
        line.fill.solid()
        line.fill.fore_color.rgb = context.theme.colors.primary
        line.line.fill.background()
        
        for i, step in enumerate(steps):
            step_left = Emu(int(left_start) + i * (int(step_width) + int(self.STEP_MARGIN)))
            self._render_step(slide, context, step, step_left, top, step_width, i + 1)
        
        return self.TIMELINE_HEIGHT
    
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산"""
        return self.TIMELINE_HEIGHT
    
    def _render_step(
        self,
        slide: Slide,
        context: RenderContext,
        step: Dict[str, Any],
        left: Emu,
        top: Emu,
        width: Emu,
        step_number: int
    ) -> None:
        """단일 단계 렌더링"""
        # 원형 마커
        marker_size = Emu(Cm(0.8))
        marker_x = Emu(int(left) + int(width) // 2 - int(marker_size) // 2)
        marker_y = Emu(int(top) + Emu(Cm(1.2)))
        
        marker = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            marker_x, marker_y, marker_size, marker_size
        )
        marker.fill.solid()
        marker.fill.fore_color.rgb = context.theme.colors.accent
        marker.line.fill.background()
        
        # 제목
        title = step.get('title', '')
        title_top = Emu(int(top) + Emu(Cm(0.2)))
        title_height = Emu(Cm(0.8))
        
        title_shape = slide.shapes.add_textbox(left, title_top, width, title_height)
        tf = title_shape.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.CENTER
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.body_font
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = context.theme.colors.primary
        
        # 기간
        period = step.get('period', '')
        if period:
            period_top = Emu(int(top) + Emu(Cm(2.1)))
            period_height = Emu(Cm(0.6))
            
            period_shape = slide.shapes.add_textbox(left, period_top, width, period_height)
            tf = period_shape.text_frame
            p = tf.paragraphs[0]
            p.text = period
            p.alignment = PP_ALIGN.CENTER
            
            run = p.runs[0] if p.runs else p.add_run()
            run.font.name = context.theme.fonts.caption_font
            run.font.size = Pt(9)
            run.font.color.rgb = context.theme.colors.text_secondary
        
        # 설명
        description = step.get('description', '')
        if description:
            desc_top = Emu(int(top) + Emu(Cm(2.7)))
            desc_height = Emu(Cm(0.8))
            
            desc_shape = slide.shapes.add_textbox(left, desc_top, width, desc_height)
            tf = desc_shape.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = description
            p.alignment = PP_ALIGN.CENTER
            
            run = p.runs[0] if p.runs else p.add_run()
            run.font.name = context.theme.fonts.caption_font
            run.font.size = Pt(8)
            run.font.color.rgb = context.theme.colors.text_secondary


@register_component('gantt', category='visual')
class GanttComponent(BaseComponent):
    """간트 차트 컴포넌트
    
    프로젝트 일정을 간트 차트 형태로 표시합니다.
    
    Data Schema:
        {
            "phases": [
                {
                    "name": "착수",
                    "start": "2025-01",
                    "end": "2025-01",
                    "color": "#C51F2A"  # 선택적
                },
                ...
            ],
            "months": ["1월", "2월", "3월", ...]  # 선택적
        }
    """
    
    CHART_HEIGHT = Emu(Cm(4))
    ROW_HEIGHT = Emu(Cm(0.6))
    HEADER_HEIGHT = Emu(Cm(0.8))
    LABEL_WIDTH = Emu(Cm(3))
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """간트 차트 렌더링"""
        phases = data.get('phases', [])
        months = data.get('months', ['1월', '2월', '3월', '4월', '5월', '6월', 
                                      '7월', '8월', '9월', '10월', '11월', '12월'])
        
        if not phases:
            return Emu(0)
        
        left_start = context.get_content_start_x()
        chart_width = Emu(int(context.content_width) - int(self.LABEL_WIDTH))
        month_width = Emu(int(chart_width) // len(months))
        
        # 헤더 (월 표시)
        self._render_header(slide, context, months, left_start, top, month_width)
        
        # 각 단계 바
        current_top = Emu(int(top) + int(self.HEADER_HEIGHT))
        for i, phase in enumerate(phases):
            self._render_phase_bar(slide, context, phase, left_start, current_top, 
                                   month_width, months, i)
            current_top = Emu(int(current_top) + int(self.ROW_HEIGHT))
        
        total_height = Emu(int(self.HEADER_HEIGHT) + len(phases) * int(self.ROW_HEIGHT))
        return total_height
    
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산"""
        phases = data.get('phases', [])
        return Emu(int(self.HEADER_HEIGHT) + len(phases) * int(self.ROW_HEIGHT))
    
    def _render_header(
        self,
        slide: Slide,
        context: RenderContext,
        months: List[str],
        left_start: Emu,
        top: Emu,
        month_width: Emu
    ) -> None:
        """헤더 (월) 렌더링"""
        chart_left = Emu(int(left_start) + int(self.LABEL_WIDTH))
        
        for i, month in enumerate(months):
            month_left = Emu(int(chart_left) + i * int(month_width))
            
            shape = slide.shapes.add_textbox(month_left, top, month_width, self.HEADER_HEIGHT)
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.text = month
            p.alignment = PP_ALIGN.CENTER
            
            run = p.runs[0] if p.runs else p.add_run()
            run.font.name = context.theme.fonts.caption_font
            run.font.size = Pt(8)
            run.font.color.rgb = context.theme.colors.text_secondary
    
    def _render_phase_bar(
        self,
        slide: Slide,
        context: RenderContext,
        phase: Dict[str, Any],
        left_start: Emu,
        top: Emu,
        month_width: Emu,
        months: List[str],
        phase_idx: int
    ) -> None:
        """단계 바 렌더링"""
        # 라벨
        label = phase.get('name', '')
        label_shape = slide.shapes.add_textbox(left_start, top, self.LABEL_WIDTH, self.ROW_HEIGHT)
        tf = label_shape.text_frame
        p = tf.paragraphs[0]
        p.text = label
        p.alignment = PP_ALIGN.LEFT
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.body_font
        run.font.size = Pt(9)
        run.font.color.rgb = context.theme.colors.text_primary
        
        # 바 (간소화된 버전 - 전체 기간 표시)
        chart_left = Emu(int(left_start) + int(self.LABEL_WIDTH))
        
        # start/end 파싱 (간소화: 인덱스로 처리)
        start_idx = phase.get('start_month', phase_idx * 2) % len(months)
        end_idx = phase.get('end_month', start_idx + 2) % len(months)
        if end_idx < start_idx:
            end_idx = len(months) - 1
        
        bar_left = Emu(int(chart_left) + start_idx * int(month_width))
        bar_width = Emu((end_idx - start_idx + 1) * int(month_width))
        bar_height = Emu(int(self.ROW_HEIGHT) * 7 // 10)
        bar_top = Emu(int(top) + (int(self.ROW_HEIGHT) - int(bar_height)) // 2)
        
        # 색상 결정
        colors = [
            context.theme.colors.accent,
            context.theme.colors.primary,
            context.theme.colors.accent2,
            context.theme.colors.accent5,
            context.theme.colors.accent6,
        ]
        bar_color = colors[phase_idx % len(colors)]
        
        bar = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            bar_left, bar_top, bar_width, bar_height
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = bar_color
        bar.line.fill.background()


@register_component('milestones', category='visual')
class MilestoneComponent(BaseComponent):
    """마일스톤 컴포넌트
    
    프로젝트 마일스톤을 카드 형태로 표시합니다.
    
    Data Schema:
        {
            "items": [
                {
                    "id": "M1",
                    "title": "착수보고",
                    "date": "2025-01-10",
                    "deliverable": "수행계획서"
                },
                ...
            ],
            "columns": 3
        }
    """
    
    CARD_HEIGHT = Emu(Cm(2.8))
    CARD_MARGIN = Emu(Cm(0.3))
    
    def render(
        self, 
        slide: Slide, 
        context: RenderContext, 
        data: Dict[str, Any],
        top: Emu,
        **kwargs
    ) -> Emu:
        """마일스톤 렌더링"""
        items = data.get('items', [])
        columns = data.get('columns', min(len(items), 6))
        
        if not items:
            return Emu(0)
        
        total_margin = int(self.CARD_MARGIN) * (columns - 1)
        card_width = Emu((int(context.content_width) - total_margin) // columns)
        left_start = context.get_content_start_x()
        
        for i, item in enumerate(items):
            col = i % columns
            row = i // columns
            
            card_left = Emu(int(left_start) + col * (int(card_width) + int(self.CARD_MARGIN)))
            card_top = Emu(int(top) + row * (int(self.CARD_HEIGHT) + int(self.CARD_MARGIN)))
            
            self._render_milestone_card(slide, context, item, card_left, card_top, card_width)
        
        num_rows = (len(items) + columns - 1) // columns
        return Emu(num_rows * (int(self.CARD_HEIGHT) + int(self.CARD_MARGIN)))
    
    def get_required_height(
        self, 
        context: RenderContext, 
        data: Dict[str, Any],
        **kwargs
    ) -> Emu:
        """필요한 높이 계산"""
        items = data.get('items', [])
        columns = data.get('columns', min(len(items), 6))
        
        if not items:
            return Emu(0)
        
        num_rows = (len(items) + columns - 1) // columns
        return Emu(num_rows * (int(self.CARD_HEIGHT) + int(self.CARD_MARGIN)))
    
    def _render_milestone_card(
        self,
        slide: Slide,
        context: RenderContext,
        item: Dict[str, Any],
        left: Emu,
        top: Emu,
        width: Emu
    ) -> None:
        """단일 마일스톤 카드 렌더링"""
        # 카드 배경
        card_bg = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            left, top, width, self.CARD_HEIGHT
        )
        card_bg.fill.solid()
        card_bg.fill.fore_color.rgb = context.theme.colors.background
        card_bg.line.color.rgb = context.theme.colors.primary
        card_bg.line.width = Pt(1.5)
        
        # ID (상단)
        milestone_id = item.get('id', '')
        id_top = Emu(int(top) + Emu(Cm(0.2)))
        id_height = Emu(Cm(0.6))
        
        id_shape = slide.shapes.add_textbox(left, id_top, width, id_height)
        tf = id_shape.text_frame
        p = tf.paragraphs[0]
        p.text = milestone_id
        p.alignment = PP_ALIGN.CENTER
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.title_font
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = context.theme.colors.accent
        
        # 제목
        title = item.get('title', '')
        title_top = Emu(int(top) + Emu(Cm(0.8)))
        title_height = Emu(Cm(0.6))
        
        title_shape = slide.shapes.add_textbox(left, title_top, width, title_height)
        tf = title_shape.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.CENTER
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.body_font
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = context.theme.colors.primary
        
        # 날짜
        date = item.get('date', '')
        date_top = Emu(int(top) + Emu(Cm(1.5)))
        date_height = Emu(Cm(0.5))
        
        date_shape = slide.shapes.add_textbox(left, date_top, width, date_height)
        tf = date_shape.text_frame
        p = tf.paragraphs[0]
        p.text = date
        p.alignment = PP_ALIGN.CENTER
        
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = context.theme.fonts.caption_font
        run.font.size = Pt(9)
        run.font.color.rgb = context.theme.colors.text_secondary
        
        # 산출물
        deliverable = item.get('deliverable', '')
        if deliverable:
            del_top = Emu(int(top) + Emu(Cm(2)))
            del_height = Emu(Cm(0.6))
            
            del_shape = slide.shapes.add_textbox(left, del_top, width, del_height)
            tf = del_shape.text_frame
            p = tf.paragraphs[0]
            p.text = f"산출물: {deliverable}"
            p.alignment = PP_ALIGN.CENTER
            
            run = p.runs[0] if p.runs else p.add_run()
            run.font.name = context.theme.fonts.caption_font
            run.font.size = Pt(8)
            run.font.color.rgb = context.theme.colors.text_secondary
