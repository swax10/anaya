from anaya.core import Anaya
import streamlit as st

if __name__ == "__main__":
    title = "Anaya🔥📑"
    st.set_page_config(
            page_title=title,
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    anaya = Anaya(
            title=title,
            initial_message="Hello! I am **Anaya🔥**. How can I help you today?",
            model="llama3:8b"
        )
    anaya.run()