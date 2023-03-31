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
from datetime import datetime, timedelta
from decouple import config

# DEV or PROD
environment = 'PROD'
if environment == 'DEV':
    webserver = 'localhost:8080'
elif environment == 'PROD':
    webserver = 'airflow-airflow-webserver-1:8080'


# AWS LOG KEYS
log_aws_access_key_id = config('log_aws_access_key_id')
log_aws_secret_access_key = config('log_aws_secret_access_key')

# create a client for logs
clientlogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id=log_aws_access_key_id,
                        aws_secret_access_key=log_aws_secret_access_key)


# Set the title of the app
st.title("Analytics Dashboard")
st.write('This dashboard shows key usage statistics for the app.')

# Enter Password to Access Batch Functionality
password = st.text_input("Enter Password:")

if password != '':
    if password == 'damgadmin': 
    
        # ######################################################################################################
        # TODO: 100 MOST RECENT EVENTS, WILL NEED TO LOOP THROUGH

        url = f"http://{webserver}/api/v1/eventLogs?limit=1"

        response = requests.get(url=url, auth=('airflow2', 'airflow2'))

        data = response.json()
        total_airflow_events = data['total_entries']
        st.write(f"Total Events from Airflow: {total_airflow_events}")

        # total_airflow_events = 1980
        data = []
        for i in range(0, int(total_airflow_events/100) + 1):
            url = f"http://{webserver}/api/v1/eventLogs?offset={i*100}"
            print(url)
            response = requests.get(url=url, auth=('airflow2', 'airflow2'))
            if response.status_code == 200:
                data += response.json()['event_logs']
       
        # event_df = pd.json_normalize(data, record_path =['event_logs'])
        event_df = pd.json_normalize(data)
        st.write(event_df)

        # User Requests Over Time
        st.header('Requests Over Time')
        summary = event_df.loc[(event_df['dag_id'].isin(['audio_transcription', 'audio_transcription_batch'])) & (event_df['event'].isin(['failed', 'success'])),
                    ['dag_id','event','execution_date']]
        # summary['execution_date'].dt.date
        st.write(summary.drop_duplicates())

        counts = summary.drop_duplicates().groupby(['dag_id','event','execution_date']).size().reset_index(name='counts')
        st.write(counts)

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


        #############################################################################
        # CUSTOM QUESTION HISTORY FROM CLOUD WATCH
        query = """
        fields @timestamp, @message | filter @message like /Custom_Question/ | sort @timestamp desc | limit 25
        """

        log_group = 'assignment4-log-group'

        start_query_response = clientlogs.start_query(
            logGroupName=log_group,
            startTime=int((datetime.today() - timedelta(days=5)).timestamp()),
            endTime=int(datetime.now().timestamp()),
            queryString=query,
        )
        # start_query_response

        query_id = start_query_response['queryId']

        response = None

        while response == None or response['status'] == 'Running':
            print('Waiting for query to complete ...')
            time.sleep(1)
            response = clientlogs.get_query_results(
                queryId=query_id
            )

        data = response['results']

        message_records = []
        for record in data:
            # convert dictionary string to dictionary
            # st.write(type(eval(record[1]['value'])))
            record_dict = eval(record[1]['value'])
            message_records.append(record_dict)

        # message_records
        log_df = pd.DataFrame(message_records)
        st.header('CloudWatch Records of Custom Question History (25 Most Recent):')
        st.write(log_df.head(25))
        # ######################################################################################################
        
    else:
        st.error("You don't have permission to access this functionality")

