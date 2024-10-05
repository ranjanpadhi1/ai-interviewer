import streamlit as st
from interview_service import InterviewService
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Interviewer")

if 'service' not in st.session_state:
    st.session_state['service'] = InterviewService()    

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

service: InterviewService = st.session_state.service

st.title("AI Interviewer")
st.caption("Upload Your Resume to start your virtual interview")

resume = st.file_uploader("Resume(.pdf)")
msg = st.empty()

emp_info = None
submit = None

if resume:
    msg.warning("Uploading resume . . .")
    emp_info = service.upload_resume(resume)

    if emp_info:
        msg.success("Upload successful !")
    else:
        msg.error("Upload failed, please try again !")

    if emp_info:
        msg.info(f"Hi {emp_info['name']}!")

        yoe = st.slider("YOE as per your CV, feel free to update it", value = emp_info['yoe'], max_value=30)
        company = st.text_input("Which company interview you want to mock?")
        interview_type = st.selectbox("Select Interview Type", options=["Coding", "System Design", "Behavioural"])
        submit = st.button("Start Interview")
    
        if submit:
            msg = st.empty()
            emp_info['yoe'] = str(yoe)
            emp_info['company'] = company
            emp_info['interview_type'] = interview_type
            emp_info['history'] = st.session_state.chat_history

            msg.warning("Starting Interview . . .")
            resp = service.start_interview(emp_info)
            st.session_state.chat_history.append({"role": "ai", "content": resp})

            msg.success("Navigate to Interview section to Start Interview")








