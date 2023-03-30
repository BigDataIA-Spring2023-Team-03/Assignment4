import boto3
import openai
import os
import io
import requests
from dotenv import load_dotenv
from typing import Tuple
import boto3
from botocore.client import Config
import json
# AWS credentials

def OpenAiAPiCall(txt_file_key: str, question : str):

    load_dotenv()

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    whisper_api_key = os.getenv("WHISPER_API_KEY")
    s3_bucket_folder = os.getenv("FOLDER_NAME")
    open_api = os.getenv("OPENAI_API_KEY")

    # Initialize S3 client
    URL_EXPIRATION_TIME = 300000 # in seconds

    s3 = boto3.client('s3',
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name='us-east-2',
                            config=Config(signature_version='s3v4'))

    response = s3.get_object(Bucket=s3_bucket_name, Key=txt_file_key)
    text = response["Body"].read().decode()    
    print("\n Text in Processed_Audio: ",text) 

    # Set up OpenAI API client
    openai.api_key = open_api

    # Call OpenAI API to generate text
    prompt = f"{text}\nQ: {question}\nA:"
    answer = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        stop="\n"
    )
    
    answer_text = answer.choices[0].text.strip()

# Print the answer
    print("\n Answer: ",answer_text)


    # Display generated text
    return answer_text

