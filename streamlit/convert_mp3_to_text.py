#Author: Raj Mehta
#Description: Back end code for Audio Transcription using Whisper Api (https://whisperapi.com/)

import boto3
import io
import os
import requests
from dotenv import load_dotenv
from typing import Tuple
import boto3
from botocore.client import Config
import json

def convert_mp3_to_text_function(mp3_file_key: str):

    load_dotenv()

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    whisper_api_key = os.getenv("WHISPER_API_KEY")
    s3_bucket_folder = os.getenv("FOLDER_NAME")
  
    


    object_key = mp3_file_key
    URL_EXPIRATION_TIME = 300000 # in seconds

    s3_client = boto3.client('s3',
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name='us-east-2',
                            config=Config(signature_version='s3v4'))

    mp3_url = s3_client.generate_presigned_url('get_object',
                                        Params={'Bucket': s3_bucket_name,
                                                'Key': object_key},
                                        ExpiresIn=URL_EXPIRATION_TIME)

    print(mp3_url)


    url = "https://transcribe.whisperapi.com"
    headers = {
    'Authorization': 'Bearer ' + whisper_api_key
    }
    # file = {'file': open(mp3_url, 'rb')}
    data = {
    "fileType": "mp3", #default is wav
    "diarization": "false",
    #Note: setting this to be true will slow down results.
    #Fewer file types will be accepted when diarization=true
    "numSpeakers": "2",
    #if using diarization, you can inform the model how many speakers you have
    #if no value set, the model figures out numSpeakers automatically!
    "url": mp3_url, #can't have both a url and file sent!
    "language": "en", #if this isn't set, the model will auto detect language,
    "task": "transcribe" #default is transcribe. Other option is "translate"
    #translate will translate speech from language to english
    }

    response = requests.post(url, headers=headers, data=data)

    print("\n",type(response.text))
    print("\n")
    
    # Convert response to JSON object and extract text attribute
    response_json = json.loads(response.text)
    print("\n Response from Whisper API:",response_json)
    text = response_json['text']

    file_upload_name = mp3_file_key[:-4] + ".txt"
    with open('my_file.txt', 'w') as f:
        f.write(text)

    # Upload text data to S3 bucket
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.put_object(Body=text, Bucket=s3_bucket_name, Key=s3_bucket_folder+ file_upload_name)

    return text



