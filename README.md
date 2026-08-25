
# 🧠 MediMind - Medical Chatbot

MediMind is an AI-powered medical chatbot that uses **LangChain**, **FAISS**, and **Groq LLM** to answer medical questions based on uploaded PDF documents. It supports **RAG (Retrieval-Augmented Generation)** and offers a friendly chat interface via **Streamlit**.

---

## 🔧 Features

- 🧾 Load and chunk PDF documents
- 🔍 Search using FAISS vector store
- 🤖 LLM-powered answers using `llama3-8b-8192` via Groq API
- 🧠 Custom prompt template for medical accuracy
- 💬 Interactive chat UI with memory
- 🛒 Agentic medicine catalog with 200 dummy medicines
- 📦 Session-based cart, stock validation, checkout, and order confirmation
- 📧 Automated Email Notifications with branded HTML invoice attachment & live preview
- 📱 SMS Notifications dispatched on order completion
- 📄 Direct download of official HTML Invoice (`.html`)
- 🔎 Symptom-aware catalog recommendations that can be added to the cart from chat
- 🔐 `.env` based API key security

---

## 📁 Project Structure



medical-chatbot/
├── data/                       # Folder for raw medical PDFs
├── vectorestore/db_faiss/     # Vector database (FAISS)
├── medicalbot.py              # Streamlit chatbot & checkout app
├── notification_service.py    # Email SMTP & SMS notification service
├── medicine_store.py          # Medicine catalog & order parser
├── connect_memory_with_llm.py # CLI interface to test chatbot
├── create_memory_for_llm.py   # Loads, chunks, embeds PDFs
├── .env                       # Contains API keys & credentials (not pushed)
├── .gitignore                 # Excludes .env and FAISS store
├── requirements.txt
└── README.md



---

## 💡 How It Works

1. Load PDFs from `data/`
2. Split text into chunks using `RecursiveCharacterTextSplitter`
3. Create vector embeddings with `sentence-transformers/all-MiniLM-L6-v2`
4. Store vectors in FAISS
5. Ask questions via Streamlit interface
6. Query runs through LangChain `RetrievalQA` + Groq LLM
7. Returns accurate answers with document sources
8. Place medicine order & receive instant Email Invoice, SMS notification, and HTML Invoice download


## 🚀 Getting Started

### 1. Clone the Repo

git clone https://github.com/Bilal-codes05/medical-chatbot.git
cd medical-chatbot


### 2. Install Dependencies


pip install -r requirements.txt


or with Pipenv:


pipenv install

### 3. Setup Environment

Create a `.env` file in the root:


GROQ_API_KEY=your_groq_api_key

# (Optional) Email Invoice SMTP Configuration:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=noreply@medimind.com

# (Optional) Twilio SMS Configuration:
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890


*Note: If SMTP or Twilio credentials are not configured, MediMind operates in **Simulated Notification Mode**—allowing seamless development without failing checkout.*

### 4. Generate Vector Store


pipenv run python vector_create.py


### 5. Run Streamlit App
streamlit run medicalbot.py

## Medicine store workflow

The Streamlit app has three views:

1. **Agent chat**: Ask about uploaded documents, describe a need such as “I have a headache”, or buy directly with a message such as “I want one paracetamol and two vitamin D tablets”. Recognized medicines are added to the cart automatically.
2. **Medicine catalog**: Search by medicine, category, or symptom, select a quantity, and add items to the cart.
3. **Cart and checkout**: Enter full name, phone number, email address, and delivery address. Upon placing an order, receive an instant Order ID, Email Invoice, SMS notification, live invoice preview, and downloadable `.html` invoice file.

The catalog is intentionally dummy data for demonstration. It is not connected to a payment provider or a real pharmacy inventory system, and recommendations do not replace advice from a qualified clinician.



## 🛡️ Notes

* **Your `.env` file is private**, never push it to GitHub.
* Ensure your PDF files are medically relevant and clean.
* You can switch the model or prompt template easily in code.

---

## 📜 License

This project is for educational and research purposes only. Please consult medical professionals for real advice.

---

## 👨‍💻 Author

Made with ❤️ by Muhammad Bilal Rafique
LinkedIn: linkedin.com/in/bilal-rafique5


