import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from medicine_store import (
    add_to_cart,
    add_medicine_order,
    cart_items,
    cart_total,
    checkout,
    get_catalog,
    recommend_medicines,
    search_medicines,
)

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
        model_name="openai/gpt-oss-20b",
        temperature=0.5,
        max_tokens=512,
    )


SYSTEM_PROMPT = """
You are MediMind, a helpful medical assistant.
Use ONLY the information provided in the context to answer the user's question.
If the answer is unavailable, say: "I couldn't find this information in the uploaded documents."
Do not make up information or use outside knowledge. Keep the answer clear and direct.

Context:
{context}
"""
prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("human", "{input}")])


@st.cache_resource
def create_rag_chain():
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": 3})
    document_chain = create_stuff_documents_chain(load_llm(), prompt)
    return create_retrieval_chain(retriever, document_chain)


def format_pkr(amount):
    return f"PKR {amount:,.0f}"


def initialize_state():
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("catalog", get_catalog())
    st.session_state.setdefault("cart", {})
    st.session_state.setdefault("pending_recommendations", [])
    st.session_state.setdefault("last_order", None)


def render_catalog():
    st.subheader("Find a medicine")
    st.caption("Search by name, category, or symptom. Prices are shown in Pakistani rupees.")
    with st.form("catalog_search"):
        search_query = st.text_input("Search medicines", placeholder="Try headache, vitamin, or paracetamol")
        categories = ["All"] + sorted({item["category"] for item in st.session_state.catalog})
        category = st.selectbox("Category", categories)
        submitted = st.form_submit_button("Search catalog", icon=":material/search:")
    if submitted:
        st.session_state.catalog_results = search_medicines(st.session_state.catalog, search_query, category)
    results = st.session_state.get("catalog_results", st.session_state.catalog[:20])
    st.caption(f"Showing {len(results)} result(s) | Select a quantity to add an item.")
    if not results:
        st.info("No medicines matched that search.", icon=":material/search_off:")
        return
    for medicine in results:
        with st.container(border=True):
            details, purchase = st.columns([3, 1], vertical_alignment="center")
            details.markdown(f"**{medicine['name']}**  \n{medicine['category']} | {medicine['manufacturer']}")
            details.write(medicine["description"])
            details.caption(f"{format_pkr(medicine['price_pkr'])} | {medicine['stock']} in stock")
            quantity = purchase.number_input(
                "Quantity", min_value=1, max_value=max(1, medicine["stock"]),
                value=1, key=f"quantity_{medicine['id']}"
            )
            if purchase.button("Add to cart", key=f"add_{medicine['id']}", icon=":material/add_shopping_cart:", width="stretch"):
                ok, message = add_to_cart(st.session_state.cart, medicine["id"], quantity, st.session_state.catalog)
                (st.success if ok else st.error)(message)


def render_cart():
    st.subheader("Review your order")
    st.caption("Confirm your items and delivery details before placing the order.")
    items = cart_items(st.session_state.cart, st.session_state.catalog)
    if not items:
        st.info("Your cart is empty. Add a medicine from the catalog or agent recommendations.", icon=":material/shopping_cart:")
        return
    for item in items:
        with st.container(border=True):
            item_details, item_total = st.columns([3, 1], vertical_alignment="center")
            item_details.markdown(f"**{item['name']}**")
            item_details.caption(f"Quantity {item['quantity']} | {item['category']}")
            item_total.markdown(
                f"<div style='text-align: right; font-weight: 600;'>"
                f"{format_pkr(item['total_pkr'])}</div>",
                unsafe_allow_html=True,
            )
    st.metric("Order total", format_pkr(cart_total(st.session_state.cart, st.session_state.catalog)))
    with st.form("checkout"):
        st.markdown("#### Delivery details")
        customer_name = st.text_input("Full name")
        phone = st.text_input("Phone number")
        address = st.text_area("Delivery address")
        place_order = st.form_submit_button("Place order", type="primary", icon=":material/check_circle:")
    if place_order:
        if not all(value.strip() for value in (customer_name, phone, address)):
            st.warning("Please complete your name, phone number, and delivery address.", icon=":material/warning:")
            return
        ok, message, order = checkout(st.session_state.cart, st.session_state.catalog)
        if ok:
            order["order_id"] = f"MM-{datetime.now():%Y%m%d%H%M%S}"
            st.session_state.last_order = order
            st.success(f"{message} Your order ID is {order['order_id']}.", icon=":material/check_circle:")
            st.rerun()
        st.error(message, icon=":material/error:")


def render_recommendations():
    recommendations = st.session_state.pending_recommendations
    if not recommendations:
        return
    with st.container(border=True):
        st.markdown("**Actionable recommendations**")
        st.caption("Catalog matches only. They do not replace advice from a qualified clinician.")
        for medicine in recommendations:
            left, right = st.columns([3, 1], vertical_alignment="center")
            left.write(f"{medicine['name']} - {format_pkr(medicine['price_pkr'])} ({medicine['stock']} in stock)")
            if right.button("Add", key=f"recommend_{medicine['id']}", icon=":material/add_shopping_cart:"):
                ok, message = add_to_cart(st.session_state.cart, medicine["id"], 1, st.session_state.catalog)
                (st.toast if ok else st.error)(message)


def render_chat():
    st.subheader("MediMind agent")
    st.caption("Type naturally. You can ask a question, request a suggestion, or buy medicines directly.")
    with st.container(border=True):
        st.markdown("**Try writing:** `I want one paracetamol and two vitamin D tablets`")
        st.caption("The medicines will be added to your cart automatically. Open the cart tab to checkout.")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    render_recommendations()
    user_query = st.chat_input("Ask a question or describe what you need...")
    if not user_query:
        return
    st.session_state.messages.append({"role": "user", "content": user_query})
    order_added, order_message = add_medicine_order(
        st.session_state.cart,
        user_query,
        st.session_state.catalog,
    )
    if order_added:
        answer = (
            f"{order_message} Your cart is ready. Open **Cart and checkout** "
            "to enter delivery details and place your order."
        )
        st.session_state.pending_recommendations = []
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
    recommendations = recommend_medicines(st.session_state.catalog, user_query)
    if recommendations:
        answer = "I found matching catalog options below. Review them and add one to your cart. I cannot diagnose conditions."
        st.session_state.pending_recommendations = recommendations
    else:
        try:
            answer = create_rag_chain().invoke({"input": user_query})["answer"]
        except Exception as error:
            answer = f"I couldn't complete the document search: {error}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()


def main():
    st.set_page_config(
        page_title="MediMind", page_icon=":material/medical_services:",
        layout="wide", initial_sidebar_state="expanded"
    )
    initialize_state()
    with st.sidebar:
        st.markdown("## MediMind")
        st.caption("A document-grounded health assistant with an actionable medicine store.")
        st.markdown("### How to use it")
        st.markdown("1. Describe a need in **Agent chat**.\n2. Review catalog matches.\n3. Add items and checkout.")
        st.caption("Recommendations are informational and do not replace a qualified clinician.")
        if st.button("Reset chat", icon=":material/refresh:", width="stretch"):
            st.session_state.messages = []
            st.session_state.pending_recommendations = []
            st.rerun()
    st.markdown("# MediMind")
    st.markdown("Your medical knowledge workspace and medicine companion.")
    st.space("small")
    total_items = sum(st.session_state.cart.values())
    metrics = st.columns(4)
    metrics[0].metric("Catalog", f"{len(st.session_state.catalog)} medicines")
    metrics[1].metric("In your cart", f"{total_items} item(s)")
    metrics[2].metric("Cart total", format_pkr(cart_total(st.session_state.cart, st.session_state.catalog)))
    metrics[3].metric("Status", "Ready", delta="Agent online")
    if st.session_state.last_order:
        order = st.session_state.last_order
        st.success(f"Order {order['order_id']} confirmed for {format_pkr(order['total_pkr'])}.", icon=":material/check_circle:")
    chat_tab, catalog_tab, cart_tab = st.tabs([
        ":material/chat: Agent chat", ":material/medication: Medicine catalog", ":material/shopping_cart: Cart and checkout"
    ])
    with chat_tab:
        render_chat()
    with catalog_tab:
        render_catalog()
    with cart_tab:
        render_cart()


if __name__ == "__main__":
    main()
