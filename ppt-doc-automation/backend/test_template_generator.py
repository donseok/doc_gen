"""
개선된 PPT 생성 테스트 스크립트

기존 방식과 새로운 템플릿 기반 방식을 비교 테스트합니다.
"""
import os
import sys
import json

# 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from app.services.template_slide_generator import TemplateSlideGenerator, create_presentation_from_json


# 경로 설정
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "templates", "pptx", "group", "그룹 공통 PPT템플릿.pptx")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# 테스트용 JSON 데이터 (프로젝트 수행계획서 기반)
TEST_JSON = {
    "presentation": {
        "title": "스마트 물류관리 시스템 구축 프로젝트 수행계획서",
        "author": "김철수",
        "date": "2025-01-03",
        "slides": [
            {
                "slide_number": 1,
                "layout_id": 1,
                "slide_type": "title",
                "placeholders": {
                    "title": "스마트 물류관리 시스템 구축\\n프로젝트 수행계획서",
                    "subtitle": "(주)테크솔루션 | 2025.01.03"
                }
            },
            {
                "slide_number": 2,
                "layout_id": 2,
                "slide_type": "toc",
                "placeholders": {
                    "toc_items": [
                        {"number": "01", "title": "프로젝트 개요", "pages": "03-05"},
                        {"number": "02", "title": "추진 전략 및 방법론", "pages": "06-08"},
                        {"number": "03", "title": "프로젝트 조직 및 역할", "pages": "09-10"},
                        {"number": "04", "title": "프로젝트 일정", "pages": "11-12"},
                        {"number": "05", "title": "품질 및 위험 관리", "pages": "13-15"}
                    ]
                }
            },
            {
                "slide_number": 3,
                "layout_id": 3,
                "slide_type": "content",
                "placeholders": {
                    "main_title": "1. 프로젝트 개요",
                    "action_title": "글로벌물류의 차세대 스마트 물류관리 시스템 구축을 통해 물류 처리 효율 30% 향상을 목표로 합니다.",
                    "body": [
                        {"level": 1, "text": "프로젝트명: 스마트 물류관리 시스템 구축"},
                        {"level": 2, "text": "발주기관: (주)글로벌물류"},
                        {"level": 2, "text": "수행사: (주)테크솔루션"},
                        {"level": 1, "text": "계약금액: 15억원 (VAT 별도)"},
                        {"level": 1, "text": "계약기간: 2025-01-06 ~ 2025-12-31 (총 12개월)"}
                    ]
                }
            },
            {
                "slide_number": 4,
                "layout_id": 4,
                "slide_type": "content",
                "placeholders": {
                    "main_title": "2. 시스템 범위",
                    "action_title": "WMS, TMS, OMS, Dashboard 4개 핵심 시스템을 클라우드 네이티브 아키텍처로 구축합니다."
                },
                "custom_elements": [
                    {
                        "type": "icon_card_grid",
                        "data": {
                            "columns": 4,
                            "items": [
                                {"title": "WMS", "subtitle": "창고관리시스템", "features": ["입출고 관리", "재고 관리", "피킹/패킹"], "accent_color": "#002452"},
                                {"title": "TMS", "subtitle": "배송관리시스템", "features": ["배차 관리", "경로 최적화", "실시간 추적"], "accent_color": "#C51F2A"},
                                {"title": "OMS", "subtitle": "주문관리시스템", "features": ["주문 접수", "할당 관리", "정산"], "accent_color": "#4B6580"},
                                {"title": "Dashboard", "subtitle": "통합모니터링", "features": ["실시간 현황", "KPI", "리포트"], "accent_color": "#E9B86E"}
                            ]
                        }
                    }
                ]
            },
            {
                "slide_number": 5,
                "layout_id": 3,
                "slide_type": "content",
                "placeholders": {
                    "main_title": "3. 기대 효과",
                    "action_title": "AI 기반 물류 최적화로 처리 효율 30% 향상, 재고 정확도 99.5% 달성, 운영 비용 20% 절감을 기대합니다.",
                    "body": [
                        {"level": 1, "text": "물류 처리 효율 30% 향상"},
                        {"level": 2, "text": "AI 기반 수요 예측 및 경로 최적화"},
                        {"level": 1, "text": "재고 정확도 99.5% 달성"},
                        {"level": 2, "text": "실시간 재고 추적 및 자동 보충"},
                        {"level": 1, "text": "운영 비용 20% 절감"},
                        {"level": 2, "text": "클라우드 기반 확장성 및 자동화"}
                    ]
                }
            }
        ]
    }
}


def main():
    print("=" * 60)
    print("PPT 생성 테스트 (템플릿 기반 방식)")
    print("=" * 60)
    
    # 템플릿 경로 확인
    template_path = os.path.abspath(TEMPLATE_PATH)
    print(f"\n템플릿 경로: {template_path}")
    print(f"템플릿 존재: {os.path.exists(template_path)}")
    
    if not os.path.exists(template_path):
        print("[ERROR] 템플릿 파일을 찾을 수 없습니다!")
        return
    
    # 출력 디렉토리 확인
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # 템플릿 기반 생성
        print("\n[1] 템플릿 기반 PPT 생성 중...")
        prs = create_presentation_from_json(template_path, TEST_JSON)
        
        # 저장
        output_path = os.path.join(OUTPUT_DIR, "테스트_템플릿기반_생성.pptx")
        prs.save(output_path)
        print(f"[SUCCESS] 생성 완료: {output_path}")
        print(f"  - 슬라이드 수: {len(prs.slides)}")
        
        # 레이아웃 정보 출력
        print("\n[2] 슬라이드별 레이아웃 정보:")
        for i, slide in enumerate(prs.slides):
            print(f"  슬라이드 {i+1}: {slide.slide_layout.name}")
        
        print("\n" + "=" * 60)
        print("테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] 생성 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
