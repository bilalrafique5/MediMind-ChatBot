
# 🧠 MediMind - Medical Chatbot

MediMind is an AI-powered medical chatbot that uses **LangChain**, **FAISS**, and **Groq LLM** to answer medical questions based on uploaded PDF documents. It supports **RAG (Retrieval-Augmented Generation)** and offers a friendly chat interface via **Streamlit**.

---

## 🔧 Features

- 🧾 Load and chunk PDF documents
- 🔍 Search using FAISS vector store
- 🤖 LLM-powered answers using `llama3-8b-8192` via Groq API
- 🧠 Custom prompt template for medical accuracy
- 💬 Interactive chat UI with memory
- 🔐 `.env` based API key security

---

## 📁 Project Structure



medical-chatbot/
├── data/                       # Folder for raw medical PDFs
├── vectorestore/db\_faiss/     # Vector database (FAISS)
├── medicalbot.py              # Streamlit chatbot interface
├── connect\_memory\_with\_llm.py # CLI interface to test chatbot
├── vector\_create.py           # Loads, chunks, embeds PDFs
├── .env                       # Contains API keys (not pushed)
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


### 4. Generate Vector Store


pipenv run python vector_create.py


### 5. Run Streamlit App
pipenv run streamlit run medicalbot.py



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


