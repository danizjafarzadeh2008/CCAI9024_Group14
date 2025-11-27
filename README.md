# ApolloQuiz – AI-Powered Quiz Generation Platform

ApolloQuiz is a full-stack AI-powered quiz generation system that transforms **YouTube videos, audio recordings, PDFs, and images** into high-quality quizzes using the **DeepSeek LLM API**.  
It supports multiple question types, Bloom levels, difficulty selection, and rich customization.

Deployed Live Link: http://3.25.220.94/ 


---

## ✨ Features

### 🔹 Content Upload
- YouTube transcript extraction  
- Audio transcription (ElevenLabs Whisper API)  
- PDF text extraction  
- Image-to-text (OCR)  
- Chunking and text cleaning  
- Full database storage for reproducibility  

### 🔹 AI Quiz Generation
- Powered by **DeepSeek Chat Completion API**
- Supports MCQ, FRQ, True/False, Reasoning, Matching, Cloze
- Adjustable:
  - difficulty  
  - number of questions  
  - Bloom level  
  - topic focus  
- Custom instructions supported  
- Regenerate individual questions  
- Generate explanations for each question  

### 🔹 Frontend
- Clean UI with HTML + Tailwind (CDN)
- Uses localStorage for selected content
- No build tools required

### 🔹 Backend
- Django REST Framework
- Gunicorn app server
- Nginx reverse proxy
- Extended timeouts for long LLM responses

---

## 🛠 Tech Stack

| Component | Technology |
|----------|-----------|
| Backend Framework | Django 5.1 |
| API Layer | DRF |
| LLM | DeepSeek Chat API |
| Speech-to-Text | ElevenLabs Whisper |
| Server | Gunicorn |
| Reverse Proxy | Nginx |
| Database | SQLite (default) |
| Environment | Ubuntu 22.04 |
| Frontend | HTML, TailwindCSS (CDN), Vanilla JS |

---
