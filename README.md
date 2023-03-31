# Live Application Link

# CodeLab Documentation
https://codelabs-preview.appspot.com/?file_id=1HVNaWkd4QOnp5tfxkyWu0S9DaV6LLmSpahldr8xvbUo

# Overview - Meeting Intelligence Application
This tool uses APIs (Whisper API and ChatGPT 3.5 turbo API) from OpenAI to take an audio file as input and transcribe it and
answer standard questions, user's custom questions based on the text. It uses Streamlit for the UI and Airflow for the automation.

# Components
## Streamlit - streamlit/ in the root path
Used Python Streamlit for the frontend of our application. The Streamlit application connects to Airflow via Airflow APIs. These APIs are used to trigger DAGs and pass through user input into the DAGs. The APIs are also used to get event logs from airflow and see the status of DAG runs.

### Page Layout:
>  **Main** - Adhoc Process, where a user can either select a local file to upload or a file from S3. <br>
>  **Batch Process** - Batch Process, where a user runs all files in the Batch folder through the process. <br>
>  **Analytics Dashboard** - This dashboard records different usage statistics for the app.
     Access is granted via a password known by the admins

## Airflow - airflow/ in the root path
The adhoc DAG starts by processing the audio file. From there, two tasks are generated. The first creates the transcript from the audio file and stores the transcript off into S3. The second takes the transcript, asks standard questions about the transcript, and records the resulting answers. These questions and answers are also stored off in S3. The batch DAG follows a similar process, but loops through the files in the input s3 folder.

### DAGS
1. audio_transcription (adhoc)
2. audio_transcription_batch

## Docker
Streamlit and Airflow have been dockerized and are connected on a single external network airflow_default

```
docker network create airflow_default
```


Dockerfile for the streamlit
```
FROM python:3.10.6

WORKDIR /app

COPY main.py /app/

COPY requirements.txt /app/

COPY pages /app/pages

COPY Logging /app/Logging

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "main.py"]
```

There are docker-compose files for both streamlit and airflow in their respective directories.

Docker Compose file for streamlit application
```
version: "3"
services:
 app:
   env_file:
     - .env
   container_name: frontend
   build:
     dockerfile: Dockerfile
   command: "streamlit run --server.port 8501 --server.enableCORS false main.py"
   ports:
     - "8501:8501"
   networks:
     - airflow_default
   image: frontend:latest

networks:
 airflow_default:
   external: true
```


Docker Compose file for airflow
- Fetch the docker compose file
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.5.1/docker-compose.yaml'
```


- Create required directories
```
mkdir -p ./dags ./logs ./plugins ./working_data
echo -e "AIRFLOW_UID=$(id -u)" > .env
```


- Update the following in the docker-compose file
```
# Do not load examples
AIRFLOW__CORE__LOAD_EXAMPLES: 'false'

# Additional python package
_PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:- pandas }

# Output dir
- ${AIRFLOW_PROJ_DIR:-.}/working_data:/opt/airflow/working_data

# Change default admin credentials
_AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow2}
_AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow2}
```
# Running Locally
Steps to install and run the application locally:
- Make sure to install the prerequisites - Docker Desktop, Git
  -- Clone the repository
```
git clone https://github.com/BigDataIA-Spring2023-Team-03/Assignment4.git 
```

- Change the directory to streamlit
```
cd streamlit
```
- Create virtual environment
```
python -m venv streamlit_venv
```

- Docker build and up
```
docker-compose build
docker-compose up
```

This will start the streamlit application in the port 8501
> http://localhost:8501/

- Open a new instance of terminal and change the directory to airflow
```
cd ../airflow
```

- Docker compose up for airflow
```
docker-compose up airflow-init
docker-compose up
```

This will start the airflow in the port 8080
> http://localhost:8080/

# Architecture Diagram
![Arch Diagram](https://github.com/BigDataIA-Spring2023-Team-03/Assignment4/blob/mani/arch_diagram.png)

# Attestation
WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT
AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK. <br>

### Contribution:
- member1: 25%
- member2: 25%
- member3: 25%
- member4: 25%






