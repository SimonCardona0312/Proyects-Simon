import streamlit as st 
import whisper         
import os              
import fpdf as FPDF
import google.generativeai as GenAI

st.title("Slides Generators")
#
from fpdf import FPDF

def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Reemplazamos caracteres que dan error en PDF básicos
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')



GenAI.configure(api_key=st.secrets["API_KEY"])
# modelos = [m.name for m in GenAI.list_models()]
# st.write("Modelos que tu llave sí puede ver:", modelos)

Audio_fill = st.file_uploader("Upload your file", type=["mp3", "wav", "m4a"])

if Audio_fill is not None:
    # 1. Guardar y Transcribir
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    # Mostramos un mensaje de carga para que el usuario espere
    with st.spinner("Whisper está procesando el audio..."):
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("Este es el texto extraído:")
    st.write(resultado["text"])


    if st.button("✨ Generative Slides"):
        
        with st.spinner("Gemini está creando tus diapositivas..."):
          
            modelo_gemini = GenAI.GenerativeModel('models/gemini-2.5-flash')
            
            instruction = f"""
            Actúa como un diseñador profesional.
            Tarea: Crea una presentación basada en este texto: {resultado['text']}
            
            Instrucciones:
            1. Crea mínimo 5 diapositivas.
            2. Cada una con Título, Viñetas y Notas del orador.
            3. Formato profesional.
            """
            

            answer = modelo_gemini.generate_content(instruction)
            
            st.markdown("---")
            st.header("📋 Tu Presentación está lista:")
            st.write(answer.text)
            pdf_bytes = crear_pdf(answer.text)
            st.download_button(
                label="💾 Descargar como PDF",
                data=pdf_bytes,
                file_name="presentacion.pdf",
                mime="application/pdf"
            )
            
        
            
            
        st.balloons() 