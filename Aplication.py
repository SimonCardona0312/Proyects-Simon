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
# --- Transcription Function ---
Audio_fill = st.file_uploader("Upload your audio", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    # 1. Definimos el límite de 3 min (en Mac son aprox 4MB)
    MAX_FILE_SIZE = 4 * 1024 * 1024 

    # 2. VALIDACIÓN AGRESIVA
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error(f"❌ ARCHIVO RECHAZADO: Pesa {Audio_fill.size / (1024*1024):.2f} MB. El límite es 4MB (~3 min).")
        # Borramos el archivo de la memoria de Streamlit para que no intente nada más
        Audio_fill = None 
        st.stop() # Detención total

    # 3. PROCESAMIENTO (Solo si es menor a 4MB)
    # Si ves que sigue cargando, es porque esta parte no está bien indentada
    with st.spinner("Processing short audio..."):
        with open("temp_audio.mp3", "wb") as f:
            f.write(Audio_fill.getbuffer())
        
        # Cargamos el modelo pequeño para que sea instantáneo
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")
        
        st.success("Transcription success")
        st.write(resultado["text"])
