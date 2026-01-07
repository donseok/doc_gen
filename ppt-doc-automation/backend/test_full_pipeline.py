"""
마크다운 → PPT 전체 파이프라인 테스트

프로젝트_수행계획서.md를 읽어서 JSON으로 변환하고 PPT를 생성합니다.
"""

import os
import sys
import json

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.markdown_to_json import convert_markdown_to_json, convert_file
from app.services.component_generator import ComponentBasedGenerator


def test_full_pipeline():
    """전체 파이프라인 테스트"""
    
    print("=" * 70)
    print("마크다운 → JSON → PPT 전체 파이프라인 테스트")
    print("=" * 70)
    print()
    
    # 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(os.path.dirname(base_dir), 'docs')
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 입력 파일
    md_path = os.path.join(docs_dir, '프로젝트_수행계획서.md')
    json_path = os.path.join(output_dir, '프로젝트_수행계획서.json')
    pptx_path = os.path.join(output_dir, '프로젝트_수행계획서_자동생성.pptx')
    
    print(f"📄 입력 마크다운: {md_path}")
    print()
    
    # 1단계: 마크다운 → JSON
    print("-" * 70)
    print("1단계: 마크다운 → JSON 변환")
    print("-" * 70)
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        json_data = convert_markdown_to_json(md_content)
        
        # JSON 저장
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 변환 완료!")
        print(f"   출력 파일: {json_path}")
        print(f"   슬라이드 수: {len(json_data.get('slides', []))}")
        print()
        
        # 슬라이드 요약 출력
        print("   생성된 슬라이드:")
        for i, slide in enumerate(json_data.get('slides', [])[:10], 1):
            slide_type = slide.get('slide_type', 'unknown')
            title = slide.get('title', slide.get('main_title', ''))[:35]
            print(f"   {i:2d}. [{slide_type:8}] {title}...")
        
        if len(json_data.get('slides', [])) > 10:
            print(f"   ... 외 {len(json_data['slides']) - 10}개")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {md_path}")
        return None
    except Exception as e:
        print(f"❌ JSON 변환 오류: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print()
    
    # 2단계: JSON → PPT
    print("-" * 70)
    print("2단계: JSON → PPT 생성")
    print("-" * 70)
    
    try:
        generator = ComponentBasedGenerator(theme="dongkuk")
        prs = generator.generate(json_data)
        prs.save(pptx_path)
        
        print(f"✅ PPT 생성 완료!")
        print(f"   출력 파일: {pptx_path}")
        print(f"   슬라이드 수: {len(prs.slides)}")
        
    except Exception as e:
        print(f"❌ PPT 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print()
    print("=" * 70)
    print("✅ 전체 파이프라인 테스트 완료!")
    print("=" * 70)
    print()
    print("생성된 파일:")
    print(f"  - JSON: {json_path}")
    print(f"  - PPTX: {pptx_path}")
    
    return {
        "json_path": json_path,
        "pptx_path": pptx_path,
        "slide_count": len(prs.slides)
    }


def test_json_only():
    """JSON 변환만 테스트"""
    print("=" * 70)
    print("마크다운 → JSON 변환 테스트")
    print("=" * 70)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(os.path.dirname(base_dir), 'docs')
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    md_path = os.path.join(docs_dir, '프로젝트_수행계획서.md')
    json_path = os.path.join(output_dir, '프로젝트_수행계획서.json')
    
    try:
        json_data = convert_file(md_path, json_path)
        
        print(f"✅ 변환 완료!")
        print(f"   슬라이드 수: {len(json_data.get('slides', []))}")
        print()
        
        # 메타데이터 출력
        print("메타데이터:")
        for key, value in json_data.get('metadata', {}).items():
            print(f"  {key}: {value}")
        print()
        
        # 슬라이드 요약
        print("슬라이드:")
        for i, slide in enumerate(json_data.get('slides', []), 1):
            slide_type = slide.get('slide_type', 'unknown')
            title = slide.get('title', slide.get('main_title', ''))[:40]
            elements = len(slide.get('visual_elements', []))
            body = len(slide.get('body', []))
            
            info = []
            if elements > 0:
                info.append(f"요소:{elements}")
            if body > 0:
                info.append(f"불릿:{body}")
            
            info_str = f" ({', '.join(info)})" if info else ""
            print(f"  {i:2d}. [{slide_type:8}] {title}...{info_str}")
        
        return json_data
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--json-only':
        test_json_only()
    else:
        test_full_pipeline()
