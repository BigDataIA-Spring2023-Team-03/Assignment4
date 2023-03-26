import os
import streamlit as st
import boto3
from dotenv import load_dotenv
import requests
import subprocess
from convert_mp3_to_text import convert_mp3_to_text_function


# Load the environment variables from the .env file
load_dotenv()

# Get the AWS access key ID and secret access key from the environment variables
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Get the S3 bucket name and region from the environment variables
s3_bucket_name = os.environ.get("S3_BUCKET_NAME")

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# Define the Streamlit app
def main():
    # Set the title of the app
    st.title("MP3 Transcription")

    # Create a dropdown to select an existing file from the S3 bucket
    s3_objects = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix="audio_files/")
    s3_files = [obj["Key"] for obj in s3_objects.get("Contents", [])]
    selected_file = st.selectbox("Select an existing file from S3", ["None"] + s3_files)

    # Check if both an uploaded file and an S3 file were selected
    if selected_file != "None":
        st.write("Please select a file")
        filename = selected_file
        # Print the file name and size
        st.write("File name:", filename)
        
    if st.button("Convert to transcript") and selected_file!= "None":
        response_transcript = convert_mp3_to_text_function(filename)
        st.write("Transcript:", response_transcript)

# Run the Streamlit app
if __name__ == "__main__":
    main()
