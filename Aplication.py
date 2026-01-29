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
    # 1. Guardar y Transcribir
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    # Mostramos un mensaje de carga para que el usuario espere
    with st.spinner("Whisper is processing your audio"):
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("This is your transcribed text")
    st.write(resultado["text"])


    if st.button("✨ Generative Slides"):
        
        with st.spinner("Gemini is creating your slides..."):
          
            modelo_gemini = GenAI.GenerativeModel('models/gemini-2.5-flash')
            
            instruction = f"""
  
            Analiza el audio: {resultado['text']} y genera ÚNICAMENTE diapositivas claramente separadas.

            Reglas obligatorias:

            1. IDIOMA:
            - Detecta el idioma principal del audio.
            - TODO el contenido generado DEBE estar EXCLUSIVAMENTE en ese idioma.
            - No mezcles idiomas ni traduzcas.

            2. TRANSCRIPCIÓN:
            - Incluye la transcripción completa del audio.
            - Escríbela únicamente en el idioma original.
            - Colócala al inicio bajo el encabezado:
                === TRANSCRIPCIÓN ===

            3. DETECCIÓN DE INSTRUCCIÓN:
            - Determina si el audio contiene una instrucción clara para crear contenido.

            4. SI EXISTE UNA INSTRUCCIÓN CLARA:
            - Genera una presentación con un MÍNIMO de 5 DIAPOSITIVAS.
            - Cada diapositiva debe estar claramente separada y numerada.
            - Cada diapositiva debe representar una idea o parte distinta del contenido solicitado.
            - El contenido puede ser texto continuo o en líneas, no hay restricciones internas de formato.

            Usa EXACTAMENTE este separador para cada diapositiva:

            --- DIAPOSITIVA N ---

            5. SI NO EXISTE UNA INSTRUCCIÓN CLARA:
            - Genera SOLO UNA diapositiva.
            - Indica claramente que se necesita una instrucción explícita en el audio.

            6. FORMATO:
            - No escribas explicaciones adicionales.
            - No agregues comentarios fuera de la transcripción y las diapositivas.
            """

            answer = modelo_gemini.generate_content(instruction)
            
            st.markdown("---")
            st.header("📝 Generated Content")
            st.write(answer.text)
            pdf_bytes = crear_pdf(answer.text)
            st.download_button(
                label="💾 Download PDF",
                data=pdf_bytes,
                file_name="Presentation PDF",
                mime="application/pdf"
            )
            
        
            
            

        st.balloons() 
