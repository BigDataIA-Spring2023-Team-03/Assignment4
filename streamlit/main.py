import os
import streamlit as st
import boto3
from dotenv import load_dotenv
import requests
import json
import subprocess
import time
import openai
from Logging.aws_logging import write_logs

# DEV or PROD
environment = 'PROD'
if environment == 'DEV':
    webserver = 'localhost:8080'
elif environment == 'PROD':
    webserver = 'airflow-airflow-webserver-1:8080'

# Load the environment variables from the .env file
load_dotenv()

# Get the AWS access key ID and secret access key from the environment variables
# aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
# aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")

# Get the S3 bucket name and region from the environment variables
# s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
s3_bucket_name = 'adhoc-assignment-4'

openai.organization = "org-1yfndFUb17q04b6u9hdKuPsn"
openai.api_key = os.getenv("openai_api_key")

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

if 'custom' not in st.session_state:
    st.session_state.custom = False

if 'transcript' not in st.session_state:
    st.session_state.transcript = ''

if 'file_name' not in st.session_state:
    st.session_state.file_name = ''

if 'transcription_generated' not in st.session_state:
    st.session_state.transcription_generated = False

if 'convert_to_transcript' not in st.session_state:
    st.session_state.convert_to_transcript = False

# Check DAG Status
def check_dag_status(dag_id):
    url = f'http://{webserver}/api/v1/dags/{dag_id}/dagRuns'
    response = requests.get(url = url, auth=('airflow2','airflow2'))
    response_json = response.json()
    state = response_json['dag_runs'][len(response_json['dag_runs'])-1]['state']
    return state


# Define the Streamlit app
def main():
    # Set the title of the app
    st.title("MP3 Uploader and Transcription")
    st.write('File must be in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.')

    dag_id = "audio_transcription"
    dag_status = check_dag_status(dag_id)

    if dag_status == "running":
        st.write("Please wait for the DAG to finish running...")
        time.sleep(10)
        dag_status = check_dag_status(dag_id)
        st.experimental_rerun()
    else:
        # Create a file uploader
        uploaded_file = st.file_uploader("Upload an MP3 file")

    # Create a dropdown to select an existing file from the S3 bucket
    s3_objects = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix='raw/')
    s3_files = [obj["Key"] for obj in s3_objects.get("Contents", []) if not obj['Key'] == 'raw/']
    # Get Necessary file
    s3_files = [file.split('/')[1] for file in s3_files if file[-1] != '/' and file.split('.')[1] in ('wav', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'webm')]

    selected_file = st.selectbox("Select an existing file from S3", ["None"] + s3_files)

        # Check if both an uploaded file and an S3 file were selected
        if uploaded_file and selected_file != "None":
            st.write("Error: please select only one option")
        else:
            # Check if an uploaded file was selected
            if uploaded_file is not None:
                if uploaded_file.name.split('.')[1] not in ('wav', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'webm'):
                    st.error(f'Incorrect File Format!')
                    st.stop()
                # Get the file name and size
                filename = uploaded_file.name
                if not filename == st.session_state.file_name:
                    st.session_state.transcription_generated = False
                    st.session_state.transcript = ''
                    st.session_state.file_name = filename
                    st.session_state.convert_to_transcript = False
                filesize = uploaded_file.size

                # Print the file name and size
                st.write("File name:", filename)
                st.write("File size:", filesize, "bytes")

                # Upload the file to the S3 bucket if it doesn't already exist
                if filename not in s3_files:
                    s3_client.upload_fileobj(uploaded_file, s3_bucket_name, 'raw/' + filename)
                    st.write("File uploaded successfully!")
                else:
                    st.write("File already exists in S3 bucket.")

            # Check if an S3 file was selected
            elif selected_file != "None":
                # Get the file name and size
                filename = selected_file
                if not filename == st.session_state.file_name:
                    st.session_state.transcription_generated = False
                    st.session_state.transcript = ''
                    st.session_state.file_name = filename
                    st.session_state.convert_to_transcript = False
                obj = s3_client.get_object(Bucket=s3_bucket_name, Key=filename)
                filesize = obj["ContentLength"]

                # Print the file name and size
                st.write("File name:", filename)
                st.write("File size:", filesize, "bytes")

            # If no file was selected
            else:
                st.write("### No file selected")

            # Create a button to convert the file to transcript
            if uploaded_file or selected_file != "None":
                # response_transcript = ''
                # if not st.session_state.convert_to_transcript:
                #     st.session_state.convert_to_transcript = st.checkbox('Convert To Transcript')
                check = st.checkbox('Convert To Transcript')
                if check:
                    if uploaded_file or selected_file:
                        # If a file was uploaded or selected, get the file name and pass it to the conversion script
                        if uploaded_file:
                            # AWS CloudWatch Logging
                            write_logs(f'File Method: Uploaded, filename: {uploaded_file}')
                            filename = uploaded_file.name
                        else:
                            # AWS CloudWatch Logging
                            write_logs(f'File Method: Selected, filename: {selected_file}')
                            filename = selected_file

                        if not st.session_state.transcription_generated:
                            # API Call to Airflow to execute process_audio_files_dag
                            data = {
                                    "dag_run_id": "",
                                    "conf": {"filename": filename}
                                    }
                            response = requests.post(url = f'http://{webserver}/api/v1/dags/audio_transcription/dagRuns', json=data, auth=('airflow2','airflow2'))
                            if response.status_code == 409:
                                st.error(f'{filename} already transferred to S3!')

                            dag_run_id = response.json()['dag_run_id']
                            st.write(f"Dag_run_id: {dag_run_id}")
                        
                        # response_transcript = convert_mp3_to_text_function(filename)
                        # st.write("Transcript:", response_transcript)

                            starttime = time.time()
                            while check_dag_status("audio_transcription") not in ('failed', 'success'):
                                time.sleep(10.0 - ((time.time() - starttime) % 10.0))

                            # AWS CloudWatch Logging
                            write_logs(f'Process: ADHOC, DAG_RUN_ID: {dag_run_id}, Status: {check_dag_status("audio_transcription")}')

                            if check_dag_status("audio_transcription") == 'success':
                                if '/' in filename:
                                    filename = filename.split('/')[-1]
                                data = {
                                        "dag_id": "audio_transcription",
                                        "dag_run_id": dag_run_id,
                                        "task_id": "process_audio_files",
                                        "xcom_key": filename
                                        }

                                url = f"http://{webserver}/api/v1/dags/{data['dag_id']}/dagRuns/{data['dag_run_id']}/taskInstances/{data['task_id']}/xcomEntries/{data['xcom_key']}"

                                response = requests.get(url=url, auth=('airflow2', 'airflow2'))
                            # st.write(response.json())

                                response_transcript = response.json()['value']
                                st.session_state.transcript = response_transcript
                                st.session_state.transcription_generated = True

                                data = {
                                        "dag_id": "audio_transcription",
                                        "dag_run_id": dag_run_id,
                                        "task_id": "default_quessionaire",
                                        "xcom_key": "answers"
                                        }

                                url = f"http://{webserver}/api/v1/dags/{data['dag_id']}/dagRuns/{data['dag_run_id']}/taskInstances/{data['task_id']}/xcomEntries/{data['xcom_key']}"

                                response = requests.get(url = url, auth=('airflow2','airflow2'))
                                st.write('Standard Questions and Answers:')
                                response_answers = response.json()['value'].replace("'", '"')
                                for i,(j,k) in enumerate(json.loads(response_answers).items()):
                                    st.write(f'# Q{i+1}: {j}')
                                    st.write(f'## A: {k}')

                        if st.session_state.transcription_generated:
                            st.write("### Custom Question")
                            custom_question = st.text_input("What would you like to ask?")
                            if custom_question != "":
                                # AWS CloudWatch Logging
                                write_logs(f'Custom Question: {custom_question}')

                                # Generate the answer using OpenAI's GPT-3
                                answer = openai.Completion.create(
                                    engine="text-davinci-002",
                                    prompt=f"Q: {st.session_state.transcript + custom_question}\nA:",
                                    max_tokens=1024,
                                    n=1,
                                    stop=None,
                                    temperature=0.7,
                                )

                                total_tokens = answer['usage']['total_tokens']

                                # Print the answer
                                st.write("### Answer")
                                st.write(answer.choices[0].text.strip())
                                st.write(f'Tokens Used: {total_tokens}')

                                # AWS CloudWatch Logging
                                # write_logs(f'GPT Answer: {answer.choices[0].text.strip()}')
                                log_custom_q = {'Custom_Question': custom_question,
                                            'Answer': answer.choices[0].text.strip(),
                                            'Tokens': total_tokens
                                            }
                                write_logs(str(log_custom_q))

                        else:
                            st.error(f'Airflow DAG failed!')


                    else:
                        st.warning("Please upload a file or select an existing file from S3.")



# Run the Streamlit app
if __name__ == "__main__":
    main()

