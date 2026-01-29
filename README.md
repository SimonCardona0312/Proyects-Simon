🪄 AI Transcription & Slide Creator
A modern AI-driven productivity tool built with Streamlit and Google Gemini.

This application automates the process of transforming audio recordings—including WhatsApp voice notes—into structured, editable PowerPoint presentations.

🌟 Project Overview
AI Transcription & Slide Creator is a web application designed to bridge the gap between spoken ideas and visual presentations. By combining state-of-the-art speech recognition with generative AI, it allows users to upload raw audio and receive a professional .pptx file in seconds.

The project emphasizes proactive AI analysis, where the system independently organizes content into logical slides without requiring explicit user instructions.

🚀 Project Goals
Automate content creation from audio sources.

Support mobile-first formats like WhatsApp .opus files.

Provide a proactive AI experience that structures information autonomously.

Deliver editable outputs in standard PowerPoint format.

Implement an immersive UI with animated visual feedback.

✨ Core Features
Multi-format Audio Support: Handles MP3, WAV, M4A, and high-compression OPUS files.

Proactive Intelligence: Automatically generates a minimum of 5 slides based on audio context.

Dynamic UI: Features a custom-styled interface with an animated "Magic" background.

Seamless Export: Generates real .pptx files using in-memory buffering for speed and security.

🛠️ Technologies & Tools

Technology,Purpose
Python,Core programming language
Streamlit,Web interface and deployment
OpenAI Whisper,High-precision audio transcription
Google Gemini 1.5,Generative AI for content structuring
python-pptx,Programmatic PowerPoint generation
FFmpeg,Backend audio codec processing
CSS Injection,UI customization and animated backgrounds
🧠 Software Architecture & Workflow
The application follows a linear processing pipeline to ensure data integrity and performance:

1. Audio Processing (The Ear)
The app utilizes FFmpeg at the system level to decode various audio formats. Once decoded, OpenAI Whisper transcribes the speech into raw text, handling background noise and multiple languages.

2. Cognitive Analysis (The Brain)
The raw text is fed into Google Gemini. We implemented a "Proactive Prompt" strategy: the AI is instructed to bypass the need for user commands, instead focusing on identifying key themes and dividing them into structured sections marked by unique anchors.

3. Document Synthesis (The Hand)
The structured response is parsed by the python-pptx engine. It creates a presentation object in the server's RAM (using BytesIO), maps each AI-generated section to a new slide, and prepares the binary stream for an instant download.

📂 Project Structure
Aplication.py: Main entry point containing the UI logic and API integrations.

requirements.txt: Python dependency management.

packages.txt: System-level dependencies for audio processing.

README.md: Project documentation.

Developed by Simón | Leveraging AI to make information more accessible and organized.
