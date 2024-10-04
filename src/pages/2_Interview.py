import streamlit as st
import time
from interview_service import InterviewService

st.title("Interview Chatbot")

if 'service' not in st.session_state:
    st.error("Invalid Session !")
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

text = ""
def stream_fn(stream):
    global text
    text = ""
    for chunk in stream:
        text += chunk
        yield chunk
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
    st.session_state.user_input = ""
    
    st.session_state.chat_history.append({"role": "ai", "content": bot_response})
    chats()

