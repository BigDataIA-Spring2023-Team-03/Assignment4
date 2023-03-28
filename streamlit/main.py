#Author: Raj Mehta
#Description: Front end code for Audio Transcription
import os
import streamlit as st
import boto3
from dotenv import load_dotenv
import requests
import subprocess
from convert_mp3_to_text import convert_mp3_to_text_function
import time


# Load the environment variables from the .env file
load_dotenv()

# Get the AWS access key ID and secret access key from the environment variables
# aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
# aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")

# Get the S3 bucket name and region from the environment variables
# s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
s3_bucket_name = 'adhoc-assignment4'

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)


# Check DAG Status
def check_dag_status():
    url = 'http://localhost:8080/api/v1/dags/audio_transcription/dagRuns'
    response = requests.get(url = url, auth=('airflow2','airflow2'))
    response_json = response.json()
    # most recent dag_run
    state = response_json['dag_runs'][-1]['state']
    # if response_json['dag_runs'][0]['state'] == 'failed':
    #     print('failure')

    # TESTING
    st.write(f"- {response_json['dag_runs'][-1]['state']}")
    return state


# Define the Streamlit app
def main():
    # Set the title of the app
    st.title("MP3 Uploader and Transcription")

    # Create a file uploader
    uploaded_file = st.file_uploader("Upload an MP3 file")

    # Create a dropdown to select an existing file from the S3 bucket
    s3_objects = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix='raw/')
    s3_files = [obj["Key"] for obj in s3_objects.get("Contents", []) if not obj['Key'] == 'raw/']
    selected_file = st.selectbox("Select an existing file from S3", ["None"] + s3_files)

    # Check if both an uploaded file and an S3 file were selected
    if uploaded_file and selected_file != "None":
        st.write("Error: please select only one option")
    else:
        # Check if an uploaded file was selected
        if uploaded_file is not None:
            # Get the file name and size
            filename = uploaded_file.name
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
            obj = s3_client.get_object(Bucket=s3_bucket_name, Key=filename)
            filesize = obj["ContentLength"]

            # Print the file name and size
            st.write("File name:", filename)
            st.write("File size:", filesize, "bytes")

        # If no file was selected
        else:
            st.write("No file selected")

        # Create a button to convert the file to transcript
        if uploaded_file or selected_file != "None":
            if st.button("Convert to Transcript"):
                if uploaded_file or selected_file:
                    # If a file was uploaded or selected, get the file name and pass it to the conversion script
                    if uploaded_file:
                        filename = uploaded_file.name
                    else:
                        filename = selected_file

                    # API Call to Airflow to execute process_audio_files_dag
                    data = {
                            "dag_run_id": "",
                            "conf": {"filename": filename}
                            }
                    # TESTING
                    # st.write(data)
                    response = requests.post(url = 'http://localhost:8080/api/v1/dags/audio_transcription/dagRuns', json=data, auth=('airflow2','airflow2'))
                    # response = requests.post(url = 'http://backend:8000/s3_transfer', json=data, headers={'Authorization':  f'Bearer {st.session_state.access_token}'})
                    if response.status_code == 409:
                        st.error(f'{filename} already transferred to S3!')

                    # TESTING
                    # st.write(response)
                    # st.write(response.json())
                    st.write(f"Dag_run_id: {response.json()['dag_run_id']}")

                    dag_run_id = response.json()['dag_run_id']
                    
                    # response_transcript = convert_mp3_to_text_function(filename)
                    # st.write("Transcript:", response_transcript)

                    st.write('DAG Status Check (Checks every 30s):')
                    # API to get DAG status, only proceed when you have a state = success
                    # checks every 30 seconds if dag not failed or success
                    starttime = time.time()
                    while check_dag_status() not in ('failed', 'success'):
                        print("tick")
                        time.sleep(30.0 - ((time.time() - starttime) % 30.0))

                    if check_dag_status() == 'success':
                        # API Call to Airflow to get transcript from XCOM
                        if '/' in filename:
                            filename = filename.split('/')[-1]
                        data = {
                                "dag_id": "audio_transcription",
                                "dag_run_id": dag_run_id,
                                "task_id": "process_audio_files",
                                "xcom_key": filename
                                }

                        url = f"http://localhost:8080/api/v1/dags/{data['dag_id']}/dagRuns/{data['dag_run_id']}/taskInstances/{data['task_id']}/xcomEntries/{data['xcom_key']}"
                        # TESTING
                        # st.write(url, data)

                        response = requests.get(url=url, auth=('airflow2', 'airflow2'))
                        st.write(response.json())

                        response_transcript = response.json()['value']
                        st.write('Transcript:')
                        st.json(response_transcript)

                        # API Call to Airflow to get answers from XCOM
                        data = {
                                "dag_id": "audio_transcription",
                                "dag_run_id": dag_run_id,
                                "task_id": "default_quessionaire",
                                "xcom_key": "answers"
                                }

                        url = f"http://localhost:8080/api/v1/dags/{data['dag_id']}/dagRuns/{data['dag_run_id']}/taskInstances/{data['task_id']}/xcomEntries/{data['xcom_key']}"
                        # TESTING
                        # st.write(url, data)

                        response = requests.get(url = url, auth=('airflow2','airflow2'))
                        # st.write(response.json())

                        response_answers = response.json()['value']
                        st.write('Answers:')
                        st.json(response_answers)
                    else:
                        st.error(f'Airflow DAG failed!')


                else:
                    st.warning("Please upload a file or select an existing file from S3.")


# Run the Streamlit app
if __name__ == "__main__":
    main()

