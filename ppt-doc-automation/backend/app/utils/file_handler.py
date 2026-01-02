"""
파일 처리 유틸리티
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile

from app.config import settings


class FileHandler:
    """파일 처리 유틸리티 클래스"""
    
    @staticmethod
    def save_upload_file(
        upload_file: UploadFile,
        destination_dir: str,
        filename: Optional[str] = None,
    ) -> str:
        """
        업로드된 파일 저장
        
        Args:
            upload_file: FastAPI UploadFile 객체
            destination_dir: 저장할 디렉토리
            filename: 저장할 파일명 (옵션, 없으면 원본 파일명 사용)
            
        Returns:
            저장된 파일의 전체 경로
        """
        os.makedirs(destination_dir, exist_ok=True)
        
        if not filename:
            # 고유 ID 추가하여 파일명 생성
            ext = Path(upload_file.filename).suffix
            base_name = Path(upload_file.filename).stem
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{base_name}_{unique_id}{ext}"
        
        file_path = os.path.join(destination_dir, filename)
        
        with open(file_path, "wb") as f:
            shutil.copyfileobj(upload_file.file, f)
        
        return file_path
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        파일 삭제
        
        Args:
            file_path: 삭제할 파일 경로
            
        Returns:
            삭제 성공 여부
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """파일 확장자 추출"""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def is_allowed_extension(filename: str, allowed_extensions: List[str] = None) -> bool:
        """
        허용된 파일 확장자인지 확인
        
        Args:
            filename: 파일명
            allowed_extensions: 허용된 확장자 목록
            
        Returns:
            허용 여부
        """
        if allowed_extensions is None:
            allowed_extensions = settings.ALLOWED_EXTENSIONS
        
        ext = FileHandler.get_file_extension(filename)
        return ext in allowed_extensions
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """파일 크기 반환 (바이트)"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    @staticmethod
    def ensure_directory(directory: str) -> None:
        """디렉토리가 없으면 생성"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
        """
        디렉토리 내 파일 목록 반환
        
        Args:
            directory: 대상 디렉토리
            extension: 필터링할 확장자 (옵션)
            
        Returns:
            파일 경로 목록
        """
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if extension is None or file.endswith(extension):
                    files.append(file_path)
        
        return files
