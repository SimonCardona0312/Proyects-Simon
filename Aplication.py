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
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1. El usuario sube el archivo
Audio_fill = st.file_uploader("Upload audio", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    # Límite estricto: 4MB (Aprox 3 min en Mac)
    MAX_SIZE = 4 * 1024 * 1024 

    if Audio_fill.size > MAX_SIZE:
        st.error(f"❌ ARCHIVO DEMASIADO GRANDE ({Audio_fill.size / (1024*1024):.2f} MB). Máximo 4MB.")
        # Usamos stop() y además NO ponemos un 'else', para que el código termine aquí
        st.stop() 

    # --- TODO EL PROCESAMIENTO DEBE IR AQUÍ ABAJO ---
    # Si llegó aquí, es porque el archivo es pequeño.
    
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    with st.spinner("Whisper is processing..."):
        # Solo se cargará el modelo si el archivo pasó la prueba de tamaño
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.write(resultado["text"])

    # El botón de Gemini debe estar aquí, protegido por la validación de arriba
    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is working..."):
            model = GenAI.GenerativeModel('gemini-1.5-flash')
            # Instrucción simplificada para asegurar que entienda el audio de Mac
            prompt = f"Analyze this text from a Mac audio: {resultado['text']}. Create 5 slides in English. No Arabic."
            response = model.generate_content(prompt)
            st.write(response.text)
