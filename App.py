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
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "opus" , "aac" ,"m4a"])

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

            Mandatory rules:
            TASK: 
            Analyze the following text from an audio: "{resultado['text']}"
            Your goal is to transform this information into a professional presentation.

            MANDATORY RULES:
            1. AUTOMATIC CREATION: 
               - Do not wait for an instruction. 
               - Convert the main topics, ideas, or story of the audio into a structured presentation.

            2. LANGUAGE:
               - Use the same language as the audio for everything.

            3. STRUCTURE:
               - Include the transcription first under: === TRANSCRIPTION ===
               - Create a MINIMUM of 5 slides based on the content.
               - If the audio is very short, expand the ideas to reach the 5 slides.
               - Use EXACTLY this separator: --- SLIDE N ---

            4. SLIDE CONTENT:
               - Each slide must have a Title and a clear Summary of an idea from the audio.
               - Do not add meta-comments (like "I have analyzed the audio"). Just the content.

            5. MAC FILTER:
               - Ignore background noise or static. Do not use non-Latin characters.
            """
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            answer = modelo_gemini.generate_content(instruction)

            st.markdown(
                """
                <style>
                .stApp {
                    background-image: url("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJndndndndndndndndndndndndndndndndndndnd/giphy.gif");
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                }
                </style>
                """,
                unsafe_allow_html=True
)
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











