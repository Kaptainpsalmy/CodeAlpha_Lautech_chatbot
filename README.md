# 🎓 LAUTECH Smart Assistant - FAQ Chatbot

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-black)

An intelligent FAQ chatbot for LAUTECH (Ladoke Akintola University of Technology) students and aspirants. Built with Flask and modern NLP techniques, this chatbot provides instant answers about admissions, school fees, accommodation, academic programs, and campus life.

![Chatbot Demo](screenshots/chat-demo.png)

## ✨ Features

### 🤖 Smart Chat Interface
- **Real-time responses** with typing indicators
- **Dark mode UI** with teal user bubbles and electric blue accents
- **Text-to-speech** for accessibility
- **Copy to clipboard** functionality
- **Suggested questions** for quick access
- **Auto-scroll** to new messages

### 🧠 Advanced NLP Matching
- **TF-IDF vectorization** for semantic understanding
- **Cosine similarity** for accurate matching
- **Custom mappings** for common questions
- **Fuzzy matching** for typos (e.g., "medcine" → "medicine")
- **Confidence scoring** (0-100%)
- **Fallback handlers** for greetings and common queries

### 📊 Admin Dashboard
- **Secure login** with JWT authentication
- **Dashboard overview** with statistics
- **Unknown questions** management
- **FAQ CRUD operations** (Create, Read, Update, Delete)
- **Bulk import/export** of FAQs
- **Analytics** on chatbot usage

### 🔄 Learning System
- **Logs unknown questions** automatically
- **Admin can add answers** to improve the bot
- **Real-time index refresh** after updates
- **Tracks unanswered questions** for improvement

### 🚀 Production Ready
- **Deployed on Vercel** (serverless)
- **PostgreSQL database** (Neon)
- **Environment variable** configuration
- **CORS enabled** for frontend access
- **Responsive design** for all devices

## 🛠️ Tech Stack

### Backend
- **Python 3.9** - Core language
- **Flask 2.3.3** - Web framework
- **scikit-learn 1.5.2** - TF-IDF vectorization & cosine similarity
- **NLTK 3.9.1** - Text preprocessing (tokenization, stopwords)
- **PostgreSQL** - Production database (via Neon)
- **SQLite** - Development database
- **JWT** - Authentication
- **Gunicorn** - WSGI server

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with dark mode
- **JavaScript** - Interactive features
- **Font Awesome** - Icons
- **Chart.js** - Admin dashboard charts

### DevOps
- **Git** - Version control
- **GitHub** - Repository hosting
- **Vercel** - Deployment platform
- **Neon PostgreSQL** - Managed database

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Node.js (for Vercel CLI, optional)
- PostgreSQL (for production) or SQLite (for development)

## 🚀 Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Kaptainpsalmy/CodeAlpha_Lautech_chatbot.git
cd CodeAlpha_Lautech_chatbot

