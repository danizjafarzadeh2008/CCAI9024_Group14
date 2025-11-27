ApolloQuiz – AI-Powered Quiz Generation Platform

ApolloQuiz is a full-stack AI-driven platform for generating high-quality quizzes from YouTube videos, PDFs, uploaded audio, or images. The system extracts content, chunks it, and uses the DeepSeek LLM API to generate structured quizzes with explanations.

🚀 Features
Content Upload

YouTube URL ingestion (transcript or transcription)

Audio transcription via ElevenLabs Whisper

PDF text extraction

Image → OCR extraction

Automatic chunking and cleaning

Quiz Generation

DeepSeek LLM-based question creation

Multiple question types:

MCQ, FRQ, True/False, Reasoning, Cloze, Matching

Adjustable difficulty, number of questions, Bloom level

Optional custom instructions

Question regeneration and explanation generation

Backend

Django + Django REST Framework

Gunicorn application server

Nginx reverse proxy with long timeouts

Fully reproducible pipeline

Frontend

Pure HTML/CSS/JS

Tailwind (CDN)

LocalStorage-based state management

Clean, modern UI
