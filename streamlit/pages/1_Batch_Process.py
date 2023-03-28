import os
import streamlit as st
import boto3
from dotenv import load_dotenv
import requests
import time
from main import check_dag_status

# Load the environment variables from the .env file
load_dotenv()

# Get the AWS access key ID and secret access key from the environment variables
aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")

# Get the S3 bucket name and region from the environment variables
# s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
s3_bucket_name = 'raw-assignment4'

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

def file_and_filetype(s3_files):
    # Select a file and Read Transcript or q&a from S3
    selected_file = st.selectbox("Select a File:", ["None"] + s3_files)
    desired_output = st.selectbox("Desired Output - Transcript or Q&A:", ["None"] + ['Transcript', 'Q&A'])
    return selected_file, desired_output


# Set the title of the app
st.title("Batch Process")
st.write('This process reads all the files from the Batch Folder in AWS S3. The transcript for these audio files extracted. Additionally, the core questions and answers from the transcript are extracted. These files are saved off in AWS S3.')

# @st.cache
# Enter Password to Access Batch Functionality
password = st.text_input("Enter Password:")

if password != '':
    if password == 'damgadmin': 
        # Create a list of all the files in the Batch Folder
        s3_objects = s3_client.list_objects_v2(Bucket=s3_bucket_name)
        s3_files = [obj["Key"] for obj in s3_objects.get("Contents", [])]
        st.write(f'Total Files: {len(s3_files)}')
        st.write(f'File List:')
        st.write(s3_files)

        # Convert files to transcript and Q&A
        if st.button(f"Convert {len(s3_files)} Files to Transcript"):

            # API Call to Airflow to execute process_audio_files_dag
            data = {
                    "dag_run_id": "",
                    "conf": {"filename": filename}
                    }
            response = requests.post(url = 'http://localhost:8080/api/v1/dags/audio_transcription/dagRuns', json=data, auth=('airflow2','airflow2'))
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
            while check_dag_status() not in ('failed', 'success'):
                print("tick")
                time.sleep(30.0 - ((time.time() - starttime) % 30.0))

            Select a file and Read Transcript or q&a from S3
            selected_file = st.selectbox("Select a File:", ["None"] + s3_files)
            desired_output = st.selectbox("Desired Output - Transcript or Q&A:", ["None"] + ['Transcript', 'Q&A'])

            selected_file, desired_output = file_and_filetype()
            if st.button('Generate'):
                if selected_file != 'None' and desired_output != 'None':
                
                    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
                    if desired_output == 'Transcript':
                        transcript_file = f"{selected_file.split('.')[0]}_transcript.txt"
                        response = s3.get_object(Bucket='processed-text-assignment4', Key=transcript_file)
                        response_transcript = response.json()
                        st.write('Transcript:')
                        st.json(response_transcript)
                    else:
                        answer_file = f"{selected_file.split('.')[0]}_answers.json"
                        response = s3.get_object(Bucket='answers-assignment4', Key=answer_file)
                        response_answers = response.json()
                        st.write('Answers:')
                        st.json(response_answers)
        
    else:
        st.error("You don't have permission to access this functionality")