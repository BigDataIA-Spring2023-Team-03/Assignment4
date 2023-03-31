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
s3_bucket_name = 'batch-assignment-4'

whisper_secret_key = Variable.get('WHISPER_API_SECRET')

openai.api_key = whisper_secret_key

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'audio_transcription_batch',
    default_args=default_args,
    description='Transcribe batch audio files from S3 using Whisper API',
    schedule_interval=timedelta(days=1),
    # params=user_input
)

# TODO - can merge these 2 below functions, no point of having 2 s3 clients
def transcribe_audio_file(bucket_name, key):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = s3.get_object(Bucket=bucket_name, Key='raw/' + key)
    audio_data = response["Body"].read()
    audio_file = io.BytesIO(audio_data)
    audio_file.name = key
    transcription = openai.Audio.transcribe("whisper-1", audio_file)
    transcription['text'] = transcription['text'].replace("'", "")
    transcription['text'] = transcription['text'].replace('"', "")
    return transcription

def process_audio_files(ti, **kwargs):
    filename = kwargs['filename']
    index = kwargs['index']
    if "/" in filename:
        filename = filename.split('/')[-1]
    ti.xcom_push(key=filename, value=transcribe_audio_file(s3_bucket_name, filename))


def push_text(ti, **kwargs):
    filename = kwargs['filename']
    index = kwargs['index']
    if "/" in filename:
        filename = filename.split('/')[-1]
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    transcribed_audio = ti.xcom_pull(task_ids=[f'process_audio_files_{index}'], key=filename)[0]['text']
    transcript_file = f"{filename.split('.')[0]}_transcript.txt"

    with open(transcript_file, 'w') as f:
        f.write(transcribed_audio)

    with open(transcript_file, 'rb') as data:
        s3.upload_fileobj(data, s3_bucket_name, 'processed/' + transcript_file)

    os.remove(transcript_file)


def default_quessionaire(ti, **kwargs):
    filename = kwargs['filename']
    index = kwargs['index']
    if "/" in filename:
        filename = filename.split('/')[-1]
    transcribed_audio = ti.xcom_pull(task_ids=[f'process_audio_files_{index}'], key=filename)[0]['text']
    default_questions_answers = {
        "Summarize the topic of following text in three words or less:": "",
        "How many people might be involved in the audio?": "",
        "What are the names of the people in the audio?": ""
    }
    for i, (j,k) in enumerate(default_questions_answers.items()):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": j + transcribed_audio}],
            temperature=0.7
        )

        chat_output = completion.choices[0].message.content.strip()
        chat_output = chat_output.replace("'", "")
        chat_output = chat_output.replace("'", "")
        default_questions_answers[j] = chat_output
        ti.xcom_push(key="answers", value=default_questions_answers)


def push_answers(ti, **kwargs):
    # filename from streamlit
    filename = kwargs['filename']
    index = kwargs['index']
    if "/" in filename:
        filename = filename.split('/')[-1]

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    answers = ti.xcom_pull(task_ids=[f'default_quessionaire_{index}'], key='answers')[0]
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

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3_objects = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix='raw/')
s3_files = [obj["Key"] for obj in s3_objects.get("Contents", []) if not obj['Key'] == 'raw/']

print(s3_files)



for i,file in enumerate(s3_files):
    task_process_audio_files = PythonOperator(
        task_id=f'process_audio_files_{i}',
        provide_context=True,
        python_callable=process_audio_files,
        op_kwargs={'filename': file, 'index': i},
        dag=dag
    )

    task_push_text = PythonOperator(
        task_id=f'push_text_{i}',
        provide_context=True,
        python_callable=push_text,
        op_kwargs={'filename': file, 'index': i},
        dag=dag
    )

    task_default_quessionaire = PythonOperator(
        task_id=f'default_quessionaire_{i}',
        provide_context=True,
        python_callable=default_quessionaire,
        op_kwargs={'filename': file, 'index': i},
        dag=dag
    )

    task_push_answers = PythonOperator(
        task_id=f'push_answers_{i}',
        provide_context=True,
        python_callable=push_answers,
        op_kwargs={'filename': file, 'index': i},
        dag=dag
    )

    # clear_xcoms = PythonOperator(
    #     task_id='clear_xcoms',
    #     python_callable=clear_xcoms,
    #     provide_context=True,
    #     dag=dag
    # )

    task_start = DummyOperator(
        task_id=f'start_{i}',
        dag=dag
    )


    task_end = DummyOperator(
        task_id=f'end_{i}',
        dag=dag
    )


    ###################################################################################################

    task_start >> task_process_audio_files >> [task_push_text, task_default_quessionaire]
    task_default_quessionaire >> task_push_answers
    task_push_text >> task_end
    task_push_answers >> task_end
