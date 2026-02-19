# LAUTECH FAQ Chatbot

A smart FAQ chatbot for LAUTECH students and aspirants. Answers questions about admissions, school life, fees, hostels, academic programs, and student affairs.

## Features

- 🤖 Smart FAQ matching using NLP
- 🎨 Dark mode UI with teal user bubbles
- 📋 Copy answers to clipboard
- 🔊 Text-to-speech for answers
- 💡 Suggested questions
- 📊 Admin dashboard to manage FAQs
- 🔄 Learns from unknown questions

## Tech Stack

- **Backend:** Python Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (development), PostgreSQL (production)
- **NLP:** scikit-learn, NLTK
- **Deployment:** Vercel

## Project Structure
lautech-chatbot/
├── backend/ # Flask API and NLP logic
├── frontend/ # HTML, CSS, JavaScript files
├── data/ # JSON data files
└── README.md

## Setup Instructions

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Run: `python backend/api/chat.py`

## Author

Built by Samuel for CodeAlpha Internship