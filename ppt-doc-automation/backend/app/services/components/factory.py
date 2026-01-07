"""
컴포넌트 팩토리

슬라이드 및 시각 요소 컴포넌트를 생성하는 팩토리 클래스들을 정의합니다.
Factory Pattern을 사용하여 컴포넌트 생성을 캡슐화합니다.
"""

from typing import Dict, Type, Optional, Any
from .base import BaseComponent, BaseSlideComponent


class SlideComponentFactory:
    """슬라이드 컴포넌트 팩토리
    
    슬라이드 타입에 따라 적절한 슬라이드 컴포넌트를 생성합니다.
    
    Usage:
        factory = SlideComponentFactory()
        component = factory.create('title')
        component.render(slide, context, data)
    """
    
    _registry: Dict[str, Type[BaseSlideComponent]] = {}
    
    @classmethod
    def register(cls, slide_type: str, component_class: Type[BaseSlideComponent]) -> None:
        """컴포넌트 등록
        
        Args:
            slide_type: 슬라이드 타입 식별자
            component_class: 컴포넌트 클래스
        """
        cls._registry[slide_type] = component_class
    
    @classmethod
    def create(cls, slide_type: str, **kwargs) -> BaseSlideComponent:
        """슬라이드 컴포넌트 생성
        
        Args:
            slide_type: 슬라이드 타입 (title, toc, content, section 등)
            **kwargs: 컴포넌트 생성자에 전달할 인자
            
        Returns:
            생성된 슬라이드 컴포넌트 인스턴스
            
        Raises:
            ValueError: 등록되지 않은 슬라이드 타입인 경우
        """
        if slide_type not in cls._registry:
            # 기본적으로 content 타입 사용
            if 'content' in cls._registry:
                return cls._registry['content'](**kwargs)
            raise ValueError(f"Unknown slide type: {slide_type}. Available: {list(cls._registry.keys())}")
        
        return cls._registry[slide_type](**kwargs)
    
    @classmethod
    def list_types(cls) -> list:
        """등록된 슬라이드 타입 목록 반환"""
        return list(cls._registry.keys())


class VisualComponentFactory:
    """시각 요소 컴포넌트 팩토리
    
    시각 요소 타입에 따라 적절한 컴포넌트를 생성합니다.
    
    지원 타입:
        - table: 표 컴포넌트
        - big_numbers: 대형 숫자 카드
        - icon_cards: 아이콘 카드 그리드
        - feature_cards: 기능 카드
        - pain_cards: 문제점 카드
        - process_flow: 프로세스 플로우
        - timeline: 타임라인
        - gantt: 간트 차트
        - milestones: 마일스톤
        - chart: 차트 (바, 도넛 등)
        - org_chart: 조직도
        - tech_stack: 기술 스택
        - two_column_list: 2열 리스트
        - checklist: 체크리스트
        - risk_cards: 위험 카드
        
    Usage:
        factory = VisualComponentFactory()
        component = factory.create('table')
        height = component.render(slide, context, data, top)
    """
    
    _registry: Dict[str, Type[BaseComponent]] = {}
    
    @classmethod
    def register(cls, element_type: str, component_class: Type[BaseComponent]) -> None:
        """컴포넌트 등록
        
        Args:
            element_type: 시각 요소 타입 식별자
            component_class: 컴포넌트 클래스
        """
        cls._registry[element_type] = component_class
    
    @classmethod
    def create(cls, element_type: str, **kwargs) -> BaseComponent:
        """시각 요소 컴포넌트 생성
        
        Args:
            element_type: 시각 요소 타입
            **kwargs: 컴포넌트 생성자에 전달할 인자
            
        Returns:
            생성된 컴포넌트 인스턴스
            
        Raises:
            ValueError: 등록되지 않은 시각 요소 타입인 경우
        """
        if element_type not in cls._registry:
            raise ValueError(f"Unknown visual element type: {element_type}. Available: {list(cls._registry.keys())}")
        
        return cls._registry[element_type](**kwargs)
    
    @classmethod
    def list_types(cls) -> list:
        """등록된 시각 요소 타입 목록 반환"""
        return list(cls._registry.keys())
    
    @classmethod
    def has_type(cls, element_type: str) -> bool:
        """특정 타입이 등록되어 있는지 확인"""
        return element_type in cls._registry


class LayoutComponentFactory:
    """레이아웃 컴포넌트 팩토리
    
    레이아웃 타입에 따라 적절한 레이아웃 컴포넌트를 생성합니다.
    
    지원 타입:
        - two_column: 2열 레이아웃
        - grid: 그리드 레이아웃
        - stack: 수직 스택 레이아웃
    """
    
    _registry: Dict[str, Type[BaseComponent]] = {}
    
    @classmethod
    def register(cls, layout_type: str, component_class: Type[BaseComponent]) -> None:
        """컴포넌트 등록"""
        cls._registry[layout_type] = component_class
    
    @classmethod
    def create(cls, layout_type: str, **kwargs) -> BaseComponent:
        """레이아웃 컴포넌트 생성"""
        if layout_type not in cls._registry:
            raise ValueError(f"Unknown layout type: {layout_type}. Available: {list(cls._registry.keys())}")
        
        return cls._registry[layout_type](**kwargs)
    
    @classmethod
    def list_types(cls) -> list:
        """등록된 레이아웃 타입 목록 반환"""
        return list(cls._registry.keys())


def register_component(component_type: str, category: str = "visual"):
    """컴포넌트 등록 데코레이터
    
    컴포넌트 클래스를 적절한 팩토리에 자동 등록합니다.
    
    Args:
        component_type: 컴포넌트 타입 식별자
        category: 카테고리 (slide, visual, layout)
        
    Usage:
        @register_component('table', category='visual')
        class TableComponent(BaseComponent):
            ...
    """
    factory_map = {
        'slide': SlideComponentFactory,
        'visual': VisualComponentFactory,
        'layout': LayoutComponentFactory,
    }
    
    def decorator(cls):
        factory = factory_map.get(category)
        if factory:
            factory.register(component_type, cls)
        return cls
    
    return decorator
