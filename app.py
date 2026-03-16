import os
import json
from groq import Groq
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "llama-3.3-70b-versatile"

TONE_GUIDES = {
    "Formal":     "professional, polite, structured, no slang, appropriate for business or academic communication",
    "Friendly":   "warm, approachable, conversational, positive, casual but respectful",
    "Assertive":  "confident, direct, action-oriented, clear expectations, no hedging or filler words",
    "Apologetic": "sincere, empathetic, takes responsibility, offers resolution, humble and understanding",
}


def rewrite_email(draft: str, tone: str):
    if not draft.strip():
        return "Please paste a draft email first.", "", ""

    if not os.getenv("GROQ_API_KEY"):
        return "❌ API key not found. Please add GROQ_API_KEY to your .env file.", "", ""

    # --- Step 1: Rewrite ---
    rewrite_prompt = f"""You are an expert email communication coach.

Rewrite the following draft email in a {tone} tone ({TONE_GUIDES[tone]}).

Rules:
- Keep the core message and intent intact
- Only return the rewritten email — no explanation, no subject line prefix, no preamble
- Make it concise and natural sounding

Draft email:
\"\"\"
{draft}
\"\"\"

Rewritten email ({tone} tone):"""

    rewrite_response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": rewrite_prompt}],
    )
    rewritten = rewrite_response.choices[0].message.content.strip()

    # --- Step 2: Analyze ---
    analysis_prompt = f"""Analyze this email rewrite. Respond in raw JSON only — no markdown, no backticks, no extra text.

Return exactly this format:
{{
  "tone_match": "<Excellent / Good / Partial>",
  "key_change": "<one sentence describing the main change made>",
  "word_count": <integer>,
  "readability": "<Simple / Moderate / Advanced>"
}}

Original draft:
\"\"\"{draft}\"\"\"

Rewritten email:
\"\"\"{rewritten}\"\"\"
"""

    analysis_response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": analysis_prompt}],
    )
    analysis = {}
    try:
        raw = analysis_response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        analysis = json.loads(raw)
    except Exception:
        analysis = {
            "tone_match": "Good",
            "key_change": "Tone adjusted to match target style.",
            "word_count": len(rewritten.split()),
            "readability": "Moderate",
        }

    tone_match  = analysis.get("tone_match", "Good")
    key_change  = analysis.get("key_change", "")
    word_count  = analysis.get("word_count", len(rewritten.split()))
    readability = analysis.get("readability", "Moderate")

    stats = f"Tone match: {tone_match}  |  Words: {word_count}  |  Readability: {readability}"
    tip   = f"What changed: {key_change}"

    return rewritten, stats, tip


def clear_all():
    return "", "", "", "", "Formal"


# ── Gradio UI ──────────────────────────────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

* { box-sizing: border-box; }

body, .gradio-container {
    font-family: 'DM Sans', sans-serif !important;
    background: #F5F2EB !important;
}

.gradio-container {
    max-width: 900px !important;
    margin: 0 auto !important;
    padding: 40px 24px !important;
}

#header {
    text-align: center;
    margin-bottom: 36px;
}

#header h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 42px !important;
    font-weight: 400 !important;
    color: #1A1714 !important;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
    line-height: 1.1;
}

#header p {
    font-size: 15px;
    color: #6B6560;
    font-weight: 300;
}

.panel-box {
    background: #FFFFFF;
    border: 1px solid #E5E0D8;
    border-radius: 16px;
    padding: 24px;
}

label span {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #8C867F !important;
}

textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    border: 1.5px solid #E5E0D8 !important;
    border-radius: 12px !important;
    background: #FDFCFA !important;
    color: #1A1714 !important;
    padding: 14px !important;
    transition: border-color 0.2s !important;
    resize: vertical !important;
}

textarea:focus {
    border-color: #B8A898 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(184,168,152,0.15) !important;
}

.tone-radio .wrap {
    display: flex !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
}

.tone-radio label {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 8px 18px !important;
    border: 1.5px solid #E5E0D8 !important;
    border-radius: 99px !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    background: #FDFCFA !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #6B6560 !important;
    text-transform: none !important;
    letter-spacing: normal !important;
}

.tone-radio label:hover {
    border-color: #B8A898 !important;
    color: #1A1714 !important;
}

button.primary {
    font-family: 'DM Sans', sans-serif !important;
    background: #1A1714 !important;
    color: #F5F2EB !important;
    border: none !important;
    border-radius: 99px !important;
    padding: 12px 32px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.18s !important;
}

button.primary:hover { background: #3D3530 !important; }

button.secondary {
    font-family: 'DM Sans', sans-serif !important;
    background: transparent !important;
    color: #8C867F !important;
    border: 1.5px solid #E5E0D8 !important;
    border-radius: 99px !important;
    padding: 12px 24px !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
}

button.secondary:hover {
    border-color: #B8A898 !important;
    color: #1A1714 !important;
}

#stats textarea, #tip textarea {
    background: #F5F2EB !important;
    border: 1px solid #E5E0D8 !important;
    color: #6B6560 !important;
    font-size: 13px !important;
    border-radius: 10px !important;
}

.divider {
    border: none;
    border-top: 1px solid #E5E0D8;
    margin: 20px 0;
}

#footer {
    text-align: center;
    margin-top: 32px;
    font-size: 12px;
    color: #B8B2AA;
}
"""

with gr.Blocks(title="Email Tone Rewriter") as app:

    gr.HTML("""
    <div id="header">
        <h1>Email Tone Rewriter</h1>
        <p>Paste your draft · choose your tone · get a polished rewrite instantly</p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML('<div class="panel-box">')
            input_email = gr.Textbox(
                label="Your Draft Email",
                placeholder='e.g. "hey can u send the report asap need it today thanks"',
                lines=10,
                max_lines=20,
            )
            tone_selector = gr.Radio(
                choices=["Formal", "Friendly", "Assertive", "Apologetic"],
                value="Formal",
                label="Choose Tone",
                elem_classes=["tone-radio"],
            )
            with gr.Row():
                submit_btn = gr.Button("✦ Rewrite Email", variant="primary")
                clear_btn  = gr.Button("Clear", variant="secondary")
            gr.HTML('</div>')

        with gr.Column(scale=1):
            gr.HTML('<div class="panel-box">')
            output_email = gr.Textbox(
                label="Rewritten Email",
                placeholder="Your rewritten email will appear here…",
                lines=10,
                max_lines=20,
            )
            gr.HTML('<hr class="divider">')
            stats_box = gr.Textbox(
                label="Analysis",
                interactive=False,
                elem_id="stats",
                lines=1,
            )
            tip_box = gr.Textbox(
                label="What Changed",
                interactive=False,
                elem_id="tip",
                lines=2,
            )
            gr.HTML('</div>')

    submit_btn.click(
        fn=rewrite_email,
        inputs=[input_email, tone_selector],
        outputs=[output_email, stats_box, tip_box],
    )

    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[input_email, output_email, stats_box, tip_box, tone_selector],
    )

    gr.HTML("""
    <div id="footer">
        Powered by Groq · Llama 3.3 70B · Built with Gradio · Free to use · No data stored
    </div>
    """)

if __name__ == "__main__":
    app.launch(css=css)