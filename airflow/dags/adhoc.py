import boto3
import io
import json
import os
from datetime import datetime, timedelta
from airflow.models import DAG, XCom, Variable
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models.param import Param
import openai

aws_access_key_id = Variable.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = Variable.get('AWS_SECRET_ACCESS_KEY')
s3_bucket_name = 'adhoc-assignment-4'

whisper_secret_key = Variable.get('WHISPER_API_SECRET')

openai.api_key = whisper_secret_key

# PARAMS --> from Streamlit
user_input = {
    "filename": Param('No File Name!', type='string')
}


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'audio_transcription',
    default_args=default_args,
    description='Transcribe audio files from S3 using Whisper API',
    schedule_interval=timedelta(days=1),
    params=user_input
)

# TESTING
# def testing(**kwargs):
#     print(f'Current Working Directory: {os.getcwd()}')
#     print(f"File Input from Streamlit: {kwargs['dag_run'].conf['filename']}")

def transcribe_audio_file(bucket_name, key):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = s3.get_object(Bucket=bucket_name, Key='raw/' + key)
    audio_data = response["Body"].read()
    audio_file = io.BytesIO(audio_data)
    audio_file.name = key
    transcription = openai.Audio.transcribe("whisper-1", audio_file)

    return transcription

def process_audio_files(ti, **kwargs):
    filename = kwargs['dag_run'].conf['filename']
    if "/" in filename:
        filename = filename.split('/')[-1]
    ti.xcom_push(key=filename, value=transcribe_audio_file(s3_bucket_name, filename))


def push_text(ti, **kwargs):
    filename = kwargs['dag_run'].conf['filename']
    if "/" in filename:
        filename = filename.split('/')[-1]
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    transcribed_audio = ti.xcom_pull(task_ids=['process_audio_files'], key=filename)[0]['text']
    transcript_file = f"{filename.split('.')[0]}_transcript.txt"

    with open(transcript_file, 'w') as f:
        f.write(transcribed_audio)

    with open(transcript_file, 'rb') as data:
        s3.upload_fileobj(data, s3_bucket_name, 'processed/' + transcript_file)

    os.remove(transcript_file)


def default_quessionaire(ti, **kwargs):
    # filename from streamlit
    filename = kwargs['dag_run'].conf['filename']
    if "/" in filename:
        filename = filename.split('/')[-1]
    # s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    transcribed_audio = ti.xcom_pull(task_ids=['process_audio_files'], key=filename)[0]['text']
    # file_name = 'audio1.txt'
    default_questions_answers = {
        "Summarize the topic of following text in three words or less:": "",
        "How many people might be involved in the audio?": "",
        "What are the names of the people in the audio?": ""
    }
    # file_name = 'audio1_answers.txt'
    for i, (j,k) in enumerate(default_questions_answers.items()):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": j + transcribed_audio}],
            temperature=0.7
        )

        chat_output = completion.choices[0].message.content.strip()
        default_questions_answers[j] = chat_output
        ti.xcom_push(key="answers", value=default_questions_answers)


def push_answers(ti, **kwargs):
    # filename from streamlit
    filename = kwargs['dag_run'].conf['filename']
    if "/" in filename:
        filename = filename.split('/')[-1]

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    answers = ti.xcom_pull(task_ids=['default_quessionaire'], key='answers')[0]
    answer_file = f"{filename.split('.')[0]}_answers.json"

    # TESTING
    print(answer_file)
    print(answers)

    with open(answer_file, 'w') as f:
        f.write(json.dumps(answers))

    with open(answer_file, 'rb') as data:
        s3.upload_fileobj(data, s3_bucket_name, 'answers/' + answer_file)

    os.remove(answer_file)

def clear_xcoms(**context):
    # TODO: implement this and call at the end of the dag execution
    pass


###################################################################################################
# TASKS:
# testing = PythonOperator(
#     task_id='testing',
#     python_callable=testing,
#     provide_context=True,
#     dag=dag
# )

process_audio_files = PythonOperator(
    task_id='process_audio_files',
    provide_context=True,
    python_callable=process_audio_files,
    dag=dag
)

push_text = PythonOperator(
    task_id='push_text',
    provide_context=True,
    python_callable=push_text,
    dag=dag
)

default_quessionaire = PythonOperator(
    task_id='default_quessionaire',
    provide_context=True,
    python_callable=default_quessionaire,
    dag=dag
)

push_answers = PythonOperator(
    task_id='push_answers',
    provide_context=True,
    python_callable=push_answers,
    dag=dag
)

# clear_xcoms = PythonOperator(
#     task_id='clear_xcoms',
#     python_callable=clear_xcoms,
#     provide_context=True,
#     dag=dag
# )

start = DummyOperator(
    task_id='start',
    dag=dag
)

end = DummyOperator(
    task_id='end',
    dag=dag
)


###################################################################################################

start >> process_audio_files >> [push_text, default_quessionaire]
default_quessionaire >> push_answers
push_text >> end
push_answers >> end