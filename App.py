#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Libraries
import streamlit as st 
import whisper         
import os              
import google.generativeai as GenAI
from pptx import Presentation 
from io import BytesIO

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# This is the visual part of the page 
st.set_page_config(page_title="Gen", page_icon="🪄")
st.title("🪄 Transcription and Slide Creator")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Enter your API KEY here 
GenAI.configure(api_key=st.secrets["API_KEY"])

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PowerPoint Function
def crear_pptx(texto):
    prs = Presentation()
    
    secciones = texto.split("--- SLIDE")
    
    for i, seccion in enumerate(secciones):
        if seccion.strip():
            slide_layout = prs.slide_layouts[1] 
            slide = prs.slides.add_slide(slide_layout)

            lineas = seccion.strip().split('\n')
            
            title_shape = slide.shapes.title
            body_shape = slide.placeholders[1]
            
            title_shape.text = f"Slide {i}" if i > 0 else "Presentation Intro"
            body_shape.text = seccion.strip()

    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a", "opus"])

if Audio_fill is not None:
    MAX_FILE_SIZE = 10 * 1024 * 1024
   
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error("The audio is too long or too short. Please upload a file shorter than 3 minutes. (MAX 10MB)")
        st.stop()
    else:
        # Guardamos el archivo con su extensión original para mejor compatibilidad
        extension = Audio_fill.name.split('.')[-1]
        temp_filename = f"temp_audio.{extension}"
        
        with open(temp_filename, "wb") as f:
            f.write(Audio_fill.getbuffer())
            
        with st.spinner("Whisper is processing your audio..."):
            # USAMOS MODELO BASE EN MINÚSCULAS PARA ESTABILIDAD
            modelo_whisper = whisper.load_model("base")
            
            # DETECCIÓN AUTOMÁTICA DE IDIOMA Y PARÁMETROS PARA CPU
            resultado = modelo_whisper.transcribe(temp_filename, task="transcribe", fp16=False)
            
            # Guardamos el idioma detectado para Gemini
            idioma_detectado = resultado.get("language", "en")

    st.success(f"Transcription success (Detected Language: {idioma_detectado.upper()})")
    st.subheader("This is your transcribed text")
    st.write(resultado["text"])

    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is creating your slides..."):
            # Ajuste del modelo a la versión flash disponible
            modelo_gemini = GenAI.GenerativeModel('gemini-1.5-flash')
            
            instruction = f"""
            Analyze the audio text: "{resultado['text']}" and generate ONLY clearly separated slides.

            Mandatory rules:

            1. LANGUAGE:
            - The detected language is {idioma_detectado}.
            - ALL generated content MUST be EXCLUSIVELY in that language.
            - If it's Spanish, write in Spanish. If it's English, write in English.

            2. TRANSCRIPTION:
            - Include the complete transcription of the audio.
            - Write it only in the original language.
            - Place it at the beginning under the heading:
                === TRANSCRIPTION ===

            3. INSTRUCTION DETECTION:
            - Determine whether the audio contains a clear instruction to create content.

            4. IF A CLEAR INSTRUCTION EXISTS:
            - Generate a presentation with a MINIMUM of 5 SLIDES.
            - Use EXACTLY this separator: --- SLIDE N ---

            5. IF NO CLEAR INSTRUCTION EXISTS:
            - Generate ONLY ONE slide explaining that an instruction is needed.

            6. FORMAT:
            - Do not write additional explanations or comments.
            """

            answer = modelo_gemini.generate_content(instruction)
            st.markdown("---")
            st.header("📝 Generated Content")
            
            st.info("Everything is ready! You can review the content below and download your slides.")
            st.write(answer.text)
            
            pptx_data = crear_pptx(answer.text)
            
            st.download_button(
                label="🚀 DOWNLOAD YOUR POWERPOINT",
                data=pptx_data,
                file_name="Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True 
            )
            st.balloons()
