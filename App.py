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
  
            Analiza el siguiente audio: {resultado['text']} y genera ÚNICAMENTE diapositivas claramente separadas.
            
            REGLAS OBLIGATORIAS (CUMPLIMIENTO ESTRICTO):
            
            1. IDIOMA:
            - Detecta automáticamente el idioma principal del audio.
            - TODO el contenido generado debe estar EXCLUSIVAMENTE en ese idioma.
            - No traduzcas, no mezcles idiomas y no expliques el idioma detectado.
            
            2. TRANSCRIPCIÓN:
            - Incluye la transcripción COMPLETA y literal del audio.
            - Escríbela únicamente en el idioma original.
            - Debe colocarse AL INICIO del resultado bajo el encabezado EXACTO:
            
            ▣ STREAMLIT TRANSCRIPTION ▣
            
            3. DETECCIÓN DE INSTRUCCIONES:
            - Analiza si el audio contiene una instrucción clara para crear contenido (por ejemplo: explicar, resumir, enseñar, presentar, describir, desarrollar un tema).
            
            4. SI EXISTE UNA INSTRUCCIÓN CLARA:
            - Genera una presentación con EXACTAMENTE 5 DIAPOSITIVAS (no más, no menos).
            - Cada diapositiva debe:
              - Estar claramente numerada.
              - Desarrollar UNA idea distinta.
              - Contener información AMPLIA, detallada y explicativa.
              - Tener al menos 3–5 párrafos o múltiples líneas bien desarrolladas.
              - NO usar contenido corto, frases sueltas ni resúmenes mínimos.
            
            - Usa EXACTAMENTE este separador para cada diapositiva:
            
            ⎯⎯⎯ SECTION: SLIDE N ⎯⎯⎯
            
            (reemplaza N por el número correspondiente)
            
            5. SI NO EXISTE UNA INSTRUCCIÓN CLARA:
            - Crea EXACTAMENTE 5 diapositivas.
            - Cada diapositiva debe explicar de forma detallada lo que se menciona en el audio.
            - Amplía las ideas, proporciona contexto y ejemplos cuando sea posible.
            - En la ÚLTIMA diapositiva, explica claramente al usuario que puede solicitar algo más específico si lo desea.
            - El contenido interno de cada diapositiva debe ser extenso y explicativo, nunca breve.
            
            6. PROHIBICIONES:
            - No incluyas conclusiones fuera de las diapositivas.
            - No agregues texto antes o después de las secciones.
            - No uses viñetas excesivamente cortas.
            - No generes menos de 5 diapositivas bajo ninguna circunstancia.


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







