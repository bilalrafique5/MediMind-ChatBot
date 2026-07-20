from dotenv import load_dotenv
load_dotenv()

import os
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

def load_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.5,
        max_tokens=512
    )

SYSTEM_PROMPT = (
    "Use the pieces of information provided in the context to answer the user's question.\n"
    "If you don't know the answer, just say that you don't know. Do not try to make up an answer.\n"
    "Do not provide anything outside the given context.\n\n"
    "Context:\n{context}\n\n"
    "Start the answer directly. No small talk, please."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

DB_FAISS_PATH = "vectorestore/db_faiss"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={"k": 3})

document_chain = create_stuff_documents_chain(load_llm(), prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

user_query = input("Write Query here: ")
response = retrieval_chain.invoke({"input": user_query})

print("\nRESULT:\n", response["answer"])
print("\nSOURCE DOCUMENTS:\n")
for i, doc in enumerate(response["context"], 1):
    print(f"--- Document {i} ---")
    print(doc.page_content)
    print()