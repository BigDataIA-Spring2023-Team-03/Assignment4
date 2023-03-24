import boto3
from botocore import UNSIGNED
from botocore.config import Config
import os
from decouple import config
from botocore.exceptions import ClientError

aws_access_key_id = config('aws_access_key_id')
aws_secret_access_key = config('aws_secret_access_key')


class S3Util:
    def __init__(self, resource, bucket_name):
        # self.s3 = boto3.client(resource, config=Config(signature_version=UNSIGNED))
        self.s3 = boto3.client(resource, 
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key)
        self.bucket_name = bucket_name

    def upload_file(self, file_name, bucket, object_name=None):
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        print('test1')
        # Upload the file
        s3_client = boto3.client('s3')
        print('test2')
        # try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        # except ClientError as e:
        #     logging.error(e)
        #     return False
        return True
    
    # def get_pages(self, prefix=''):
    #     paginator = self.s3.get_paginator('list_objects')
    #     return paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

    # def get_url(self, *args):
    #     url = self.s3.generate_presigned_url(
    #         ClientMethod='get_object',
    #         Params={
    #             'Bucket': self.bucket_name,
    #             'Key': '/'.join(args)
    #         }
    #     )
    #     return url



#########################################
# # SCRAP
# s3Util = S3Util('s3', 'damg7245-assignment4')

# dir(s3Util)
# s3Util.bucket_name
# s3Util.s3.upload_file('JV_AUDIO_EXAMPLE.WAV', 'damg7245-assignment4', 'Uploaded_Audio_Files/JV_AUDIO_EXAMPLE.WAV')

# # Why Doesn't this work?
# s3Util.upload_file('JV_AUDIO_EXAMPLE.WAV', 'In_Audio_Files')