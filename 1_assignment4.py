import streamlit as st
from streamlit_extras.switch_page_button import switch_page
# Utils
from Util.S3Util import *

#########################################
# Pages:
st.set_page_config(
    page_title="DAMG7245_Spring2023 Group 03",
    page_icon="👋",
)


s3Util = S3Util('damg7245-assignment4')

#########################################
# Upload File to S3:
uploaded_files = st.file_uploader("Choose a Audio file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
    # bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)
    # st.write(bytes_data)

    # Upload to S3
    # s3Util.upload_file(uploaded_file.name, 'Input_Audio_Files')