import sys
import os

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.json_to_ppt_generator import JsonToPptGenerator

def main():
    json_path = r"C:\Users\DKSYSTEMS\.gemini\antigravity\brain\587ba97a-c8e3-4e01-9079-0e4a4ec79963\ppt_content.json"
    template_path = r"D:\doc_gen\ppt-doc-automation\templates\pptx\group\그룹 공통 PPT템플릿.pptx"
    output_path = r"C:\Users\DKSYSTEMS\.gemini\antigravity\brain\587ba97a-c8e3-4e01-9079-0e4a4ec79963\smart_logistics_plan.pptx"

    print(f"Generating PPT from {json_path}")
    print(f"Using template: {template_path}")
    
    try:
        generator = JsonToPptGenerator(template_path=template_path)
        generated_file = generator.generate_from_file(json_path, output_path)
        print(f"Successfully generated PPT: {generated_file}")
    except Exception as e:
        print(f"Error generating PPT: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
