#Author: Raj Mehta
#Description: Front end code for Audio Transcription
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
    st.title("MP3 Uploader to S3 Bucket")

    # Create a file uploader
    mp3_file = st.file_uploader("Choose an MP3 file")

    # Check if a file was uploaded
    if mp3_file is not None:
        # Get the file name and size
        filename = mp3_file.name
        filesize = mp3_file.size

        # Print the file name and size
        st.write("File name:", filename)
        st.write("File size:", filesize, "bytes")

        # Upload the file to the S3 bucket
        s3_folder = "audio_files/"
        s3_key = s3_folder + filename
        s3_client.upload_fileobj(mp3_file, s3_bucket_name, s3_key)

        # Print a success message
        st.write("File uploaded successfully!")
    else:
        # Print a message if no file was uploaded
        st.write("No file uploaded")



# Run the Streamlit app
if __name__ == "__main__":
    main()

