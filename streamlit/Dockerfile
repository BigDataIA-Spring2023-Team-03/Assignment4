FROM python:3.10.6

WORKDIR /app

COPY main.py /app/

COPY requirements.txt /app/

COPY pages /app/pages

COPY Logging /app/Logging

#COPY ./ /app/requirements.txt

RUN pip install -r requirements.txt



CMD ["streamlit", "run", "main.py"]