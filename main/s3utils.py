from storages.backends.s3boto import S3BotoStorage



class StaticS3BotoStorage(S3BotoStorage):
    location = 'assets'
    upload_to = 'assets'

class MediaS3BotoStorage(S3BotoStorage):
    location = 'media'
    upload_to = 'media'
