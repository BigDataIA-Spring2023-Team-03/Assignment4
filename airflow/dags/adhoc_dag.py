import os
from datetime import datetime, timedelta
from decouple import config, AutoConfig
import boto3

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.S3_hook import S3Hook

import openai

# TODO: go up one directory and use that .env file
# config = AutoConfig(search_path='..')

aws_access_key_id = config('aws_access_key_id')
aws_secret_access_key = config('aws_secret_access_key')

openai.organization = config('openai_organization')
openai.api_key = config('openai_api_key')


###################################################################################################
# Define your Airflow DAG settings
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='adhoc_dag',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2022, 3, 23),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["airflow", "adhoc", "transcribe_audio"]
) as dag:


    ###################################################################################################
    # PYTHON FUNCTIONS:
    def get_location():
        print(f'Current Working Directory: {os.getcwd()}')

    # Download audio file from S3
    # def s3_get_audio_file():
        # hook = S3Hook('s3_conn')
        # hook.get_key(key=key, bucket_name=bucket_name)

    # Function to Upload the Transcribed text to S3
    def upload_to_s3(filename, bucket, object_name):
        # hook = S3Hook('s3_conn')
        # hook.load_file(filename=filename, key=key, bucket_name=bucket_name)
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        response = s3_client.upload_file(file_name, bucket, object_name)

    # Function to Pass the Audio file through whisper API
    def transcribe_audio_file(bucket_name, file_name):
        # Download the audio file from S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        # audio_data = response["Body"].read()

        # audio_file= open("JV_AUDIO_EXAMPLE.wav", "rb")
        audio_file = open(response, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        transcription = transcript.text
        # TESTING
        print(transcription)
        return transcription

    # Check to check files in S3
    def process_audio_files(bucket_name):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        objects = s3.list_objects_v2(Bucket=s3_bucket_name)['Contents']
        for obj in objects:
            filename = obj['Key']
            # TESTING
            print(filename)
            if filename.endswith('.wav'):
                transcription = transcribe_audio_file(bucket_name, filename)

                # Convert string to text file
                with open(f"{file_name}.txt", "w") as text_file:
                    text_file.write(transcription)

                # Upload file to S3
                upload_to_s3(f"{file_name}.txt", bucket_name, f"Audio_Transcripts/{file_name}.txt")




    

    ###################################################################################################
    # TASKS:
    # Print Location:
    task_get_location = PythonOperator(
        task_id='get_location',
        python_callable=get_location
    )

    # Transcribe the file
    task_process_audio_files = PythonOperator(
        task_id='process_audio_files',
        python_callable=process_audio_files,
        op_kwargs={
            'bucket_name': 'damg7245-assignment4'
            # 'key': 'Uploaded_Audio_Files/JV_AUDIO_EXAMPLE.WAV'
        }
    )

    # Upload Transcription to S3
    task_upload_to_s3 = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        op_kwargs={
            'filename': '/home/jvidelefsky/airflow_a4/JV_AUDIO_EXAMPLE.WAV',
            'key': 'Audio_Transcripts/JV_AUDIO_EXAMPLE.WAV',
            'bucket_name': 'damg7245-assignment4'
        }
    )

    
    ###################################################################################################
    # FLOW:
    task_get_location >> task_process_audio_files # >> task_upload_to_s3