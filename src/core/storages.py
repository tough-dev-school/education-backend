from django.core.files import File
from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore[import-untyped]


class ProdReadOnlyStorage(S3Boto3Storage):
    def exists(self, name: str) -> bool:
        del name

        return True

    def delete(self, name: str) -> None:
        del name

    def save(self, name: str, content: File, max_length: int | None = None) -> None:
        del content, name, max_length

    def size(self) -> int:
        return 100500
