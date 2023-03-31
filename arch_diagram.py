from diagrams import Diagram, Edge, Cluster
from diagrams.onprem.client import User, Users
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.aws.storage import SimpleStorageServiceS3 as s3
from diagrams.onprem.network import Nginx
from diagrams.onprem.database import PostgreSQL
from diagrams.oci.monitoring import Telemetry
from diagrams.custom import Custom

with Diagram("ASSIGNMENT-4", show=False, direction='LR'):
    user = Users("users")
    audiofile = Custom("Audio File", "./audiofile.png")
    textfile = Custom("Text File", "./textfile.png")
    datastorage = s3("AWS S3")

    with Cluster("Application Instance"):

        with Cluster("Services"):
            openai = Custom("Chat GPT", "./chatgpt.png")  

        with Cluster("Applications"):
            userfacing = Custom("Streamlit", "./streamlit.png")

        with Cluster("Batch Processing"):
            airflow = Airflow("Airflow") 
            whisper = Custom("Whisper", "./whisper.jpg")      
             

    
    # Defining Edges
    user >> Edge(label = "Creates") >> audiofile
    user >> Edge(label = "Login to Dashboard") >> userfacing
    user >> Edge(label = "Upload MP3 File") >> userfacing

    userfacing << Edge(label = "Strors MP3 file on S3") << datastorage    
    userfacing << Edge(label = "Fetches MP3 file from S3") << datastorage
    userfacing >> Edge(label = "Fetches Text file from S3") >> datastorage
    
    
    userfacing >> Edge(label = "Event Processing") >> airflow
    userfacing >> Edge(label = "Processes MP3 File") >> whisper
    whisper >> Edge(label = "Processses MP3 File and Creates")  >> textfile
    textfile >> Edge(label = "Stored in S3") >> datastorage

    openai << Edge(label = "Uses Text File to Answer Adhoc Questions") << userfacing

    airflow >> Edge(label = "Stores Transcribed Files to S3 Bucket") >> datastorage