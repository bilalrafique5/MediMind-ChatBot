import os
import requests
import streamlit as st

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

load_dotenv()


# =========================
# Configuration
# =========================

DB_FAISS_PATH = "vectorestore/db_faiss"


# =========================
# Load Vector Store
# =========================

@st.cache_resource
def get_vectorstore():

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    return db


# =========================
# Load LLM
# =========================

@st.cache_resource
def load_llm():

    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="openai/gpt-oss-20b",
        temperature=0.5,
        max_tokens=512
    )


# =========================
# RAG Prompt
# =========================

SYSTEM_PROMPT = """
You are MediMind, a helpful medical assistant.

Use ONLY the information provided in the context to answer the user's question.

Rules:
- If the answer is available in the context, answer using that information.
- If the answer is not available in the context, say:
  "I couldn't find this information in the uploaded documents."
- Do not make up information.
- Do not use outside knowledge.
- Keep the answer clear and easy to understand.
- Start the answer directly without small talk.

Context:
{context}
"""


prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}")
])


# =========================
# Create RAG Chain
# =========================

@st.cache_resource
def create_rag_chain():

    db = get_vectorstore()

    retriever = db.as_retriever(
        search_kwargs={"k": 3}
    )

    document_chain = create_stuff_documents_chain(
        load_llm(),
        prompt
    )

    retrieval_chain = create_retrieval_chain(
        retriever,
        document_chain
    )

    return retrieval_chain


# =========================
# Wikipedia Search
# =========================

def wikipedia_search(query):

    try:

        headers = {
            "User-Agent": "MediMindChatbot/1.0"
        }

        search_url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 1
        }

        response = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        results = response.json().get(
            "query", {}
        ).get("search", [])

        if not results:
            return "No Wikipedia results found."

        title = results[0]["title"]

        summary_url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + title.replace(" ", "_")
        )

        response2 = requests.get(
            summary_url,
            headers=headers,
            timeout=10
        )

        response2.raise_for_status()

        return response2.json().get(
            "extract",
            "No summary available."
        )

    except Exception as e:

        return f"Wikipedia search failed: {e}"


# =========================
# Calculator
# =========================

def calculator(expression):

    try:

        return str(
            eval(
                expression,
                {"builtins": {}}
            )
        )

    except Exception as e:

        return f"Error calculating expression: {e}"


# =========================
# Streamlit App
# =========================

def main():

    st.set_page_config(
        page_title="MediMind Chatbot",
        page_icon="🩺"
    )

    st.title("🧠 MediMind Chatbot")

    st.markdown(
        "Ask questions about the uploaded medical documents."
    )


    # Chat history
    if "messages" not in st.session_state:

        st.session_state.messages = []


    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])


    # User input
    user_query = st.chat_input(
        "Ask a question..."
    )


    if user_query:

        # Show user message
        with st.chat_message("user"):

            st.markdown(user_query)

        st.session_state.messages.append({
            "role": "user",
            "content": user_query
        })


        # Generate answer
        with st.chat_message("assistant"):

            with st.spinner("Searching documents..."):

                try:

                    rag_chain = create_rag_chain()

                    response = rag_chain.invoke({
                        "input": user_query
                    })

                    answer = response["answer"]

                    st.markdown(answer)


                    # Show source documents
                    with st.expander("📚 Source Documents"):

                        documents = response.get(
                            "context",
                            []
                        )

                        if documents:

                            for i, doc in enumerate(
                                documents,
                                1
                            ):

                                st.markdown(
                                    f"**Document {i}**"
                                )

                                st.write(
                                    doc.page_content
                                )

                                st.divider()

                        else:

                            st.write(
                                "No source documents found."
                            )


                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })


                except Exception as e:

                    st.error(
                        f"An error occurred: {str(e)}"
                    )


    # Reset button
    if st.button("🔄 Reset Chat"):

        st.session_state.messages = []

        st.rerun()



if __name__ == "__main__":
    main()