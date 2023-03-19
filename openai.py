# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 15:45:36 2023

@author: j.videlefsky
"""

# https://platform.openai.com/docs/api-reference/making-requests
# https://medium.com/geekculture/a-simple-guide-to-chatgpt-api-with-python-c147985ae28
# openai\Scripts\activate.bat
# pip install openai

# Use model = gpt-3.5-turbo


import os
import openai
openai.organization = "org-eul6p1H8uwpL8y7vA5l8cy02"
openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.Model.list()


# WhisperAI
# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
# os.getcwd()
audio_file= open("openai/JV_AUDIO_EXAMPLE.wav", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)

# transcript
# transcript.text
transcription = transcript.text


# Clean String for Topic Summarization
# https://towardsdatascience.com/text-cleaning-for-nlp-in-python-2716be301d5d


# What is my conversation about?
summary_prompt = "Summarize the topic of following text in three words or less:"

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": summary_prompt + transcription}],
    temperature=0.7
)

chat_output = completion.choices[0].message.content.strip()
print(f'Topic of Conversation: {chat_output}')