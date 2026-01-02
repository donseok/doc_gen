"""
애플리케이션 설정

개선 사항 (제미나이 분석서 반영):
- 스토리지 확장성을 위한 설정 추가 (로컬/S3)
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    APP_NAME: str = "PPT 문서 자동화 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./data/ppt_automation.db"

    # 디렉토리 설정
    TEMPLATES_DIR: str = "./templates"
    SAMPLES_DIR: str = "./samples"
    OUTPUT_DIR: str = "./output"

    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # 파일 업로드 설정
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".md", ".pptx"]

    # 스토리지 설정 (제미나이 분석서 개선 사항 반영)
    STORAGE_TYPE: str = "local"  # 'local' 또는 's3'

    # S3 설정 (STORAGE_TYPE이 's3'일 때 사용)
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: str = "ap-northeast-2"
    S3_ENDPOINT_URL: Optional[str] = None  # MinIO 등 S3 호환 스토리지용
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # 마크다운 파서 설정
    USE_LEGACY_PARSER: bool = False  # True면 정규식 기반 레거시 파서 사용

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 필요한 디렉토리 생성
os.makedirs(settings.TEMPLATES_DIR, exist_ok=True)
os.makedirs(settings.SAMPLES_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

# 데이터베이스 디렉토리 생성
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
db_dir = os.path.dirname(db_path)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

