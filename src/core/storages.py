from storages.backends.s3boto3 import S3Boto3Storage
from typing import no_type_check


class ProdReadOnlyStorage(S3Boto3Storage):
    @no_type_check
    def exists(self, *args, **kwargs):
        return True

    @no_type_check
    def delete(self, *args, **kwargs):
        return

    @no_type_check
    def size(self, *args, **kwargs):
        return 100500

    @no_type_check
    def save(self, *args, **kwargs):
        return None
