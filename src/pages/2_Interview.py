import streamlit as st
import time
from interview_service import InterviewService
import pyttsx3
import threading

st.title("Interview Chatbot")

if 'service' not in st.session_state or len(st.session_state.chat_history) == 0:
    st.error("Interview not started yet !")
    st.stop()

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

service: InterviewService= st.session_state.service
con = st.empty()

def chats():
    with con.container(height=600, border=0):
        for chat in st.session_state.chat_history:
            message = st.chat_message(chat["role"])
            message.write(chat["content"])
            
        global output_placeholder
        output_placeholder = st.empty()

chats()

def speak_text_in_thread(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)   
    engine.say(text)
    print(text)
    engine.runAndWait()

text = ""
def stream_fn(stream):
    global text
    text = ""
    for chunk in stream:
        # speak_text_in_thread(chunk.content)
        text += chunk.content
        yield chunk.content
        time.sleep(0.03)


if user_input := st.chat_input():
    st.session_state.chat_history.append({"role": "human", "content": user_input})
    chats()

    stream = service.interview_qna(user_input)
    msg = output_placeholder.chat_message('ai')
    msg.write_stream(stream_fn(stream))

    bot_response = text
    text = ""
    output_placeholder.empty()

    st.session_state.chat_history.append({"role": "ai", "content": bot_response})
    chats()

