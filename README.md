# Email Tone Rewriter

An NLP-powered tool that rewrites emails in your chosen tone using Groq's Llama 3.3 70B model.

## Tones Supported
- Formal
- Friendly
- Assertive
- Apologetic

## Tech Stack
- Python
- Gradio (UI)
- Groq API (Llama 3.3 70B)
- python-dotenv

## Setup

1. Clone the repo
   git clone https://github.com/YOUR_USERNAME/email-tone-rewriter.git
   cd email-tone-rewriter

2. Create virtual environment
   python -m venv venv
   venv\Scripts\activate

3. Install dependencies
   pip install -r requirements.txt

4. Add your API key
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY from console.groq.com

5. Run the app
   python app.py

## How it works
Paste your draft email → select a tone → get a polished rewrite instantly.
The app makes two LLM calls: one to rewrite, one to analyze the result.