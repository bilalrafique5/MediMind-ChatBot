import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

DB_FAISS_PATH = "vectorestore/db_faiss"

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db

@st.cache_resource
def load_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.5,
        max_tokens=512
    )

def set_custom_prompt():
    system_prompt = (
        "Use the pieces of information provided in the context to answer the user's question.\n"
        "If you don't know the answer, just say that you don't know. Do not try to make up an answer.\n"
        "Do not provide anything outside the given context.\n\n"
        "Context:\n{context}\n\n"
        "Start the answer directly. No small talk, please."
    )
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

@st.cache_resource
def create_chain():
    llm = load_llm()
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": 3})
    prompt = set_custom_prompt()
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain

def main():
    st.set_page_config(page_title="MediMind Chatbot", page_icon="🩺")
    st.title("🧠 MediMind Chatbot")
    st.markdown("Ask me anything related to medical topics based on your uploaded documents.")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    prompt = st.chat_input("Ask a medical question...")
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            try:
                chain = create_chain()
                response = chain.invoke({"input": prompt})
                result = response["answer"]

                # LCEL retrieval chain returns retrieved docs under "context"
                sources = response.get("context", [])
                formatted_sources = ""
                for i, doc in enumerate(sources, 1):
                    source_name = doc.metadata.get('source', f'Document {i}')
                    formatted_sources += f"\n\n**Source {i}:** `{source_name}`"

                final_answer = f"{result}\n\n---\n**Sources:**{formatted_sources}" if sources else result

                st.chat_message("assistant").markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()