import boto3
import io
import os
import requests
from dotenv import load_dotenv
from typing import Tuple
import boto3
from botocore.client import Config



def convert_mp3_to_text_function(mp3_file_key: str):

    load_dotenv()

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    whisper_api_key = os.getenv("WHISPER_API_KEY")
  
    


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



    # Call the Whisper API to convert the MP3 file to text
    # headers = {"Authorization": f"Bearer {os.getenv('WHISPER_API_KEY')}"}
    # url = "https://api.whisper.ai/v1/recognize"
    # response = requests.post(url, headers=headers, data=mp3_file, stream=True)
    # response.raise_for_status()

    # # Extract the transcript and confidence score from the API response
    # data = response.json()
    # transcript = data["transcript"]

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
    "numSpeakers": "1",
    #if using diarization, you can inform the model how many speakers you have
    #if no value set, the model figures out numSpeakers automatically!
    "url": mp3_url, #can't have both a url and file sent!
    "language": "en", #if this isn't set, the model will auto detect language,
    "task": "transcribe" #default is transcribe. Other option is "translate"
    #translate will translate speech from language to english
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.text)

    return response.text



