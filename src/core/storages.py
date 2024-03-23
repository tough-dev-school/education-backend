from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore[import-untyped]


class ProdReadOnlyStorage(S3Boto3Storage):
    def exists(self, name: str) -> bool:
        del name

        return True

    def delete(self, name: str) -> None:
        del name

    def size(self) -> int:
        return 100500
