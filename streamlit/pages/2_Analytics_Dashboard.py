import os
import streamlit as st
import boto3
from dotenv import load_dotenv
import requests
import time
from main import check_dag_status
import json
import seaborn as sns
import pandas as pd

# DEV or PROD
environment = 'DEV'
if environment == 'DEV':
    webserver = 'localhost:8080'
elif environment == 'PROD':
    webserver = 'airflow-airflow-webserver-1:8080'


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
    
        # ######################################################################################################
        # TODO: 100 MOST RECENT EVENTS, WILL NEED TO LOOP THROUGH
        url = f"http://{webserver}/api/v1/eventLogs?limit=1000&order_by=-when"

        response = requests.get(url=url, auth=('airflow2', 'airflow2'))

        data = response.json()
        event_df = pd.json_normalize(data, record_path =['event_logs'])
        st.write(f'Total Events: {event_df.shape[0]}')
        st.write(event_df)

        # User Requests Over Time
        st.header('Requests Over Time')
        summary = event_df.loc[(event_df['dag_id'].isin(['audio_transcription', 'audio_transcription_batch'])) & (event_df['event'].isin(['failed', 'success'])),
                    ['dag_id','event','execution_date']]
        st.write(summary.drop_duplicates())

        # fig = plt.figure(figsize=(10, 4))
        # sns.lineplot(x='date', y='total_requests', hue='email', 
        #             data=df,
        #             markers=True).set(ylim=(0))
        # st.pyplot(fig)


        # ######################################################################################################
        # # Total Requests Over Time
        # # TODO: turn into bar graph where you can see the breakdown of success/failure request status
        # st.header('Usage Over Time')

        # query = f"""
        # select date(time_of_request) date, 
        #         count(distinct email) total_users,
        #         count(*) total_requests
        # from user_api 
        # group by date
        # """
        # df = pd.read_sql_query(query, conn)
        # # TESTING
        # # st.write(df.head())
        # # st.write(df.dtypes)

        # fig = plt.figure(figsize=(10, 4))
        # g = sns.lineplot(x=df.date, y=df.total_requests, color="g")
        # sns.lineplot(x=df.date, y=df.total_users, color="b", ax=g.axes.twinx())
        # g.legend(handles=[Line2D([], [], marker='_', color="g", label='total_requests'), 
        #                 Line2D([], [], marker='_', color="b", label='total_users')])

        # st.pyplot(fig)


        # ######################################################################################################
        
    else:
        st.error("You don't have permission to access this functionality")