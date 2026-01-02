"""
스토리지 서비스 추상화

개선 사항 (제미나이 분석서 반영):
- 로컬 저장 방식에서 클라우드(S3 등) 저장 방식으로 전환 가능한 인터페이스 추상화
- 스토리지 백엔드 교체 시 코드 변경 최소화
- 확장 가능한 플러그인 구조
"""
import os
import shutil
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.config import settings


@dataclass
class StorageFile:
    """저장된 파일 메타데이터"""
    key: str  # 고유 식별자 (로컬: 상대경로, S3: 오브젝트 키)
    filename: str  # 원본 파일명
    size: int  # 파일 크기 (bytes)
    content_type: str  # MIME 타입
    created_at: datetime
    url: Optional[str] = None  # 다운로드 URL (해당되는 경우)


class StorageBackend(ABC):
    """
    스토리지 백엔드 추상 인터페이스

    모든 스토리지 구현체는 이 인터페이스를 상속받아야 함
    """

    @abstractmethod
    def save(self, file_data: BinaryIO, key: str, content_type: str = "application/octet-stream") -> StorageFile:
        """
        파일 저장

        Args:
            file_data: 파일 바이너리 데이터
            key: 저장할 키/경로
            content_type: MIME 타입

        Returns:
            저장된 파일 메타데이터
        """
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[BinaryIO]:
        """
        파일 조회

        Args:
            key: 파일 키/경로

        Returns:
            파일 바이너리 스트림 또는 None
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        파일 삭제

        Args:
            key: 파일 키/경로

        Returns:
            삭제 성공 여부
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        파일 존재 여부 확인

        Args:
            key: 파일 키/경로

        Returns:
            존재 여부
        """
        pass

    @abstractmethod
    def get_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        파일 다운로드 URL 생성

        Args:
            key: 파일 키/경로
            expires_in: URL 만료 시간 (초)

        Returns:
            다운로드 URL 또는 None
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[StorageFile]:
        """
        파일 목록 조회

        Args:
            prefix: 키 접두사 필터

        Returns:
            파일 메타데이터 목록
        """
        pass


class LocalStorage(StorageBackend):
    """
    로컬 파일 시스템 스토리지 구현

    기본 스토리지 백엔드로, 로컬 디스크에 파일을 저장
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Args:
            base_path: 기본 저장 디렉토리 (기본값: settings.OUTPUT_DIR)
        """
        self.base_path = Path(base_path or settings.OUTPUT_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, key: str) -> Path:
        """키에서 전체 경로 생성"""
        return self.base_path / key

    def save(self, file_data: BinaryIO, key: str, content_type: str = "application/octet-stream") -> StorageFile:
        """파일을 로컬 디스크에 저장"""
        full_path = self._get_full_path(key)

        # 상위 디렉토리 생성
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 저장
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)

        # 파일 정보 반환
        stat = full_path.stat()
        return StorageFile(
            key=key,
            filename=full_path.name,
            size=stat.st_size,
            content_type=content_type,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            url=str(full_path),
        )

    def get(self, key: str) -> Optional[BinaryIO]:
        """로컬 디스크에서 파일 조회"""
        full_path = self._get_full_path(key)

        if not full_path.exists():
            return None

        return open(full_path, 'rb')

    def delete(self, key: str) -> bool:
        """로컬 디스크에서 파일 삭제"""
        full_path = self._get_full_path(key)

        if not full_path.exists():
            return False

        full_path.unlink()
        return True

    def exists(self, key: str) -> bool:
        """파일 존재 여부 확인"""
        return self._get_full_path(key).exists()

    def get_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        로컬 파일 경로 반환

        참고: 로컬 스토리지에서는 만료 시간이 적용되지 않음
        """
        full_path = self._get_full_path(key)

        if not full_path.exists():
            return None

        return str(full_path)

    def list_files(self, prefix: str = "") -> List[StorageFile]:
        """디렉토리 내 파일 목록 조회"""
        search_path = self.base_path / prefix if prefix else self.base_path
        files = []

        if not search_path.exists():
            return files

        for path in search_path.rglob('*'):
            if path.is_file():
                stat = path.stat()
                relative_key = str(path.relative_to(self.base_path))
                files.append(StorageFile(
                    key=relative_key,
                    filename=path.name,
                    size=stat.st_size,
                    content_type=self._guess_content_type(path.suffix),
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    url=str(path),
                ))

        return files

    def _guess_content_type(self, suffix: str) -> str:
        """파일 확장자로 MIME 타입 추측"""
        content_types = {
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.pdf': 'application/pdf',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }
        return content_types.get(suffix.lower(), 'application/octet-stream')


class S3Storage(StorageBackend):
    """
    AWS S3 스토리지 구현

    클라우드 환경에서 사용할 수 있는 S3 호환 스토리지 백엔드
    """

    def __init__(
        self,
        bucket_name: str,
        region: str = "ap-northeast-2",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        """
        Args:
            bucket_name: S3 버킷 이름
            region: AWS 리전
            access_key: AWS 액세스 키 (환경변수 사용 가능)
            secret_key: AWS 시크릿 키 (환경변수 사용 가능)
            endpoint_url: 커스텀 엔드포인트 (MinIO 등 S3 호환 스토리지용)
        """
        self.bucket_name = bucket_name
        self.region = region
        self.endpoint_url = endpoint_url

        # boto3 임포트 (선택적 의존성)
        try:
            import boto3
            from botocore.config import Config

            config = Config(
                region_name=region,
                signature_version='s3v4',
            )

            session_kwargs = {}
            if access_key and secret_key:
                session_kwargs['aws_access_key_id'] = access_key
                session_kwargs['aws_secret_access_key'] = secret_key

            client_kwargs = {'config': config}
            if endpoint_url:
                client_kwargs['endpoint_url'] = endpoint_url

            self.s3 = boto3.client('s3', **session_kwargs, **client_kwargs)
            self._available = True

        except ImportError:
            self._available = False
            self.s3 = None

    def _check_available(self):
        """S3 클라이언트 사용 가능 여부 확인"""
        if not self._available:
            raise RuntimeError("boto3 라이브러리가 설치되지 않았습니다. pip install boto3")

    def save(self, file_data: BinaryIO, key: str, content_type: str = "application/octet-stream") -> StorageFile:
        """S3에 파일 업로드"""
        self._check_available()

        # 파일 크기 확인
        file_data.seek(0, 2)  # 끝으로 이동
        size = file_data.tell()
        file_data.seek(0)  # 처음으로 복귀

        # S3 업로드
        self.s3.upload_fileobj(
            file_data,
            self.bucket_name,
            key,
            ExtraArgs={'ContentType': content_type}
        )

        return StorageFile(
            key=key,
            filename=key.split('/')[-1],
            size=size,
            content_type=content_type,
            created_at=datetime.now(),
            url=self.get_url(key),
        )

    def get(self, key: str) -> Optional[BinaryIO]:
        """S3에서 파일 다운로드"""
        self._check_available()

        try:
            from io import BytesIO
            buffer = BytesIO()
            self.s3.download_fileobj(self.bucket_name, key, buffer)
            buffer.seek(0)
            return buffer
        except self.s3.exceptions.NoSuchKey:
            return None
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        """S3에서 파일 삭제"""
        self._check_available()

        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """S3 오브젝트 존재 여부 확인"""
        self._check_available()

        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def get_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Presigned URL 생성"""
        self._check_available()

        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception:
            return None

    def list_files(self, prefix: str = "") -> List[StorageFile]:
        """S3 버킷 내 오브젝트 목록 조회"""
        self._check_available()

        files = []
        try:
            paginator = self.s3.get_paginator('list_objects_v2')

            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                for obj in page.get('Contents', []):
                    files.append(StorageFile(
                        key=obj['Key'],
                        filename=obj['Key'].split('/')[-1],
                        size=obj['Size'],
                        content_type='application/octet-stream',  # S3는 기본 메타데이터에서 확인 필요
                        created_at=obj['LastModified'],
                        url=self.get_url(obj['Key']),
                    ))
        except Exception:
            pass

        return files


class StorageFactory:
    """
    스토리지 백엔드 팩토리

    환경 설정에 따라 적절한 스토리지 백엔드 인스턴스 생성
    """

    _instance: Optional[StorageBackend] = None

    @classmethod
    def get_storage(cls, storage_type: Optional[str] = None) -> StorageBackend:
        """
        스토리지 인스턴스 반환 (싱글톤)

        Args:
            storage_type: 스토리지 타입 ('local', 's3')
                         None이면 설정에서 자동 감지

        Returns:
            StorageBackend 인스턴스
        """
        if cls._instance is not None:
            return cls._instance

        # 환경 변수에서 스토리지 타입 결정
        if storage_type is None:
            storage_type = os.environ.get('STORAGE_TYPE', 'local')

        if storage_type == 's3':
            cls._instance = S3Storage(
                bucket_name=os.environ.get('S3_BUCKET_NAME', 'ppt-automation'),
                region=os.environ.get('S3_REGION', 'ap-northeast-2'),
                access_key=os.environ.get('AWS_ACCESS_KEY_ID'),
                secret_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                endpoint_url=os.environ.get('S3_ENDPOINT_URL'),
            )
        else:
            cls._instance = LocalStorage()

        return cls._instance

    @classmethod
    def reset(cls):
        """싱글톤 인스턴스 리셋 (테스트용)"""
        cls._instance = None


# 편의를 위한 기본 스토리지 인스턴스
def get_storage() -> StorageBackend:
    """기본 스토리지 인스턴스 반환"""
    return StorageFactory.get_storage()
