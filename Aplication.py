#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Libraries
import streamlit as st
import google.generativeai as GenAI
from fpdf import FPDF
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
# This is the visual part of the page 
st.set_page_config(page_title="Gen", page_icon="🪄")
st.title("🪄 Transcription and Slide Creator")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Enter your API key here
API_KEY = "AIzaSyAJ8c7Pg8zUcYcxesYXKo7CJi4LpPeNiec"
GenAI.configure(api_key=API_KEY)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PDF Function
def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Transcription function 
audio_file = st.file_uploader("Upload your audio so we can transcribe it and desing the slides", type=["mp3","mp4","wav", "m4a"])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("✨ Process Audio"):
        with st.spinner("Gimini is listening and writing..."):
            try:
                model = GenAI.GenerativeModel('models/gemini-3-flash-preview')
                
                # Le pedimos específicamente la transcripción Y las diapositivas
                prompt = (
                """""
Analiza el audio y genera ÚNICAMENTE diapositivas claramente separadas.

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



                """""
                )
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": "audio/mp3", "data": audio_file.read()}
                ])
                
                todo_el_contenido = response.text
                
                # Mostramos el resultado en la app
                st.markdown("---")
                st.subheader("📝 Generated Content")
                st.write(todo_el_contenido)
                
                # Opción de descarga
                pdf_output = crear_pdf(todo_el_contenido)
                st.download_button(
                    label="📥 Download and transcript and slides(PDF)",
                    data=bytes(pdf_output),
                    file_name="analisis_audio.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error: {e}")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
