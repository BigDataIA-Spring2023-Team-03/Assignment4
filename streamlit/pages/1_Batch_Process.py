import os
import streamlit as st
import boto3
from dotenv import load_dotenv
import requests
import time
from main import check_dag_status
import json

# Load the environment variables from the .env file
load_dotenv()

# Get the AWS access key ID and secret access key from the environment variables
aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")

# Get the S3 bucket name and region from the environment variables
# s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
s3_bucket_name = 'batch-assignment4'

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

def file_and_filetype(s3_files):
    # Select a file and Read Transcript or q&a from S3
    selected_file = st.selectbox("Select a File:", [""] + s3_files)
    desired_output = st.selectbox("Desired Output - Transcript or Q&A:", [""] + ['Transcript', 'Q&A'])
    return selected_file, desired_output

# SEssion State Initialization
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = ''

if 'desired_output' not in st.session_state:
    st.session_state.desired_output = ''

if 'dag_executed' not in st.session_state:
    st.session_state.dag_executed = False




# Set the title of the app
st.title("Batch Process")
st.write('This process reads all the files from the Batch Folder in AWS S3. The transcript for these audio files extracted. Additionally, the core questions and answers from the transcript are extracted. These files are saved off in AWS S3.')

# @st.cache
# Enter Password to Access Batch Functionality
password = st.text_input("Enter Password:")

if password != '':
    if password == 'damgadmin': 
        # Create a list of all the files in the Batch Folder
        s3_objects = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix='raw')
        s3_files = [obj["Key"] for obj in s3_objects.get("Contents", [])]
        # Get Necessary file
        s3_files = [file.split('/')[1] for file in s3_files if file[-1] != '/' and file.split('.')[1] in ('wav')]

        st.write(f'Total Files: {len(s3_files)}')
        st.write(f'File List:')
        st.write(s3_files)

        # Convert files to transcript and Q&A
        if st.checkbox(f"Convert {len(s3_files)} Files to Transcript"):
            
            if not st.session_state.dag_executed:
                # TESTING
                # time.sleep(5)

                # API Call to Airflow to execute process_audio_files_dag
                data = {
                        "dag_run_id": "",
                        "conf": {}
                        }
                response = requests.post(url = 'http://localhost:8080/api/v1/dags/audio_transcription_batch/dagRuns', json=data, auth=('airflow2','airflow2'))
                if response.status_code == 409:
                    st.error(f'{filename} already transferred to S3!')

                # TESTING
                # st.write(response.json())
                st.write(f"Dag_run_id: {response.json()['dag_run_id']}")

                dag_run_id = response.json()['dag_run_id']

                st.write('DAG Status Check (Checks every 30s):')
                # API to get DAG status, only proceed when you have a state = success
                # checks every 30 seconds if dag not failed or success
                starttime = time.time()
                while check_dag_status("audio_transcription_batch") not in ('failed', 'success'):
                    print("tick")
                    time.sleep(30.0 - ((time.time() - starttime) % 30.0))

                # Dag runs successfully
                if check_dag_status("audio_transcription_batch") == 'success':
                    st.session_state.dag_executed = True
                else:
                    # TODO:
                    st.error("Error during DAG run!")
    else:
        st.error("You don't have permission to access this functionality")

if st.session_state.dag_executed:
    # Select a file and Read Transcript or q&a from S3
    # selected_file = st.selectbox("Select a File:", ["None"] + s3_files)
    # desired_output = st.selectbox("Desired Output - Transcript or Q&A:", ["None"] + ['Transcript', 'Q&A'])

    selected_file, desired_output = file_and_filetype(s3_files)
    st.session_state.selected_file = selected_file
    st.session_state.desired_output = desired_output
    if st.button('Generate'):
        if selected_file != '' and desired_output != '':
            # TESTING
            # st.write(st.session_state.selected_file, st.session_state.desired_output)
        
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            if st.session_state.desired_output == 'Transcript':
                transcript_file = f"{st.session_state.selected_file.split('.')[0]}_transcript.txt"
                response = s3_client.get_object(Bucket=s3_bucket_name, Key=f'processed/{transcript_file}')
                response_transcript = response['Body'].read().decode()
                st.write(f'Filename: processed/{transcript_file}')
                st.write('Transcript:')
                st.write(response_transcript)
            else:
                answer_file = f"{st.session_state.selected_file.split('.')[0]}_answers.json"
                response = s3_client.get_object(Bucket=s3_bucket_name, Key=f'answers/{answer_file}')
                response_answers = response['Body'].read().decode()
                st.write(f'Filename: processed/{answer_file}')
                st.write('Answers:')
                st.json(response_answers)
    
    # No more statements will be run
    # st.experimental_rerun()

        
    