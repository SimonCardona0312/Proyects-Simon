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
st.markdown(
    f"""
    <style>
    /* 1. CONFIGURACIÓN BASE (PC/Tablets) */
    #video-background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        object-position: center; /* Centra el video por defecto */
        z-index: -1;
        filter: brightness(0.4);
    }}

    /* 2. AJUSTE PARA CELULARES (Pantallas de menos de 768px) */
    @media (max-width: 768px) {{
        #video-background {{
            /* Ajustamos la posición para que en celular se vea más la parte derecha (el espejo) */
            object-position: 65% center; 
        }}
        
        /* Hacemos que los textos de Streamlit no se peguen tanto a los bordes en el móvil */
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
    }}

    .stApp {{
        background: transparent;
    }}
    </style>

    <video autoplay muted loop playsinline id="video-background">
        <source src="{video_url}" type="video/mp4">
    </video>
    """,
    unsafe_allow_html=True
)
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
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:

    MAX_FILE_SIZE = 10 * 1024 * 1024
   
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error("The audio is too long or too short. Please upload a file shorter than 3 minutes. (MAX 10MB)")
        st.stop()
    else:
       
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

            1. LANGUAGE:
            - Detect the main language of the audio.
            - ALL generated content MUST be EXCLUSIVELY in that language.
            - Do not mix languages or translate.

            2. TRANSCRIPTION:
            - Include the complete transcription of the audio.
            - Write it only in the original language.
            - Place it at the beginning under the heading:
                ▣ STREAMLIT TRANSCRIPTION ▣

            3. INSTRUCTION DETECTION:
            - Determine whether the audio contains a clear instruction to create content.

            4. IF A CLEAR INSTRUCTION EXISTS:
            - Generate a presentation with a MINIMUM of 5 SLIDES.
            - Each slide must be clearly separated and numbered.
            - Each slide must represent a distinct idea or part of the requested content.
            - The content may be continuous text or in lines; there are no internal formatting restrictions.

            Use EXACTLY this separator for each slide:

            ⎯⎯⎯ SECTION: SLIDE N ⎯⎯⎯


            5. IF NO CLEAR INSTRUCTION EXISTS:
            - Generate ONLY ONE slide.
            - Clearly indicate that an explicit instruction is needed in the audio.

            6. FORMAT:
            - Do not write additional explanations.
            - Do not add comments outside the transcription and the slides.
            """
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            answer = modelo_gemini.generate_content(instruction)

            st.header("📝 Generated Content")
            
            st.info("Everything is ready! You can review the content below and download your slides.")
            st.write(answer.text)
            
            pptx_data = crear_pptx(answer.text)
            
        
            st.write("") 
            
            st.download_button(
                label="🚀 DOWNLOAD YOUR POWERPOINT",
                data=pptx_data,
                file_name="Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True 
            )
            st.balloons()









