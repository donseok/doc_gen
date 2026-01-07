"""
컴포넌트 기반 PPT 생성기 테스트

이 스크립트는 새로 구현된 컴포넌트 시스템을 검증합니다.
"""

import os
import sys

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.component_generator import ComponentBasedGenerator, generate_ppt_from_json


def test_basic_generation():
    """기본 PPT 생성 테스트"""
    
    # 테스트 JSON 데이터
    test_json = {
        "metadata": {
            "title": "스마트 물류관리 시스템 구축 프로젝트",
            "author": "김철수",
            "date": "2025-01-03"
        },
        "slides": [
            # 1. 표지 슬라이드
            {
                "slide_type": "title",
                "title": "스마트 물류관리 시스템 구축\n프로젝트 수행계획서",
                "subtitle": "(주)테크솔루션",
                "author": "김철수 PM",
                "date": "2025-01-03"
            },
            
            # 2. 목차 슬라이드
            {
                "slide_type": "toc",
                "title": "Contents",
                "items": [
                    {"number": "01", "title": "프로젝트 개요", "page_range": "03-05"},
                    {"number": "02", "title": "추진 전략 및 방법론", "page_range": "06-08"},
                    {"number": "03", "title": "프로젝트 조직 및 역할", "page_range": "09-11"},
                    {"number": "04", "title": "프로젝트 일정", "page_range": "12-14"},
                    {"number": "05", "title": "품질 및 보안 관리", "page_range": "15-17"},
                ]
            },
            
            # 3. 섹션 슬라이드
            {
                "slide_type": "section",
                "section_number": "01",
                "title": "프로젝트 개요",
                "subtitle": "Project Overview"
            },
            
            # 4. 본문 슬라이드 - 프로젝트 정보 (표)
            {
                "slide_type": "content",
                "main_title": "1. 프로젝트 개요",
                "action_title": "글로벌물류 차세대 스마트 물류관리 시스템 구축",
                "use_action_title": True,
                "visual_elements": [
                    {
                        "type": "table",
                        "data": {
                            "headers": ["항목", "내용"],
                            "rows": [
                                ["프로젝트명", "스마트 물류관리 시스템 구축"],
                                ["발주기관", "(주)글로벌물류"],
                                ["수행사", "(주)테크솔루션"],
                                ["계약금액", "15억원 (VAT 별도)"],
                                ["계약기간", "2025-01-06 ~ 2025-12-31 (12개월)"]
                            ],
                            "style": "header_highlight"
                        }
                    }
                ],
                "footer_text": "작성자_김철수"
            },
            
            # 5. 본문 슬라이드 - KPI (Big Numbers)
            {
                "slide_type": "content",
                "main_title": "1.2 프로젝트 배경 및 목적",
                "action_title": "물류 처리 효율 30% 향상, 재고 정확도 99.5% 달성 목표",
                "use_action_title": True,
                "visual_elements": [
                    {
                        "type": "big_numbers",
                        "data": {
                            "items": [
                                {"value": "500만", "label": "연간 물류 처리량", "suffix": "건"},
                                {"value": "30%", "label": "처리 효율 향상", "change": "+30%"},
                                {"value": "99.5%", "label": "재고 정확도", "change": "+15%"},
                                {"value": "20%", "label": "운영 비용 절감", "change": "-20%"}
                            ],
                            "columns": 4
                        }
                    }
                ],
                "footer_text": "작성자_김철수"
            },
            
            # 6. 섹션 슬라이드
            {
                "slide_type": "section",
                "section_number": "02",
                "title": "추진 전략 및 방법론",
                "subtitle": "Strategy & Methodology"
            },
            
            # 7. 본문 슬라이드 - 핵심 전략 (Feature Cards)
            {
                "slide_type": "content",
                "main_title": "2.1 추진 전략",
                "action_title": "안정적 전환과 혁신적 기능 구현의 균형",
                "use_action_title": True,
                "visual_elements": [
                    {
                        "type": "feature_cards",
                        "data": {
                            "items": [
                                {
                                    "number": "01",
                                    "title": "단계적 전환 전략",
                                    "description": "Big Bang 방식이 아닌 모듈별 순차 전환으로 리스크 최소화"
                                },
                                {
                                    "number": "02",
                                    "title": "애자일 기반 개발",
                                    "description": "2주 단위 스프린트로 빠른 피드백과 유연한 대응"
                                },
                                {
                                    "number": "03",
                                    "title": "현업 밀착 협업",
                                    "description": "주 2회 현업 리뷰를 통한 요구사항 정합성 확보"
                                }
                            ],
                            "columns": 3,
                            "style": "horizontal"
                        }
                    }
                ],
                "footer_text": "작성자_김철수"
            },
            
            # 8. 섹션 슬라이드
            {
                "slide_type": "section",
                "section_number": "04",
                "title": "프로젝트 일정",
                "subtitle": "Project Schedule"
            },
            
            # 9. 본문 슬라이드 - 타임라인
            {
                "slide_type": "content",
                "main_title": "4.1 마스터 일정",
                "action_title": "6단계 프로젝트 수행 로드맵",
                "use_action_title": True,
                "visual_elements": [
                    {
                        "type": "timeline",
                        "data": {
                            "steps": [
                                {"title": "착수", "period": "1월", "description": "킥오프, 환경구축"},
                                {"title": "분석", "period": "2-3월", "description": "요구사항 정의"},
                                {"title": "설계", "period": "4-5월", "description": "아키텍처 설계"},
                                {"title": "개발", "period": "6-9월", "description": "코딩, 테스트"},
                                {"title": "테스트", "period": "10-11월", "description": "통합/인수"},
                                {"title": "이행", "period": "12월", "description": "오픈, 안정화"}
                            ]
                        }
                    }
                ],
                "footer_text": "작성자_김철수"
            },
            
            # 10. 본문 슬라이드 - 마일스톤
            {
                "slide_type": "content",
                "main_title": "4.2 주요 마일스톤",
                "action_title": "6개 주요 마일스톤 및 산출물",
                "use_action_title": True,
                "visual_elements": [
                    {
                        "type": "milestones",
                        "data": {
                            "items": [
                                {"id": "M1", "title": "착수보고", "date": "2025-01-10", "deliverable": "수행계획서"},
                                {"id": "M2", "title": "요구사항 확정", "date": "2025-03-31", "deliverable": "요구사항정의서"},
                                {"id": "M3", "title": "설계 완료", "date": "2025-05-31", "deliverable": "설계서 일체"},
                                {"id": "M4", "title": "개발 완료", "date": "2025-09-30", "deliverable": "소스코드"},
                                {"id": "M5", "title": "테스트 완료", "date": "2025-11-15", "deliverable": "테스트결과서"},
                                {"id": "M6", "title": "시스템 오픈", "date": "2025-12-01", "deliverable": "오픈보고서"}
                            ],
                            "columns": 6
                        }
                    }
                ],
                "footer_text": "작성자_김철수"
            }
        ]
    }
    
    # 출력 경로
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'component_test_output.pptx')
    
    # PPT 생성
    print("=" * 60)
    print("컴포넌트 기반 PPT 생성기 테스트")
    print("=" * 60)
    print()
    
    try:
        generator = ComponentBasedGenerator(theme="dongkuk")
        prs = generator.generate(test_json)
        prs.save(output_path)
        
        print(f"✅ PPT 생성 성공!")
        print(f"   출력 파일: {output_path}")
        print(f"   슬라이드 수: {len(prs.slides)}")
        print()
        
        # 슬라이드 정보 출력
        print("생성된 슬라이드:")
        for i, slide in enumerate(prs.slides, 1):
            slide_type = test_json['slides'][i-1].get('slide_type', 'content')
            title = test_json['slides'][i-1].get('title', test_json['slides'][i-1].get('main_title', ''))
            print(f"   {i}. [{slide_type:8}] {title[:40]}...")
        
        print()
        print("=" * 60)
        print("테스트 완료!")
        print("=" * 60)
        
        return output_path
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_basic_generation()
