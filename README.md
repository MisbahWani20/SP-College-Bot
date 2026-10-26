# CUS AI Assistant

An AI-powered multilingual chatbot developed for **Cluster University Srinagar (CUS)** to provide students and visitors with quick, accessible information about the university, colleges, programmes, admissions, and other academic information.

## ✨ Features

* 🤖 **AI-Powered Chatbot** — Provides intelligent responses to university-related queries.
* 🌐 **Multilingual Support** — Allows users to interact with the chatbot in multiple languages.
* 🎙️ **Voice Input** — Users can ask questions using their voice.
* 🔊 **Voice Output** — The chatbot can read responses aloud.
* 🎓 **Programme Information** — Provides information about programmes, eligibility, duration, fees, admission, selection process, colleges, and departments.
* 🏫 **College Information** — Provides information about affiliated colleges, facilities, locations, principals, libraries, hostels, laboratories, and more.
* 📚 **University Information** — Provides general information about Cluster University Srinagar.
* 📝 **Admission Information** — Handles general admission-related queries such as application process, documents, deadlines, entrance requirements, and guidelines.
* 🔎 **Flexible Query Handling** — Supports different ways of asking the same question.
* 💬 **Interactive Chat Interface** — Clean and user-friendly web-based chatbot interface.
* 📱 **Responsive Design** — Designed to work across different screen sizes.

## 🛠️ Technologies Used

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### AI & Language Features

* Natural Language Processing
* Multilingual text processing
* Speech-to-Text
* Text-to-Speech

### Database

* SQLite
* Structured university, college, and programme knowledge

## 📂 Project Structure

```text
Ai_chatbot/
│
├── app.py
├── chatbot/
│   ├── intents.py
│   ├── programme_search.py
│   ├── programme_response.py
│   ├── college_search.py
│   ├── college_response.py
│   ├── general_admission.py
│   ├── knowledge_database.py
│   └── knowledge.db
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   └── js/
│
├── .gitignore
├── requirements.txt
└── README.md
```

> The exact structure may vary depending on the current project version.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Ai_chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add the required configuration values.

**Do not commit the `.env` file to GitHub.**

A `.env.example` file can be provided to show the required variables without exposing sensitive credentials.

### 5. Run the Application

```bash
python app.py
```

The application will start on the local Flask development server.

Open the displayed local URL in your browser.

## 💬 Example Queries

Users can ask questions such as:

```text
What programmes are offered by Cluster University Srinagar?

What is the eligibility for B.Ed?

What is the duration of M.Sc IT?

What is the fee for BCA?

Which colleges offer BBA?

How can I apply for admission?

What documents are required for admission?

```

The chatbot is designed to understand variations in how users phrase their questions.

## 🔐 Security

Sensitive configuration and credentials are stored using environment variables.


Never expose API keys, passwords, database credentials, or other private credentials in source code or public repositories.

## 🎯 Project Objective

The primary objective of the CUS AI Assistant is to make university information more accessible through a conversational interface.

Instead of navigating through multiple webpages, users can ask questions naturally and receive relevant information through **text and voice-based interaction**.

## 🔮 Future Enhancements

* Improved conversational context and follow-up questions
* Additional language support
* More advanced NLP capabilities
* Integration with official university notifications
* Improved speech recognition
* Enhanced accessibility features
* Deployment on the official university website
* Continuous expansion of the university knowledge base

## 👩‍💻 Development

This project was developed as an **M.Sc. IT final-year project** with the aim of applying AI and web technologies to improve access to university information.

## 📄 Disclaimer

This chatbot is intended to assist users in finding university-related information. Information provided by the chatbot should be verified against official Cluster University Srinagar notifications and publications for important academic or admission decisions.

---
---

## 👩‍💻 Developed By

**Iqra Bashir & Misbah Wani**  
M.Sc. IT — Final Year  
Cluster University Srinagar

---


**CUS AI Assistant**
*Making university information easier to access through AI.*
