# type: ignore
from storages.backends.s3boto3 import S3Boto3Storage


class ProdReadOnlyStorage(S3Boto3Storage):
    def exists(self, *args, **kwargs):
        return True

    def delete(self, *args, **kwargs):
        return

    def size(self, *args, **kwargs):
        return 100500

    def save(self, *args, **kwargs):
        return None
