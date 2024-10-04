from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from prompts import emp_info_system, emp_info_user, interview_system, interview_start

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

class InterviewService:

    def __init__(self) -> None:
        print("Starting server....")
        self.setup()
        self.config={"configurable": {"session_id": "default_session"}}
        pass

    def setup(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.llm = ChatGroq(model="Gemma2-9b-It")    
        self.history = ChatMessageHistory()

    def load_file(self, file):
        temp_file_name = "uploaded_file.pdf"
        with open(temp_file_name, "wb") as tempfile:
            tempfile.write(file.getbuffer())

        documents = PyPDFLoader(temp_file_name).load()
        return documents
    
    def create_chunks(self, docs):
        sp = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        return sp.split_documents(docs)
    
    def retrieval_chain(self, prompt, output_parser):
        doc_chain = create_stuff_documents_chain(self.llm, prompt, output_parser = output_parser)
        retriever = self.vector_store.as_retriever()
        return create_retrieval_chain(retriever, doc_chain)

    def upload_resume(self, resume):
        self.documents = self.load_file(resume)
        self.chunks = self.create_chunks(self.documents)
        self.vector_store = FAISS.from_documents(self.chunks, self.embeddings)
        return self.extract_emp_info()

    def extract_emp_info(self):
        prompt = ChatPromptTemplate.from_template(emp_info_system)
        chain = self.retrieval_chain(prompt, JsonOutputParser())
        return chain.invoke({"input": emp_info_user})['answer']
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        return self.history
    
    def start_interview(self, emp_info):
        self.emp_info = emp_info
        prompt = ChatPromptTemplate.from_messages([
            ("system", interview_system),
            ("human", "{input}")
        ])

        rag_chain = prompt | self.llm | StrOutputParser()
        self.interview_chain = RunnableWithMessageHistory(rag_chain, self.get_session_history, input_messages_key="input", output_messages_key="answer")

        emp_info["input"] = interview_start
        return self.interview_chain.invoke(emp_info, self.config)
    
    def interview_qna(self, input):
        self.emp_info['input'] = input
        return self.interview_chain.stream(self.emp_info, self.config)
    



