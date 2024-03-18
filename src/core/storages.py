# type: ignore
from storages.backends.s3boto3 import S3Boto3Storage


class ProdReadOnlyStorage(S3Boto3Storage):
    def exists(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return True

    def delete(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return

    def size(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return 100500

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return None
