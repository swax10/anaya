from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Anaya:
    def __init__(self, title, initial_message, model):
        self.title = title
        self.initial_message = initial_message
        self.llm = Ollama(model=model)
        self.memory = ConversationBufferMemory()
    
    def display_title(self):
        st.title(self.title)

    def display_initial_message(self):
        with st.chat_message("assistant"):
            st.markdown(self.initial_message)

    def run(self):
        self.display_title()
        self.display_initial_message()

        # Initialize chat history if not already initialized
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Ask a question to Anaya🔥📑"):
            with st.chat_message("user"):
                st.markdown(prompt)

            st.session_state.messages.append({"role": "user", "content": prompt})
            
            response = self.llm.invoke(prompt)

            with st.chat_message("assistant"):
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
    

