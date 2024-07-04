import streamlit as st
import logging
import os
import tempfile
import shutil
import pdfplumber
import ollama

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from typing import List, Tuple, Dict, Any, Optional
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

    def display_subheader(self):
        st.subheader(self.title, divider="gray", anchor=False)

    def logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.logger = logging.getLogger(__name__)
    
    def display_initial_message(self):
        with st.chat_message("assistant"):
            st.markdown(self.initial_message)

    @st.cache_resource(show_spinner=True, hash_funcs={__name__ + ".Anaya": lambda _: None})
    def extract_model_names(self, models_info: Dict[str, List[Dict[str, Any]]]) -> Tuple[str, ...]:
        """
        Extract model names from the provided models information.

        Args:
            models_info (Dict[str, List[Dict[str, Any]]]): Dictionary containing information about available models.

        Returns:
            Tuple[str, ...]: A tuple of model names.
        """
        self.logger.info("Extracting model names from models_info")
        model_names = tuple(model["name"] for model in models_info["models"])
        self.logger.info(f"Extracted model names: {model_names}")
        return model_names
    
    def create_vector_db(self, file_upload) -> Chroma:
        """
        Create a vector database from an uploaded PDF file.

        Args:
            file_upload (st.UploadedFile): Streamlit file upload object containing the PDF.

        Returns:
            Chroma: A vector store containing the processed document chunks.
        """
        self.logger.info(f"Creating vector DB from file upload: {file_upload.name}")
        temp_dir = tempfile.mkdtemp()

        path = os.path.join(temp_dir, file_upload.name)
        with open(path, "wb") as f:
            f.write(file_upload.getvalue())
            self.logger.info(f"File saved to temporary path: {path}")
            loader = UnstructuredPDFLoader(path)
            data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
        chunks = text_splitter.split_documents(data)
        self.logger.info("Document split into chunks")

        embeddings = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
        vector_db = Chroma.from_documents(
            documents=chunks, embedding=embeddings, collection_name="myRAG"
        )
        self.logger.info("Vector DB created")

        shutil.rmtree(temp_dir)
        self.logger.info(f"Temporary directory {temp_dir} removed")
        return vector_db
    def process_question(self, question: str, vector_db: Chroma, selected_model: str) -> str:
        """
        Process a user question using the vector database and selected language model.

        Args:
            question (str): The user's question.
            vector_db (Chroma): The vector database containing document embeddings.
            selected_model (str): The name of the selected language model.

        Returns:
            str: The generated response to the user's question.
        """
        self.logger.info(f"""Processing question: {
                    question} using model: {selected_model}""")
        llm = ChatOllama(model=selected_model, temperature=0)
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate 3
            different versions of the given user question to retrieve relevant documents from
            a vector database. By generating multiple perspectives on the user question, your
            goal is to help the user overcome some of the limitations of the distance-based
            similarity search. Provide these alternative questions separated by newlines.
            Original question: {question}""",
        )

        retriever = MultiQueryRetriever.from_llm(
            vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
        )

        template = """Answer the question based ONLY on the following context:
        {context}
        Question: {question}
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Only provide the answer from the {context}, nothing else.
        Add snippets of the context you used to answer the question.
        """

        prompt = ChatPromptTemplate.from_template(template)

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(question)
        self.logger.info("Question processed and response generated")
        return response
    
    @st.cache_data
    def extract_all_pages_as_images(_self, file_upload) -> List[Any]:
        """
        Extract all pages from a PDF file as images.

        Args:
            _self (Anaya): This argument will not be hashed.
            file_upload (st.UploadedFile): Streamlit file upload object containing the PDF.

        Returns:
            List[Any]: A list of image objects representing each page of the PDF.
        """
        _self.logger.info(f"Extracting all pages as images from file: {file_upload.name}")
        pdf_pages = []
        with pdfplumber.open(file_upload) as pdf:
            pdf_pages = [page.to_image().original for page in pdf.pages]
        _self.logger.info("PDF pages extracted as images")
        return pdf_pages


    
    def delete_vector_db(self,vector_db: Optional[Chroma]) -> None:
        """
        Delete the vector database and clear related session state.

        Args:
            vector_db (Optional[Chroma]): The vector database to be deleted.
        """
        self.logger.info("Deleting vector DB")
        if vector_db is not None:
            vector_db.delete_collection()
            st.session_state.pop("pdf_pages", None)
            st.session_state.pop("file_upload", None)
            st.session_state.pop("vector_db", None)
            st.success("Collection and temporary files deleted successfully.")
            self.logger.info("Vector DB and related session state cleared")
            st.rerun()
        else:
            st.error("No vector database found to delete.")
            self.logger.warning("Attempted to delete vector DB, but none was found")


    def run(self):
        self.display_subheader()
        self.logging()
        self.extract_model_names
        self.display_initial_message()

        models_info = ollama.list()
        available_models = self.extract_model_names(models_info)

        col1, col2 = st.columns([1.5, 2])

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        if "vector_db" not in st.session_state:
            st.session_state["vector_db"] = None

        if available_models:
            selected_model = col2.selectbox(
                "Pick a model available locally on your system ↓", available_models
            )

        file_upload = col1.file_uploader(
            "Upload a PDF file ↓", type="pdf", accept_multiple_files=False
        )

        if file_upload:
            st.session_state["file_upload"] = file_upload
            if st.session_state["vector_db"] is None:
                st.session_state["vector_db"] = self.create_vector_db(file_upload)
            pdf_pages = self.extract_all_pages_as_images(file_upload)
            st.session_state["pdf_pages"] = pdf_pages

            zoom_level = col1.slider(
                "Zoom Level", min_value=100, max_value=1000, value=700, step=50
            )

            with col1:
                with st.container(height=410, border=True):
                    for page_image in pdf_pages:
                        st.image(page_image, width=zoom_level)

        delete_collection = col1.button("⚠️ Delete collection", type="secondary")

        if delete_collection:
            self.delete_vector_db(st.session_state["vector_db"])

        with col2:
            message_container = st.container(height=500, border=True)

            for message in st.session_state["messages"]:
                avatar = "🤖" if message["role"] == "assistant" else "😎"
                with message_container.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Enter a prompt here..."):
                try:
                    st.session_state["messages"].append({"role": "user", "content": prompt})
                    message_container.chat_message("user", avatar="😎").markdown(prompt)

                    with message_container.chat_message("assistant", avatar="🤖"):
                        with st.spinner(":green[processing...]"):
                            if st.session_state["vector_db"] is not None:
                                response = self.process_question(
                                    prompt, st.session_state["vector_db"], selected_model
                                )
                                st.markdown(response)
                            else:
                                st.warning("Please upload a PDF file first.")

                    if st.session_state["vector_db"] is not None:
                        st.session_state["messages"].append(
                            {"role": "assistant", "content": response}
                        )

                except Exception as e:
                    st.error(e, icon="⛔️")
                    self.logger.error(f"Error processing prompt: {e}")
            else:
                if st.session_state["vector_db"] is None:
                    st.warning("Upload a PDF file to begin chat...")

