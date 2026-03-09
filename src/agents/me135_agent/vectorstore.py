import os
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.settings import get_settings
from src.document_loaders.lecture_document_loader import LectureDocumentLoader

settings = get_settings()
embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
vector_store = AstraDBVectorStore(
    collection_name="me135_lecture",
    embedding=embeddings,
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
)

if __name__ == "__main__":

    loader = LectureDocumentLoader(
        root=r"assets/ME135Lecture",
        metadata={"course": "ME135_Transport_Phenomena", "professor": "Sundar"},
    )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)
    _ = vector_store.add_documents(documents=all_splits)
