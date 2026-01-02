import traceback
try:
    from app.main import app
    print("App loaded successfully!")
except Exception as e:
    traceback.print_exc()
