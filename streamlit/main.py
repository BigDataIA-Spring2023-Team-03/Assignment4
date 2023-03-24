# import os
# import streamlit as st
# import boto3
# from dotenv import load_dotenv

# # Load the environment variables from the .env file
# load_dotenv()

# # Get the AWS access key ID and secret access key from the environment variables
# aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
# aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

# # Get the S3 bucket name and region from the environment variables
# s3_bucket_name = os.environ.get("S3_BUCKET_NAME")

# # Create an S3 client
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
# )

# # Define the Streamlit app
# def main():
#     # Set the title of the app
#     st.title("MP3 Uploader to S3 Bucket")

#     # Create a file uploader
#     mp3_file = st.file_uploader("Choose an MP3 file")

#     # Check if a file was uploaded
#     if mp3_file is not None:
#         # Get the file name and size
#         filename = mp3_file.name
#         filesize = mp3_file.size

#         # Print the file name and size
#         st.write("File name:", filename)
#         st.write("File size:", filesize, "bytes")

#         # Upload the file to the S3 bucket
#         s3_client.upload_fileobj(mp3_file, s3_bucket_name, filename)

#         # Print a success message
#         st.write("File uploaded successfully!")
#     else:
#         # Print a message if no file was uploaded
#         st.write("No file uploaded")

# # Run the Streamlit app
# if __name__ == "__main__":
#     main()


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
    st.title("MP3 Uploader and Transcription")

    # Create a file uploader
    uploaded_file = st.file_uploader("Upload an MP3 file")

    # Create a dropdown to select an existing file from the S3 bucket
    s3_objects = s3_client.list_objects_v2(Bucket=s3_bucket_name)
    s3_files = [obj["Key"] for obj in s3_objects.get("Contents", [])]
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
                s3_client.upload_fileobj(uploaded_file, s3_bucket_name, filename)
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

                    response_transcript = convert_mp3_to_text_function(filename)
                    st.write("Transcript:", response_transcript)
                else:
                    st.warning("Please upload a file or select an existing file from S3.")


# Run the Streamlit app
if __name__ == "__main__":
    main()

