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
s3_bucket_name = 'batch-assignment-4'

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# SEssion State Initialization
# if 'selected_file' not in st.session_state:
#     st.session_state.selected_file = ''

# if 'desired_output' not in st.session_state:
#     st.session_state.desired_output = ''

# if 'dag_executed' not in st.session_state:
#     st.session_state.dag_executed = False


# Set the title of the app
st.title("Analytics Dashboard")
st.write('This dashboard shows key usage statistics for the app.')

# Enter Password to Access Batch Functionality
password = st.text_input("Enter Password:")

if password != '':
    if password == 'damgadmin': 
        # Usage Graph
        st.write('Usage Graph:')
        
    else:
        st.error("You don't have permission to access this functionality")