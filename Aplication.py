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
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    # 1. Definimos el límite (4MB es ideal para ~3 min de Mac)
    MAX_FILE_SIZE = 4 * 1024 * 1024 
    
    # 2. Verificación de tamaño
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error(f"❌ ARCHIVO BLOQUEADO: Pesa {Audio_fill.size / (1024*1024):.2f} MB. El límite es 4MB.")
        st.info("Por favor, sube un audio más corto para continuar.")
        st.stop() # Detiene la ejecución aquí mismo

    # 3. PROCESAMIENTO (Esta parte solo se lee si el tamaño es correcto)
    # Guardamos el archivo temporalmente
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    with st.spinner("Whisper is processing..."):
        modelo_whisper = whisper.load_model("base")
        # Aquí es donde se suele trabar si el archivo es de Mac, 
        # pero al ser pequeño (<4MB) debería ser rápido
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("This is your transcribed text")
    st.write(resultado["text"])

    # El botón de Gemini debe estar DENTRO del bloque "if Audio_fill is not None"
    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is creating your slides..."):
            # Usamos 1.5-flash para mayor estabilidad en la nube
            modelo_gemini = GenAI.GenerativeModel('models/gemini-1.5-flash')
            
            # Tu prompt optimizado en inglés para evitar errores de Mac
            instruction = f"""
            Analyze the text: {resultado['text']}
            1. Create a transcript in the original language.
            2. Create minimum 5 slides in PROFESSIONAL ENGLISH.
            3. MAC FILTER: Ignore static, do NOT use Arabic or non-Latin characters.
            Use separator: --- SLIDE N ---
            """

            answer = modelo_gemini.generate_content(instruction)
            st.markdown("---")
            st.write(answer.text)
            
            pdf_bytes = crear_pdf(answer.text)
            st.download_button("💾 Download PDF", data=pdf_bytes, file_name="slides.pdf")
            st.balloons()
