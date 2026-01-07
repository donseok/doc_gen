import sys
print("Python executable:", sys.executable)
try:
    import pptx
    print("python-pptx is installed. Version:", pptx.__version__)
except ImportError:
    print("python-pptx is NOT installed.")
except Exception as e:
    print(f"Error importing pptx: {e}")
