#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Libraries
import streamlit as st 
import whisper         
import os              
import fpdf as FPDF
import google.generativeai as GenAI
from fpdf import FPDF

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# This is the visual part of the page 
st.set_page_config(page_title="Gen", page_icon="🪄")
st.title("🪄 Transcription and Slide Creator")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Enter your API KEY here 
GenAI.configure(api_key=st.secrets["API_KEY"])

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#PDF Function
def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Reemplazamos caracteres que dan error en PDF básicos
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    # 1. VALIDACIÓN DE TAMAÑO (Aprox 3 minutos)
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error("❌ The audio is too long. Please upload a file shorter than 3 minutes (MAX 10MB).")
        st.stop() # <--- ESTO DETIENE LA CARGA POR COMPLETO
    
    # 2. PROCESAMIENTO (Solo si pasa la validación)
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    with st.spinner("Whisper is processing your audio"):
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("This is your transcribed text")
    st.write(resultado["text"])

    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is creating your slides..."):
            # Usamos 1.5-flash para evitar errores de cuota en Streamlit Cloud
            modelo_gemini = GenAI.GenerativeModel('models/gemini-1.5-flash')
            
            # CORRECCIÓN DE SINTAXIS Y PROMPT ANTI-HALLUCINATION
            instruction = f"""
            Analyze the following transcribed text: {resultado['text']} 
            and generate ONLY clearly separated slides based on these rules:

            1. LANGUAGE:
            - TRANSCRIPTION: Keep it in the original language.
            - SLIDES: Generate all content EXCLUSIVELY in PROFESSIONAL ENGLISH.

            2. MAC AUDIO CORRECTION (Anti-Hallucination):
            - The source is a Mac MPEG-4 recording; ignore background static.
            - STRICT PROHIBITION: Do not use Arabic, Asian, or non-Latin characters.
            - If noise is detected, ignore it and focus on the main speech.

            3. STRUCTURE:
            - Minimum of 5 slides if an instruction is found.
            - Separator: Use EXACTLY --- SLIDE N ---
            - Format: No extra comments or greetings.
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
