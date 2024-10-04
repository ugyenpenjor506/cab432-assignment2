import os
import openai
import textwrap
import PyPDF2  # Import the PyPDF2 library
from flask import jsonify
from app.service.DatabaseService import DatabaseService
from app.helper.SecretManager import get_secrets
from langchain_openai import OpenAIEmbeddings  # For OpenAI embeddings
from langchain_community.vectorstores import Chroma  # For Chroma vector store
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain


# Retrieve OpenAI API Key securely from environment or secret manager
OPENAI_API_KEY = get_secrets()['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

class ApiService:
    
    @staticmethod
    def cpu_intensive_query_processing(response_text):
        """Simulate a CPU-intensive text processing task"""
        result = 0
        for _ in range(5000):
            result += sum(ord(char) for char in response_text)
            response_text = response_text[::-1]  # Reverse the text as a mock operation
        return result

    def openai_api(self, user_input, conversation_id, query_id):
        try:
            # Ensure the OpenAI API key is set
            if openai.api_key is None:
                return {"status": "error", "code": 500, "message": "OPENAI_API_KEY environment variable is not set."}

            # Load and process documents from a PDF file
            file_path = "experiment-dataset.pdf"
            if not os.path.exists(file_path):
                return {"status": "error", "code": 404, "message": f"File not found: {file_path}"}

            # Step 1: Extract text from the PDF
            text = self.extract_text_from_pdf(file_path)
            documents = self.prepare_documents(text)

            # Step 2: Create embeddings using Chroma and LangChain
            vector_store = self.create_embeddings(documents)

            # Step 3: Build the LangChain-based Retrieval-Augmented Generation (RAG) chatbot
            qa_chain = self.build_rag_chatbot(vector_store)

            # Step 4: Get the response from the chatbot
            response = qa_chain.run(user_input)
            response_text = str(response)

            # Perform CPU-intensive processing
            cpu_result = self.cpu_intensive_query_processing(response_text)

            # Format the response text for better readability
            line_width = 70
            wrapped_response = textwrap.fill(response_text, width=line_width)

            # Store the response in the database
            databaseService.create_response(conversation_id, query_id, response_text)

            # Return the formatted response and the result of CPU-intensive processing
            return {
                "status": "success",
                "code": 200,
                "response": wrapped_response,
                "cpu_result": cpu_result
            }

        except ValueError as e:
            return {"status": "error", "code": 500, "message": str(e)}

        except Exception as e:
            return {"status": "error", "code": 500, "message": f"An unexpected error occurred: {str(e)}"}

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    def prepare_documents(self, text):
        """Split the extracted text into chunks and convert them into Document objects"""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents

    def create_embeddings(self, documents):
        """Create vector embeddings using OpenAI and Chroma"""
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vector_store = Chroma.from_documents(documents, embeddings)
        return vector_store

    def build_rag_chatbot(self, vector_store):
        """Build the Retrieval-Augmented Generation (RAG) chatbot using LangChain"""
        # Initialize the OpenAI LLM
        llm = OpenAI(temperature=0.1, openai_api_key=OPENAI_API_KEY)

        # Create the document combination chain for question answering
        combine_documents_chain = load_qa_chain(llm, chain_type="stuff")

        # Build the RAG-based RetrievalQA chain
        qa_chain = RetrievalQA(retriever=vector_store.as_retriever(), combine_documents_chain=combine_documents_chain)

        return qa_chain

# Instantiate the services
apiService = ApiService()
databaseService = DatabaseService()
