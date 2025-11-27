# ApolloQuiz – AI-Powered Quiz Generator
_Group Project – CCAI9024_

ApolloQuiz is a Django-based educational platform that generates quizzes from multimedia content such as YouTube videos, audio, PDFs, and images. The system extracts text, processes it, and uses DeepSeek LLM to generate structured quiz questions in JSON.

Deployed Live Link: http://3.25.220.94/

---

## 1. Features

- Upload YouTube URLs → automatic transcript extraction  
- Upload audio recordings → ElevenLabs speech-to-text  
- Upload PDF files → PyPDF2 text extraction  
- Upload images → Tesseract OCR  
- Combine multiple content sources for a single quiz  
- Fully configurable quiz generation settings  
- Generate questions using DeepSeek Chat Completions API  
- Modern UI with TailwindCSS and Element SDK  
- Works on local and cloud deployments (AWS, Ubuntu)

---

## 2. Installation

### 2.1. Clone Repository

```bash
git clone https://github.com/your_repo_here.git
cd ai_quiz_platform
```

### 2.2. Create and Activate Virtual Environment

**Windows (PowerShell):**

```bash
python -m venv venv
.env\Scriptsctivate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3. Install Dependencies

```bash
pip install -r requirements.txt
```

Included dependencies:

- Django 5.2.8  
- Django REST Framework  
- PyPDF2  
- pytesseract  
- openai-whisper  
- ElevenLabs API tools  
- youtube-transcript-api  
- requests  
- torch  
- And more listed in `requirements.txt`

---

## 3. Environment Variables

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_deepseek_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

These keys are required for quiz generation and audio transcription.

---

## 4. Running the Application

Run database migrations:

```bash
python manage.py migrate
```

Start Django server:

```bash
python manage.py runserver
```

Visit the app:

```text
http://127.0.0.1:8000
```

---

## 5. Demo Steps (User Flow)

### Step 1 — Upload Content

Go to:

```text
/upload/
```

Upload any:

- YouTube URL  
- Audio file  
- PDF file  
- Image file  

The backend extracts text and creates content IDs.

---

### Step 2 — Configure Quiz

Go to:

```text
/configure/
```

Configure:

- Title  
- Number of questions  
- Difficulty  
- Bloom taxonomy level  
- Question types  
- Topic focus  
- Custom instructions  

Click **Generate Quiz**.

---

### Step 3 — Loading Screen

You are redirected to:

```text
/quiz-loading/<quiz_id>
```

DeepSeek processes quiz generation.

---

### Step 4 — View Quiz

Go to:

```text
/quizzes/
```

Select your quiz to see:

- Questions  
- Choices  
- Answers  
- Explanations  

---

## 6. Technology Stack

### Backend
- Python 3.13  
- Django 5.2.8  
- Django REST Framework  
- SQLite (default)

### AI / ML
- DeepSeek Chat Completions API  
- ElevenLabs Speech-to-Text  
- openai-whisper (fallback STT)  
- Tesseract OCR  
- PyPDF2  
- YouTube Transcript API  

### Frontend
- TailwindCSS  
- Vanilla JavaScript  
- Element SDK  

### Deployment
- Ubuntu 22.04 LTS  
- AWS EC2 / Lightsail  
- Nginx  
- Gunicorn  
- Certbot SSL  

---

## 7. Reproducibility Notes

### Environment

- Deployed on Ubuntu 22.04 LTS (AWS)
- Local development: Windows or Ubuntu

### Frameworks & Language

- Python 3.13  
- Django 5.2.8  
- SQLite database  

### APIs Used

- DeepSeek (quiz generation)  
- ElevenLabs (audio transcription)  

### Content Extraction Tools

- PyPDF2 for PDFs  
- Tesseract OCR for images  
- YouTube Transcript API  
- Whisper as fallback STT  

### How to Reproduce

1. Clone repo  
2. Create virtual environment  
3. Install dependencies  
4. Add `.env` API keys  
5. Run migrations  
6. Start server  

Everything needed is included in `requirements.txt`.

---

## 8. Model and API Licenses

### DeepSeek API
- Used for quiz generation  
- URL: https://platform.deepseek.com  
- License: Proprietary (API-based)

### ElevenLabs API
- Used for speech-to-text  
- License: Proprietary  

### Whisper
- MIT License  

### Tesseract OCR
- Apache 2.0 License  

### PyPDF2
- BSD 3-Clause License  

---

## 9. Authors

- Deniz Jafarzadeh  
- (Add group members as needed)

---

## 10. Project License

This project is created for educational use within the **HKU CCAI9024** course.  
Not intended for commercial deployment.

---

## 11. Acknowledgements

- HKU CCAI9024 Teaching Team  
- DeepSeek  
- ElevenLabs  
- Django & Python communities  
- Tesseract OCR contributors  
- PyPDF2 maintainers  
