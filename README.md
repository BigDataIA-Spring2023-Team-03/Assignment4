# Live Application Link

# CodeLab Documentation
https://codelabs-preview.appspot.com/?file_id=1HVNaWkd4QOnp5tfxkyWu0S9DaV6LLmSpahldr8xvbUo

# Overview - Meeting Intelligence Application
This tool uses APIs (Whisper API and ChatGPT 3.5 turbo API) from OpenAI to take an audio file as input and transcribe it and
answer standard questions, user's custom questions based on the text. It uses Streamlit for the UI and Airflow for the automation.

# Components
## Streamlit - streamlit directory in the root path
We have used Python Streamlit for the frontend of our application. The Streamlit application connects to Airflow via Airflow APIs. These APIs are used to trigger DAGs and pass through user input into the DAGs. The APIs are also used to get event logs from airflow and see the status of DAG runs.

  Page Layout:
  Main - Adhoc Process, where a user can either select a local file to upload or a file from S3
  Batch Process - Batch Process, where a user runs all files in the Batch folder through the process
  Analytics Dashboard - This dashboard records different usage statistics for the app.
    Access is granted via a password known by the admins
