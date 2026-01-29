#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Libraries
import streamlit as st 
import whisper         
import os              
import google.generativeai as GenAI
from fpdf import FPDF

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Page Config
st.set_page_config(page_title="Gen", page_icon="🪄")
st.title("🪄 Transcription and Slide Creator")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# API Key Configuration
GenAI.configure(api_key=st.secrets["API_KEY"])

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PDF Function
def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Limpieza de caracteres para evitar errores en el PDF
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Transcription & Logic Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    # 1. VALIDACIÓN DE TAMAÑO (Límite estricto de 4MB para aprox. 3 minutos en Mac)
    MAX_FILE_SIZE = 1 * 1024 
    
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error(f"❌ Error: File too large ({Audio_fill.size / (1024*1024):.2f} MB). Max limit is 4MB (~3 minutes).")
        st.stop() # Detiene la ejecución por completo aquí

    # 2. PROCESAMIENTO (Solo si el archivo es menor a 4MB)
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    with st.spinner("Whisper is processing your audio..."):
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("This is your transcribed text")
    st.write(resultado["text"])

    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is creating your slides..."):
            # Usamos 1.5-flash por ser el más rápido y estable en la nube
            modelo_gemini = GenAI.GenerativeModel('models/gemini-1.5-flash')
            
            # Prompt optimizado en inglés para evitar alucinaciones en árabe
            instruction = f"""
            Analyze the following text: "{resultado['text']}" 
            And generate ONLY clearly separated slides according to these rules:

            1. LANGUAGE:
            - TRANSCRIPTION: Keep the original text under the header === TRANSCRIPCIÓN ===.
            - SLIDES: Generate ALL slide content EXCLUSIVELY in PROFESSIONAL ENGLISH.
            - If the original text is in Spanish, translate it to English for the slides.

            2. MAC AUDIO CORRECTION (Anti-Hallucination):
            - The source is a Mac recording; ignore any background static or metallic noise.
            - STRICT PROHIBITION: Do not use Arabic, Asian, or non-Latin characters.

            3. STRUCTURE:
            - Minimum of 5 slides if an instruction is found.
            - Use EXACTLY this separator for each slide: --- SLIDE N ---
            - No extra comments, no greetings.
            """

            answer = modelo_gemini.generate_content(instruction)

            st.markdown("---")
            st.header("📝 Generated Content")
            st.write(answer.text)
            
            pdf_bytes = crear_pdf(answer.text)
            st.download_button(
                label="💾 Download PDF",
                data=pdf_bytes,
                file_name="Presentation.pdf",
                mime="application/pdf"
            )
            
        st.balloons()

