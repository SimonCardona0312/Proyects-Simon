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
    
    # Separamos el contenido por el marcador definido en el prompt
    secciones = texto.split("--- SLIDE")
    
    for i, seccion in enumerate(secciones):
        if seccion.strip():
            # Usamos un diseño de diapositiva estándar (Título y Cuerpo)
            slide_layout = prs.slide_layouts[1] 
            slide = prs.slides.add_slide(slide_layout)
            
            # Limpiamos el texto para el título y cuerpo
            lineas = seccion.strip().split('\n')
            
            title_shape = slide.shapes.title
            body_shape = slide.placeholders[1]
            
            title_shape.text = f"Slide {i}" if i > 0 else "Presentation Intro"
            body_shape.text = seccion.strip()

    # Guardamos en un objeto BytesIO para que Streamlit pueda descargarlo
    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:

    MAX_FILE_SIZE = 10 * 1024 * 1024
    # 1. Audio size validation
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error("The audio is too long or too short. Please upload a file shorter than 3 minutes. (MAX 10MB)")
        st.stop()
    else:
        # 1. I save it and transcribe it.
        with open("temp_audio.mp3", "wb") as f:
            f.write(Audio_fill.getbuffer())
            
        # We show the loading message so the user can wait.
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
              
            Analyze the audio: {resultado['text']} and generate ONLY clearly separated slides.
            
            MANDATORY RULES:
            
            1. LANGUAGE
            - Detect the main language of the audio.
            - ALL generated content MUST be EXCLUSIVELY in that language.
            - Do not mix languages or translate.
            
            2. TRANSCRIPTION
            - Include the COMPLETE transcription of the audio.
            - Write it ONLY in the original language.
            - Place it at the very beginning under the heading:
              === TRANSCRIPTION ===
            
            3. INSTRUCTION & COHERENCE DETECTION
            - Determine whether the audio contains:
              a) A clear instruction to create content, OR
              b) No clear instruction and/or incoherent, vague, or informal speech.
            
            4. IF A CLEAR INSTRUCTION EXISTS
            - Generate a presentation with a MINIMUM of 5 SLIDES.
            - Each slide must:
              - Be clearly separated and numbered.
              - Represent a distinct idea or section of the requested content.
            - Content can be free-form text or lines (no internal formatting restrictions).
            
            5. IF NO CLEAR INSTRUCTION EXISTS OR THE AUDIO IS INCOHERENT
            - STILL generate a presentation with EXACTLY 5 SLIDES.
            - The slides must:
              - Analyze ONLY what is actually present in the audio.
              - NOT invent facts, topics, or intentions.
              - Describe the nature, limitations, and possible interpretation of the audio.
            - The structure should resemble an analytical or diagnostic presentation, for example:
              - Introduction / Detected content
              - Context (or lack of it)
              - Coherence analysis
              - Possible interpretations
              - Recommendation or next steps
            - Include speaker notes when relevant, explicitly stating that no clear instruction or topic is present.
            
            6. SLIDE SEPARATOR
            Use EXACTLY the following separator for each slide:
            
            --- SLIDE N ---
            
            7. OUTPUT FORMAT
            - Do NOT add explanations outside the transcription and slides.
            - Do NOT add meta-comments or system notes.
            - Output ONLY:
              1) The transcription
              2) The slides

            """
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            answer = modelo_gemini.generate_content(instruction)
            st.markdown("---")
            st.header("📝 Generated Content")
            
            # Un contenedor con estilo para el texto de Gemini
            st.info("Everything is ready! You can review the content below and download your slides.")
            st.write(answer.text)
            
            # Generación del archivo PPTX
            pptx_data = crear_pptx(answer.text)
            
            # Espaciado extra antes del botón
            st.write("") 
            
            st.download_button(
                label="🚀 DOWNLOAD YOUR POWERPOINT",
                data=pptx_data,
                file_name="Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True # Esto hace que el botón ocupe todo el ancho
            )
            st.balloons()







