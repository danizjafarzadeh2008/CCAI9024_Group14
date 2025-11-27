\# ApolloQuiz – AI-Powered Quiz Generator

\_Group Project – CCAI9024\_

ApolloQuiz is a Django-based educational tool that allows users to upload content — YouTube videos, audio recordings, PDFs, or images — and automatically generate quizzes using an LLM (DeepSeek). The app extracts and preprocesses text, sends it to the model, and returns structured quiz JSON that can be rendered into multiple question formats.

Deployed Live Link: http://3.25.220.94/

\---

\## 🧩 1. Features

\- Upload \*\*YouTube URLs\*\* → auto transcript extraction

\- Upload \*\*audio recordings\*\* → ElevenLabs speech-to-text

\- Upload \*\*PDFs or Images\*\* → PyPDF2 + Tesseract OCR extraction

\- Organize multiple content inputs into a single quiz

\- Fully configurable quiz generation settings:

\- Difficulty

\- Bloom’s taxonomy level

\- Question types (MCQ, FRQ, T/F, Cloze, etc.)

\- Topic focus

\- LLM-generated questions using \*\*DeepSeek Chat Completions API\*\*

\- Polished UI with Element SDK customization tools

\- Compatible with local and cloud deployments (AWS)

\---

\## 🚀 2. Installation

\### \*\*2.1. Clone the Repository\*\*

\`\`\`bash

git clone https://github.com/your\_repo\_here.git

cd ai\_quiz\_platform

2.2. Create & Activate Virtual Environment

Windows (PowerShell):

bash

Copy code

python -m venv venv

.\\venv\\Scripts\\activate

Mac/Linux:

bash

Copy code

python3 -m venv venv

source venv/bin/activate

2.3. Install Dependencies

bash

Copy code

pip install -r requirements.txt

Your requirements.txt includes:

Django 5.2.8

djangorestframework 3.16.1

openai-whisper

pytesseract

PyPDF2

requests

youtube-transcript-api

torch

and other helper libraries

🔐 3. Environment Variables (API Keys Required)

Create a .env file in the project root (same level as manage.py):

ini

Copy code

DEEPSEEK\_API\_KEY=your\_deepseek\_key\_here

ELEVENLABS\_API\_KEY=your\_elevenlabs\_key\_here

These keys are required for quiz generation and audio transcription.

▶️ 4. Running the App

Run migrations and start server:

bash

Copy code

python manage.py migrate

python manage.py runserver

Open the app in your browser:

cpp

Copy code

http://127.0.0.1:8000

🎬 5. Demo Steps (How to Use ApolloQuiz)

Step 1 — Upload Content

Go to:

bash

Copy code

/upload/

Upload any combination of:

YouTube URL

Audio file

PDF file

Image file

Processed content IDs appear below the upload pane.

Step 2 — Configure Quiz

Go to:

bash

Copy code

/configure/

Configure:

Title

Difficulty

Number of questions

Question types

Bloom level

Topic focus

Custom instructions

Click Generate Quiz.

Step 3 — Loading State

You will be redirected to:

bash

Copy code

/quiz-loading/

DeepSeek will generate the quiz.

The page auto-updates once complete.

Step 4 — View Quiz

Go to:

bash

Copy code

/quiz/

Quiz is shown with:

Questions

Choices

Explanations (if enabled)

📦 6. Technology Stack

Backend

Python 3.13

Django 5.2.8

Django REST Framework

SQLite

AI / ML

DeepSeek Chat Completions API (Quiz Generation)

ElevenLabs API (Audio Transcription)

Whisper (local fallback STT)

Tesseract OCR (for images)

PyPDF2 (PDF reader)

Frontend

TailwindCSS

Element SDK

Vanilla JS (fetch API)

Deployment

Ubuntu 22.04 LTS

AWS EC2 (Lightsail)

Nginx + Gunicorn

Certbot SSL

🧪 7. Reproducibility Notes

Environment and OS

Ubuntu 22.04 LTS server (AWS deployment)

Local development on Windows acceptable

Programming Language & Frameworks

Python 3.13

Django 5.2.8

SQLite (default Django database)

AI / API Components

DeepSeek API for quiz generation

ElevenLabs API for audio transcription

Content Extraction Tools

Whisper (for fallback STT)

PyPDF2 (PDF reading)

Tesseract OCR (image text extraction)

Dependency Installation

All libraries are provided in requirements.txt

Install via pip install -r requirements.txt

Running the App

Activate virtual environment

Run migrations

Use python manage.py runserver

Access at 127.0.0.1:8000

These steps are fully sufficient to reproduce the app on any compatible machine.

📜 8. Model / API Licenses

DeepSeek API

Purpose: LLM quiz generation

URL: https://platform.deepseek.com/

License: Proprietary (API-based access)

ElevenLabs API

Purpose: Speech-to-text

URL: https://elevenlabs.io/docs

License: Proprietary API

Tesseract OCR

License: Apache 2.0

Purpose: Image text extraction

PyPDF2

License: BSD 3-Clause

Purpose: PDF parsing

Whisper

License: MIT

Purpose: Audio transcription fallback

👥 9. Authors

Deniz Jafarzadeh

(Add other group members as needed)

📄 10. License

This project is created for educational use within the HKU CCAI9024 course.

Not intended for commercial deployment.

📝 11. Acknowledgements

We thank:

HKU CCAI9024 Teaching Team

DeepSeek

ElevenLabs

Django & Python open-source communities

Tesseract OCR & PyPDF2 contributors

yaml

Copy code

\---

If you want, I can also provide:

✅ A shorter README

✅ A version optimized for GitHub Pages

✅ A "Project Architecture Diagram" in Markdown or PNG

✅ A “How each module works” section for better documentation

Just tell me!

You said:

You just give me them as a text put all the things in .md format even the commands as well

ChatGPT said:

Here is everything rewritten strictly as plain text inside a .md code block, exactly how a README.md file should be written.

All headings, sections, commands, and content are fully rendered in Markdown format — no extra explanations, no comments, no mixing.

Copy–paste directly into README.md.

md

Copy code

\# ApolloQuiz – AI-Powered Quiz Generator

\_Group Project – CCAI9024\_

ApolloQuiz is a Django-based educational platform that generates quizzes from multimedia content such as YouTube videos, audio, PDFs, and images. The system extracts text, processes it, and uses DeepSeek LLM to generate structured quiz questions in JSON.

\---

\## 1. Features

\- Upload YouTube URLs → automatic transcript extraction

\- Upload audio recordings → ElevenLabs speech-to-text

\- Upload PDF files → PyPDF2 text extraction

\- Upload images → Tesseract OCR

\- Combine multiple content sources for one quiz

\- Fully configurable quiz generation settings

\- Generate questions with DeepSeek Chat Completions API

\- Modern UI with TailwindCSS and Element SDK

\- Supports local and cloud deployment (AWS, Ubuntu)

\---

\## 2. Installation

\### 2.1. Clone Repository

\`\`\`bash

git clone https://github.com/your\_repo\_here.git

cd ai\_quiz\_platform

2.2. Create and Activate Virtual Environment

Windows (PowerShell):

bash

Copy code

python -m venv venv

.\\venv\\Scripts\\activate

Mac/Linux:

bash

Copy code

python3 -m venv venv

source venv/bin/activate

2.3. Install Dependencies

bash

Copy code

pip install -r requirements.txt

Dependencies include:

Django 5.2.8

Django REST Framework

PyPDF2

pytesseract

openai-whisper

ElevenLabs tools

youtube-transcript-api

requests

torch

and others listed in requirements.txt

3\. Environment Variables

Create a .env file in the project root:

env

Copy code

DEEPSEEK\_API\_KEY=your\_deepseek\_key\_here

ELEVENLABS\_API\_KEY=your\_elevenlabs\_key\_here

These API keys are required for LLM quiz generation and audio transcription.

4\. Running the Application

Run migrations:

bash

Copy code

python manage.py migrate

Start the development server:

bash

Copy code

python manage.py runserver

Open the app in a browser:

cpp

Copy code

http://127.0.0.1:8000

5\. Demo Steps (User Flow)

Step 1 — Upload Content

Navigate to:

bash

Copy code

/upload/

Upload:

YouTube links

Audio recordings

PDFs

Images

The system extracts text and assigns content IDs.

Step 2 — Configure Quiz

Navigate to:

bash

Copy code

/configure/

Configure:

Quiz title

Number of questions

Difficulty

Question types

Bloom level

Topic focus

Custom instructions

Click Generate Quiz.

Step 3 — Loading Status

The system redirects to:

bash

Copy code

/quiz-loading/

DeepSeek processes the quiz until completed.

Step 4 — View Quiz

Navigate to:

bash

Copy code

/quizzes/

Then select the quiz to view:

Questions

Choices

Explanations

6\. Technology Stack

Backend

Python 3.13

Django 5.2.8

Django REST Framework

SQLite

AI / ML

DeepSeek Chat Completions API

ElevenLabs Speech-to-Text

openai-whisper (fallback STT)

Tesseract OCR

PyPDF2

Frontend

TailwindCSS

Vanilla JS

Element SDK

Deployment

Ubuntu 22.04 LTS

AWS EC2 / Lightsail

Nginx

Gunicorn

Certbot SSL

7\. Reproducibility Notes

Environment

App deployed on Ubuntu 22.04 LTS (AWS)

Local development on Windows or Ubuntu

Programming Language & Frameworks

Python 3.13

Django 5.2.8

SQLite database

APIs Used

DeepSeek API for quiz generation

ElevenLabs API for audio transcription

Libraries for Content Extraction

PyPDF2 for PDF

Tesseract OCR for images

YouTube Transcript API

Whisper (fallback STT)

Dependencies

Listed in requirements.txt

Install via pip install -r requirements.txt

Running

Activate virtual environment

Run migrations

Start using python manage.py runserver

Open in 127.0.0.1:8000

These steps are sufficient to fully reproduce the app.

8\. Model and API Licenses

DeepSeek

Used for quiz generation

API-based usage

Proprietary license

ElevenLabs

Used for audio transcription

Proprietary license

Whisper

MIT License

Tesseract OCR

Apache 2.0 License

PyPDF2

BSD 3-Clause License

9\. Authors

Deniz Jafarzadeh

Other group members (add names if required)

10\. Project License

This project is intended for educational use within the HKU CCAI9024 course.

Commercial use is not permitted.

11\. Acknowledgements

HKU CCAI9024 teaching team

DeepSeek

ElevenLabs

Django community

Tesseract OCR developers

PyPDF2 maintainers
