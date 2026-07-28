import streamlit as st
import requests
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.tools.retriever import create_retriever_tool
from langchain.agents import create_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

DB_FAISS_PATH = "vectorestore/db_faiss"

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

@st.cache_resource
def load_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="openai/gpt-oss-120b",
        temperature=0.5,
        max_tokens=512
    )

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression, e.g. '25 * 4 + 10'."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Error evaluating expression: {e}"
    
@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for general knowledge questions (people, places, events, history)."""
    try:
        headers = {"User-Agent": "MediMindChatbot/1.0 (contact: chbilalrafique2@gmail.com)"}

        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 1,
        }
        
        r = requests.get(search_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        if not results:
            return "No Wikipedia results found."
        title = results[0]["title"]

        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        r2 = requests.get(summary_url, headers=headers, timeout=10)
        r2.raise_for_status()
        return r2.json().get("extract", "No summary available.")
    except Exception as e:
        return f"Wikipedia search failed: {e}"

@st.cache_resource
def create_agent_executor():
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": 3})
    
    retriever_tool = create_retriever_tool(
    retriever,
    name="document_search",
    description=(
        "Search the user's uploaded documents. These may include medical reference material "
        "AND other documents such as resumes/CVs, technical profiles, or general text. "
        "ALWAYS try this tool FIRST for any question, since the answer may exist in the uploaded documents."
    )
)


    tools = [retriever_tool,wikipedia_search , calculator]

    return create_agent(
        model=load_llm(),
        tools=tools,
        system_prompt=(
    "You are MediMind, a helpful assistant.\n"
    "- ALWAYS use the document_search tool FIRST for every question, regardless of topic.\n"
    "- If the documents contain a relevant answer, use it and mention it came from the uploaded documents.\n"
    "- If the documents don't contain the answer, THEN use Wikipedia for general knowledge, "
    "or the calculator for math.\n"
    "- Clearly state whether your answer came from the uploaded documents or from Wikipedia."
)
    )

def main():
    st.set_page_config(page_title="MediMind Chatbot", page_icon="🩺")
    st.title("🧠 MediMind Chatbot")
    st.markdown("Ask me anything — medical topics from your documents, or general knowledge or about the project owner")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    prompt = st.chat_input("Ask a question...")
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            try:
                agent = create_agent_executor()
                response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
                final_answer = response["messages"][-1].content

                st.chat_message("assistant").markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()