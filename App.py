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
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "opus" , "m4a"])

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
                Analiza el siguiente audio transcrito: {resultado["text"]}

                Tu tarea es generar ÚNICAMENTE diapositivas claramente separadas, cumpliendo TODAS las reglas a continuación sin excepción.
                
                ────────────────────────
                REGLAS OBLIGATORIAS
                ────────────────────────
                
                1. IDIOMA
                - Detecta automáticamente el idioma principal del audio.
                - TODO el contenido generado debe estar EXCLUSIVAMENTE en ese idioma.
                - No traduzcas, no mezcles idiomas y no aclares en otro idioma.
                
                2. TRANSCRIPCIÓN
                - Incluye la transcripción COMPLETA del audio.
                - Escríbela exactamente en el idioma original detectado.
                - Debe aparecer AL INICIO del resultado, bajo el encabezado EXACTO:
                
                ▣ STREAMLIT TRANSCRIPTION ▣
                
                3. DETECCIÓN DE INSTRUCCIONES
                - Analiza si el audio contiene una instrucción CLARA y EXPLÍCITA para crear contenido
                  (por ejemplo: “haz una presentación”, “explícame”, “resume”, “crea diapositivas”, etc.).
                
                4. SI EXISTE UNA INSTRUCCIÓN CLARA
                - Genera una presentación con un MÍNIMO de 5 diapositivas.
                - Cada diapositiva debe:
                  - Estar claramente separada
                  - Estar numerada
                  - Representar UNA idea distinta o una parte del contenido solicitado
                - Usa EXACTAMENTE este separador para cada diapositiva (sin modificarlo):
                
                ⎯⎯⎯ SECTION: SLIDE N ⎯⎯⎯
                
                5. SI NO EXISTE UNA INSTRUCCIÓN CLARA
                - Crea un MÍNIMO de 5 diapositivas:
                  - Explicando claramente el contenido del audio
                  - Resumiendo y estructurando lo que se dijo
                  - Indicando al usuario que puede solicitar algo más específico si lo desea
                - Mantén el mismo formato y separador de diapositivas indicado arriba.
                
                6. FORMATO
                - No incluyas texto fuera de la transcripción y las diapositivas.
                - No agregues introducciones, conclusiones ni explicaciones adicionales.
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












