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
            modelo_whisper = whisper.load_model("small")
            resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("This is your transcribed text")
    st.write(resultado["text"])

    if st.button("✨ Generative Slides"):
        
        with st.spinner("Gemini is creating your slides..."):
          
            modelo_gemini = GenAI.GenerativeModel('models/gemini-2.5-flash')
            
            instruction = f"""
  
                    Analiza el siguiente audio: {resultado['text']}
                    
                    DEBES generar la respuesta en BLOQUES SEPARADOS.
                    NO puedes escribir todo el contenido en un solo bloque.
                    Cada bloque representa UNA diapositiva independiente.
                    
                    REGLAS INQUEBRANTABLES:
                    
                    1. IDIOMA
                    - Detecta el idioma principal del audio.
                    - TODO el contenido DEBE estar exclusivamente en ese idioma.
                    - No mezcles idiomas.
                    - No traduzcas.
                    
                    2. TRANSCRIPCIÓN
                    - Incluye la transcripción COMPLETA del audio.
                    - Escríbela únicamente en el idioma original.
                    - Colócala AL INICIO bajo el encabezado EXACTO:
                    
                    ▣ STREAMLIT TRANSCRIPTION ▣
                    
                    3. DETECCIÓN DE INSTRUCCIÓN
                    - Determina si el audio contiene una instrucción clara para crear contenido.
                    
                    4. GENERACIÓN DE DIAPOSITIVAS (OBLIGATORIO)
                    - DEBES crear EXACTAMENTE 5 diapositivas.
                    - NO más, NO menos.
                    - CADA diapositiva debe escribirse en un BLOQUE SEPARADO.
                    - NUNCA combines dos diapositivas en el mismo bloque.
                    - NUNCA pongas todo el texto seguido.
                    
                    5. FORMATO OBLIGATORIO (CRÍTICO)
                    Antes de escribir el contenido de CADA diapositiva, escribe EXACTAMENTE este separador en una línea independiente:
                    
                    ⎯⎯⎯ SECTION: SLIDE N ⎯⎯⎯
                    
                    (reemplaza N por 1, 2, 3, 4 y 5)
                    
                    6. CONTENIDO DE CADA DIAPOSITIVA
                    - Cada diapositiva debe desarrollar UNA idea distinta.
                    - El contenido NO puede ser corto.
                    - Cada diapositiva debe tener:
                      - Explicación extensa
                      - Contexto
                      - Desarrollo claro del tema
                    - MÍNIMO recomendado: 120–150 palabras por diapositiva.
                    
                    7. SI EXISTE UNA INSTRUCCIÓN CLARA EN EL AUDIO
                    - Las 5 diapositivas deben cumplir exactamente la instrucción solicitada.
                    
                    8. SI NO EXISTE UNA INSTRUCCIÓN CLARA
                    - Las 5 diapositivas deben explicar detalladamente lo que dice el audio.
                    - La diapositiva 5 debe indicar claramente que el usuario puede pedir algo más específico.
                    
                    9. PROHIBICIONES ABSOLUTAS
                    - No escribas texto fuera de las diapositivas.
                    - No hagas resúmenes generales.
                    - No generes una sola diapositiva.
                    - No ignores los separadores.
                    - No compactes el contenido.
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








