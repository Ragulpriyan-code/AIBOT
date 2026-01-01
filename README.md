🤖 AIBOT – AI Chatbot with RAG (Groq + Django)

AIBOT is a document-aware AI chatbot built using Django, Retrieval-Augmented Generation (RAG), and Groq’s ultra-fast LLM inference.
It allows users to upload documents (PDF/DOCX/TXT) and ask intelligent questions grounded in those documents, all inside a modern neon dark UI.

🚀 Features

🔐 User authentication (Login / Signup / Logout)

💬 Multi-conversation chat support

📄 Upload documents (PDF, DOCX, TXT)

🧠 RAG-based document question answering

⚡ Groq-powered LLM (openai/gpt-oss-20b)

🌙 Neon blue dark-themed UI 

🗂️ Per-chat document context switching

🧹 Clean codebase with 9.9+ pylint score

🧪 Ready for deployment & scaling

🛠️ Tech Stack
Backend

Python 3.11

Django 5

PostgreSQL

Groq API

SentenceTransformers

PyPDF2 / python-docx

AI / RAG

Embeddings: all-MiniLM-L6-v2

Vector store: In-memory (SimpleVectorStore)

LLM: openai/gpt-oss-120b via Groq

Frontend

HTML5

CSS3 (Neon Dark Theme)

Vanilla JavaScript

📁 Project Structure
AIBOT/
│
├── chatbot/
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── loader.py
│   │   ├── rag_pipeline.py
│   │   └── vectorstore.py
│   ├── templates/
│   │   └── chatbot/
│   │       └── index.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── openai_client.py
│   └── tests.py
│
├── chatbotapp/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env.example
├── .gitignore
├── .pylintrc
├── manage.py
└── README.md

⚙️ Environment Setup
1️⃣ Clone the repository
git clone https://github.com/Ragulpriyan-code/AIBOT.git
cd AIBOT

2️⃣ Create & activate virtual environment
python -m venv myvenv
myvenv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Environment variables

Create a .env file:

GROQ_API_KEY=your_groq_api_key_here
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True


📌 Never commit .env to GitHub

5️⃣ Database setup (PostgreSQL)

Update settings.py:

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "chatbot_db",
        "USER": "postgres",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


Run migrations:

python manage.py makemigrations
python manage.py migrate

6️⃣ Create superuser
python manage.py createsuperuser

7️⃣ Run the server
python manage.py runserver


Open:

http://127.0.0.1:8000

🧠 How RAG Works (Simple)

User uploads a document

Document is chunked & embedded

Stored in vector store

User asks a question

Relevant chunks are retrieved

LLM answers using document + chat history

🧪 Code Quality

✔ Pylint configured with pylint-django

✔ Score: 9.9 / 10

✔ Clean imports & formatting

Run pylint:

$env:DJANGO_SETTINGS_MODULE="chatbotapp.settings"
pylint chatbot --rcfile=.pylintrc

🔒 Security Notes

.env is ignored via .gitignore

No API keys committed

Safe for public GitHub repositories

📌 Future Improvements

Persistent vector DB (FAISS / Chroma)

Streaming responses

Role-based access

Docker support

Cloud deployment (AWS / Railway / Render)

👨‍💻 Author

Ragul Priyan M
ML Data Annotator Analyst
AI • Full-Stack • RAG Systems

📍 Tamil Nadu, India

⭐ If you like this project

Give it a star ⭐ on GitHub — it really helps!
