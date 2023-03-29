FROM python:3.10.6

WORKDIR /app

COPY streamlit/main.py /app/

COPY requirements.txt /app/

COPY streamlit/pages /app/pages

#COPY ./ /app/requirements.txt

RUN pip install -r requirements.txt



CMD ["streamlit", "run", "main.py"]