import time
import boto3
from decouple import config

log_aws_access_key_id = config('log_aws_access_key_id')
log_aws_secret_access_key = config('log_aws_secret_access_key')

# create a client for logs
clientlogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id=log_aws_access_key_id,
                        aws_secret_access_key=log_aws_secret_access_key)


# write logs
def write_logs(message : str):
    clientlogs.put_log_events(
    logGroupName="assignment4-log-group",
    logStreamName="assignment4-log-stream",
    logEvents = [
        {
            'timestamp': int(time.time() * 1e3),
            'message': message
        }
    ]
    )

# Test
# user_inputs = [prod_selected, year_selected, months_selected, days_selected, files_selected]
# user_inputs = ['prod_selected', 'year_selected', 'months_selected', 'days_selected', 'files_selected']
# url = 'test'
# write_logs(f'User Input: {user_inputs}')
# write_logs(f'Generated URL: {url}')