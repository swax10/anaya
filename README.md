# [Anaya🔥📑](https://swax10.github.io/anaya/): Multimodal Retrieval-Augmented Generation

Anaya is a Content Engine that specializes in analyzing and comparing multiple PDF documents. It uses Retrieval Augmented Generation (RAG) techniques to effectively retrieve, assess, and generate insights from the documents. 📊🔍

### [📄[Docs](https://swax10.github.io/anaya/docs/introduction).]

## Contents
- [TechStack](#techstack)
- [Install](#install)
- [Demo](#demo)
- [Output](#output)

# TechStack
💻 
Anaya utilizes a powerful tech stack to provide its functionalities:

- **Streamlit** 🌈: We leverage Streamlit to create an interactive web application that allows you to easily interact with Anaya's features.
- **Logging** 📝: We employ logging to record important events and errors during the execution of Anaya, ensuring smooth operation and easy troubleshooting.
- **OS** 🖥️: Anaya uses the OS module to interact with the underlying operating system, enabling seamless integration and file operations.
- **Tempfile** 📂: We utilize tempfile to create temporary files and directories, ensuring efficient and secure handling of data.
- **Shutil** 📁: Shutil provides high-level file operations, enabling Anaya to manipulate and manage files with ease.
- **Pdfplumber** 📄: Anaya leverages pdfplumber to extract text, images, and tables from PDF documents, enabling comprehensive analysis of the content.
- **Ollama** 🦙: Anaya incorporates Ollama, a powerful component for language and vision processing, to enhance its capabilities and provide accurate results.
- **Langchain Community** 🌐: We integrate various modules from Langchain Community, including document loaders, embeddings, text splitters, vector stores, prompts, output parsers, chat models, runnables, retrievers, LLMS, and memory management. This ensures a comprehensive and efficient language processing pipeline.
- **Chromadb** 🌈: Anaya utilizes Chromadb, a local disk-based vector store for word embeddings, to enhance its language understanding capabilities.
- **Dotenv** 🌐: We employ dotenv to load environment variables from a .env file, making configuration and deployment of Anaya easier.

With this robust tech stack, Anaya empowers you to unlock the full potential of your documents and gain valuable insights effortlessly. 🚀✨

Please note that the implementation and usage of these components are tailored specifically for Anaya, enabling seamless document analysis, language processing, and interactive web application development.

Let's dive into the world of Anaya and discover the possibilities together! 🌟💡🔎📚

# Install
To install Anaya🔥📑, follow these steps:

### 1. Clone the Repository
To clone the Anaya repository from GitHub, use the following command:
```bash
git clone https://github.com/swax10/anaya.git
```

### 2. Install Requirements
Once the repository is cloned, navigate to the **anaya** folder:
```bash
cd anaya
```
Then, run the following command to install the requirements:
```bash
pip install -e .
```

### 3. Run Streamlit App
To run Streamlit demo, use the following command:
```bash
streamlit run main.py
```
# Demo
https://github.com/swax10/anaya/assets/110764543/b1a4882c-b7f1-4573-80ec-6f0d9860123c

# Output
### Embedding
![Embedding](https://github.com/swax10/anaya/assets/110764543/ad2625b3-bab1-485a-b2b8-9ed8d304a830)

### Query Processing
![Query Processing](https://github.com/swax10/anaya/assets/110764543/33840a8f-1649-48b2-9bd0-770648d4f853)