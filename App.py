# ----------------------------------------------------------------------------------------------------------------------------------
# Libraries
import streamlit as st
import whisper
import os
import google.generativeai as GenAI
from pptx import Presentation
from io import BytesIO
from pptx.enum.text import MSO_AUTO_SIZE
import re

# ----------------------------------------------------------------------------------------------------------------------------------
# Page config
st.set_page_config(page_title="Gen", page_icon="🪄")

st.markdown("""
<h1 style="
    color: #FFFFFF;
    text-align: center;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.7);
">
🪄 Transcription and Slide Creator
</h1>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------------------------------------------------------
# Background image
Url_Imagen = "https://i.pinimg.com/originals/cf/a2/39/cfa239195d194b724a9d38362859a1af.jpg"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{Url_Imagen}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .main {{
        background-color: rgba(0, 0, 0, 0.45);
        padding: 20px;
        border-radius: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------------------------------------------------------------------------------------
# API KEY
GenAI.configure(api_key=st.secrets["API_KEY"])

# ----------------------------------------------------------------------------------------------------------------------------------
# PowerPoint function
def crear_pptx(texto_generado):
    prs = Presentation()

    pattern = r"---\s*SLIDE\s*\d+\s*---\s*(.*?)\s*(?=(?:---\s*SLIDE\s*\d+\s*---)|\Z)"
    slides = re.findall(pattern, texto_generado, flags=re.S)

    if not slides:
        slides = [s for s in re.split(r"---\s*SLIDE", texto_generado) if s.strip()]

    for slide_text in slides:
        lines = [l.strip() for l in slide_text.strip().splitlines() if l.strip()]
        if not lines:
            continue

        title = lines[0]

        notes_idx = None
        for i, ln in enumerate(lines[1:], start=1):
            if ln.lower().startswith("notes"):
                notes_idx = i
                break

        if notes_idx is not None:
            bullets_lines = lines[1:notes_idx]
            notes_lines = lines[notes_idx + 1:]
        else:
            bullets_lines = lines[1:]
            notes_lines = []

        bullets = [re.sub(r'^[\*\-\u2022•]+\s*', '', b) for b in bullets_lines]

        slide = prs.slides.add_slide(prs.slide_layouts[1])

        if slide.shapes.title:
            slide.shapes.title.text = title

        if len(slide.placeholders) > 1:
            tf = slide.placeholders[1].text_frame
            tf.clear()
            tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE

            if bullets:
                p = tf.paragraphs[0]
                p.text = bullets[0]
                p.level = 0

                for b in bullets[1:]:
                    p = tf.add_paragraph()
                    p.text = b
                    p.level = 0

        notes_text = "\n".join(notes_lines) if notes_lines else "\n".join(bullets)

        try:
            slide.notes_slide.notes_text_frame.text = notes_text
        except Exception:
            pass

    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()

# ----------------------------------------------------------------------------------------------------------------------------------
# Audio upload
Audio_fill = st.file_uploader(
    "Upload your audio so we can transcribe",
    type=["mp3", "mp4", "opus", "wav", "m4a"]
)

if Audio_fill is not None:
    st.subheader("🎧 Preview your audio")
    st.audio(Audio_fill)

    if Audio_fill.size > 10 * 1024 * 1024:
        st.error("The audio is too large. Max 10MB (~3 minutes).")
        st.stop()

    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())

    with st.spinner("Whisper is processing your audio..."):
        model = whisper.load_model("base")
        result = model.transcribe("temp_audio.mp3")

    st.success("Transcription success")

    with st.expander("Show transcription"):
        st.write(result["text"])

    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is creating your slides..."):
            model = GenAI.GenerativeModel("models/gemini-2.5-flash")

            instruction = f"""
Analyze the audio: {result['text']}

Generate slides using:
--- SLIDE N ---

Each slide:
Title
• Bullet
• Bullet

notes_slide:
Speaker notes
"""

            response = model.generate_content(instruction)

            st.header("📝 Generated Content")
            st.write(response.text)

            pptx_data = crear_pptx(response.text)

            st.download_button(
                "🚀 DOWNLOAD YOUR POWERPOINT",
                pptx_data,
                "Presentation.pptx",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )

            st.balloons()
