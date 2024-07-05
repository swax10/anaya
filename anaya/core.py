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
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

class Anaya:
    """
    A class representing the Anaya assistant.

    Attributes:
        title (str): The title of the assistant.
        initial_message (str): The initial message displayed by the assistant.
        llm (Ollama): The language model used by the assistant.
        memory (ConversationBufferMemory): The memory used by the assistant.

    Methods:
        display_subheader(): Displays the assistant's title as a subheader.
        logging(): Sets up logging for the assistant.
        display_initial_message(): Displays the initial message of the assistant.
        extract_model_names(models_info): Extracts model names from models_info.
        create_vector_db(file_upload): Creates a vector database from a file upload.
        process_question(question, vector_db, selected_model): Processes a question using the assistant's language model and vector database.
        extract_all_pages_as_images(file_upload): Extracts all pages of a PDF file as images.
        delete_vector_db(file_id): Deletes a vector database.

    """
    def __init__(self, title, initial_message, model):
        """
        Initializes an instance of the Anaya assistant.

        Args:
            title (str): The title of the assistant.
            initial_message (str): The initial message displayed by the assistant.
            model (str): The model used by the assistant.

        """
        self.title = title
        self.initial_message = initial_message
        self.llm = Ollama(model=model)
        self.memory = ConversationBufferMemory()
        self.logging()

    def display_subheader(self):
        """
        Displays the assistant's title as a subheader.

        """
        st.subheader(self.title, divider="gray", anchor=False)

    def logging(self):
        """
        Sets up logging for the assistant.

        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def display_initial_message(self):
        """
        Displays the initial message of the assistant.

        """
        with st.chat_message("assistant"):
            st.markdown(self.initial_message)

    @st.cache_resource(show_spinner=True, hash_funcs={__name__ + ".Anaya": lambda _: None})
    def extract_model_names(self, models_info):
        """
        Extracts model names from models_info.

        Args:
            models_info (dict): Information about the models.

        Returns:
            tuple: The extracted model names.

        """
        self.logger.info("Extracting model names from models_info")
        model_names = tuple(model["name"] for model in models_info["models"])
        self.logger.info(f"Extracted model names: {model_names}")
        return model_names
    
    def create_vector_db(self, file_upload):
        """
        Creates a vector database from a file upload.

        Args:
            file_upload (FileUploader): The uploaded file.

        Returns:
            Chroma: The created vector database.

        """
        self.logger.info(f"Creating vector DB from file upload: {file_upload.name}")
        temp_dir = tempfile.mkdtemp()

        try:
            path = os.path.join(temp_dir, file_upload.name)
            with open(path, "wb") as f:
                f.write(file_upload.getvalue())
            self.logger.info(f"File saved to temporary path: {path}")
            
            loader = UnstructuredPDFLoader(path)
            data = loader.load()

            if not data:
                raise ValueError("No content extracted from the PDF file.")

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
            chunks = text_splitter.split_documents(data)
            self.logger.info("Document split into chunks")

            embeddings = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
            
            chroma_db_path = 'embeddings'
            collection_name = f"collection_{file_upload.name}"

            if os.path.exists(chroma_db_path):
                try:
                    vector_db = Chroma(persist_directory=chroma_db_path, embedding_function=embeddings)
                    existing_collections = vector_db._client.list_collections()
                    if collection_name in existing_collections:
                        self.logger.info(f"Vector embeddings for {file_upload.name} already exist in the Chroma DB.")
                        return Chroma(collection_name=collection_name, persist_directory=chroma_db_path, embedding_function=embeddings)
                    else:
                        self.logger.info(f"Vector embeddings for {file_upload.name} do not exist in the Chroma DB. Creating new embeddings.")
                except Exception as e:
                    self.logger.error(f"Error checking Chroma DB: {str(e)}")
            else:
                self.logger.info(f"Chroma DB directory does not exist. Creating new directory and embeddings for {file_upload.name}.")

            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=chroma_db_path
            )
            self.logger.info(f"Vector DB created for {file_upload.name}")

            return vector_db
        except Exception as e:
            self.logger.error(f"Error creating vector DB: {str(e)}")
            raise
        finally:
            shutil.rmtree(temp_dir)
            self.logger.info(f"Temporary directory {temp_dir} removed")


    def process_question(self, question, vector_db, selected_model):
        """
        Processes a question using the assistant's language model and vector database.

        Args:
            question (str): The question to process.
            vector_db (Chroma): The vector database.
            selected_model (str): The selected language model.

        Returns:
            str: The response generated by the assistant.

        """
        self.logger.info(f"Processing question: {question} using model: {selected_model}")
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
    
    def extract_all_pages_as_images(self, file_upload):
        """
        Extracts all pages of a PDF file as images.

        Args:
            file_upload (FileUploader): The uploaded PDF file.

        Returns:
            list: The extracted pages as images.

        """
        self.logger.info(f"Extracting all pages as images from file: {file_upload.name}")
        pdf_pages = []
        try:
            with pdfplumber.open(file_upload) as pdf:
                for page in pdf.pages:
                    try:
                        image = page.to_image()
                        pdf_pages.append(image.original)
                    except Exception as e:
                        self.logger.error(f"Error extracting page from PDF: {str(e)}")
            self.logger.info("PDF pages extracted as images")
        except Exception as e:
            self.logger.error(f"Error opening PDF file: {str(e)}")
        return pdf_pages

    
    def delete_vector_db(self, file_id):
        """
        Deletes a vector database.

        Args:
            file_id (str): The ID of the file associated with the vector database.

        """
        self.logger.info(f"Deleting vector DB for file: {file_id}")
        if file_id in st.session_state["vector_dbs"]:
            vector_db = st.session_state["vector_dbs"].pop(file_id)
            if vector_db:
                collection_name = f"collection_{file_id}"
                vector_db._client.delete_collection(collection_name)
                st.success(f"Collection for {file_id} deleted successfully.")
                self.logger.info(f"Vector DB for {file_id} deleted")
            else:
                st.error(f"No vector database found for {file_id}.")
                self.logger.warning(f"Attempted to delete vector DB for {file_id}, but none was found")
        else:
            st.error(f"No vector database found for {file_id}.")
            self.logger.warning(f"Attempted to delete vector DB for {file_id}, but it doesn't exist in session state")

    def run(self):
        self.display_subheader()
        self.display_initial_message()

        models_info = ollama.list()
        available_models = self.extract_model_names(models_info)

        col1, col2 = st.columns([1.5, 2])

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        if "vector_dbs" not in st.session_state:
            st.session_state["vector_dbs"] = {}

        if available_models:
            selected_model = col2.selectbox(
                "Pick a model available locally on your system ↓", available_models, key="model_select"
            )

        file_uploads = col1.file_uploader(
            "Upload multiple PDF files ↓", type="pdf", accept_multiple_files=True, key="file_uploader"
        )

        if file_uploads:
            for file_upload in file_uploads:
                file_id = file_upload.name
                try:
                    if file_id not in st.session_state["vector_dbs"]:
                        st.session_state["vector_dbs"][file_id] = self.create_vector_db(file_upload)
                    pdf_pages = self.extract_all_pages_as_images(file_upload)

                    if pdf_pages:
                        zoom_level = col1.slider(
                            f"Zoom Level for {file_id}", min_value=100, max_value=1000, value=700, step=50, key=f"zoom_{file_id}"
                        )

                        with col1:
                            with st.container(height=410, border=True):
                                for page_image in pdf_pages:
                                    st.image(page_image, width=zoom_level)
                    else:
                        st.warning(f"Unable to extract pages from {file_id}. The file may be corrupted or password-protected.")
                except Exception as e:
                    st.error(f"Error processing {file_id}: {str(e)}")


        delete_collection = col1.button("🗑️ Delete collections", type="secondary", key="delete_button")

        if delete_collection:
            for file_id in list(st.session_state["vector_dbs"].keys()):
                self.delete_vector_db(file_id)
            st.session_state["vector_dbs"] = {}
            st.rerun()

        with col2:
            message_container = st.container(height=500, border=True)

            for message in st.session_state["messages"]:
                avatar = "🤖" if message["role"] == "assistant" else "👤"
                with message_container.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Enter a prompt here...", key="chat_input"):
                try:
                    st.session_state["messages"].append({"role": "user", "content": prompt})
                    message_container.chat_message("user", avatar="👤").markdown(prompt)

                    if st.session_state["vector_dbs"]:
                        vector_db = next(iter(st.session_state["vector_dbs"].values()))
                        response = self.process_question(prompt, vector_db, selected_model)
                        st.session_state["messages"].append({"role": "assistant", "content": response})
                        message_container.chat_message("assistant", avatar="🤖").markdown(response)
                    else:
                        st.error("Please upload a PDF file first.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
