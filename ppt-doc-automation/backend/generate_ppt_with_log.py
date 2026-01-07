import sys
import os
import traceback

# Redirect stdout and stderr to log file
log_file = open("generation_log.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

print("Starting generation script...")

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(f"Added {os.path.dirname(os.path.abspath(__file__))} to sys.path")

try:
    import pptx
    print(f"python-pptx version: {pptx.__version__}")
except ImportError:
    print("Error: python-pptx not installed")
    sys.exit(1)

try:
    from app.services.json_to_ppt_generator import JsonToPptGenerator
    print("Imported JsonToPptGenerator")
except ImportError as e:
    print(f"Error importing JsonToPptGenerator: {e}")
    sys.exit(1)

def main():
    json_path = r"C:\Users\DKSYSTEMS\.gemini\antigravity\brain\587ba97a-c8e3-4e01-9079-0e4a4ec79963\ppt_content.json"
    template_path = r"D:\doc_gen\ppt-doc-automation\templates\pptx\group\그룹 공통 PPT템플릿.pptx"
    output_path = r"C:\Users\DKSYSTEMS\.gemini\antigravity\brain\587ba97a-c8e3-4e01-9079-0e4a4ec79963\smart_logistics_plan.pptx"

    print(f"Generating PPT from {json_path}")
    print(f"Using template: {template_path}")
    
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return

    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return

    try:
        generator = JsonToPptGenerator(template_path=template_path)
        generated_file = generator.generate_from_file(json_path, output_path)
        print(f"Successfully generated PPT: {generated_file}")
    except Exception as e:
        print(f"Error generating PPT: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    log_file.close()
