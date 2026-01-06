# -*- coding: utf-8 -*-
"""PPT 생성 스크립트"""
import os
import sys

# 현재 디렉토리를 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.json_to_ppt_generator import generate_ppt_from_json

json_path = r"D:\doc_gen\ppt-doc-automation\output\프로젝트_수행계획서_PPT_v2.json"
output_dir = r"D:\doc_gen\ppt-doc-automation\backend\output"

print(f"JSON 경로: {json_path}")
print(f"출력 디렉토리: {output_dir}")
print(f"JSON 파일 존재: {os.path.exists(json_path)}")

if os.path.exists(json_path):
    try:
        result = generate_ppt_from_json(json_path, output_dir)
        print(f"생성 완료: {result}")
    except Exception as e:
        print(f"오류 발생: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
else:
    print("JSON 파일을 찾을 수 없습니다.")
