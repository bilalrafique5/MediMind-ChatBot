from langchain_community.document_loaders import PyPDFLoader,DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS




# Load Raw PDFs
DATA_PATH='data/'

def load_raw_documents(data):
     loader=DirectoryLoader(data,
                     glob="*.pdf",
                     loader_cls=PyPDFLoader,)
     document=loader.load()
     return document
 
documnts=load_raw_documents(data=DATA_PATH)
# print(f"Length of PDF Pages: {len(documnts)}")


# Create Chunks
def create_chunks(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks

chunk_size=create_chunks(extracted_data=documnts)
# print(f"Number of Chunks Created: {len(chunk_size)}")

# Create Vector Embeddings
def get_embedd_model():
    embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    return embedding_model

embeddig_model=get_embedd_model()


#  store embeddings in FAISS
DB_PATH="vectorestore/db_faiss"
db=FAISS.from_documents(chunk_size,embeddig_model)
db.save_local(DB_PATH)




