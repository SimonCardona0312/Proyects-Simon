import streamlit as st
import whisper
import google.generativeai as GenAI
from pptx import Presentation
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gen", page_icon="🪄")

# --- FONDO DE PANTALLA (CON FILTRO OSCURO PARA QUE SE LEA EL TEXTO) ---
# Puedes cambiar este link por cualquier imagen de Pinterest que termine en .jpg o .png
url_fondo = "https://i.pinimg.com/originals/8e/3c/5e/8e3c5ef2d8aa56efb980fb6e16819620.jpg"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{url_fondo}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    /* Esto oscurece el fondo para que las letras blancas se lean bien */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6); 
        z-index: -1;
    }}
    h1, h2, h3, p, div {{
        color: white !important; /* Forza a que todo el texto sea blanco */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🪄 Transcription and Slide Creator")


# 3. FUNCIÓN PARA CREAR EL POWERPOINT BONITO
def crear_pptx(texto_generado):
    prs = Presentation() # Usa la plantilla básica limpia
    
    # Dividimos por diapositivas
    slides_content = texto_generado.split("--- SLIDE")

    for slide_text in slides_content:
        if slide_text.strip():
            # Usamos el diseño: Título + Contenido (Layout 1)
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)

            # Limpiamos el texto
            lineas = slide_text.strip().split('\n')
            
            # TRUCO PRO: La primera línea será el TÍTULO, el resto el CUERPO
            titulo = lineas[0].replace("Title:", "").replace("**", "").strip()
            contenido = "\n".join(lineas[1:]).strip()

            # Asignamos al PowerPoint real
            if slide.shapes.title:
                slide.shapes.title.text = titulo
            
            if len(slide.placeholders) > 1:
                slide.placeholders[1].text = contenido

    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()

# 4. CARGA DE WHISPER (Modelo Base para que no se caiga)
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

modelo_whisper = load_whisper()

# 5. INTERFAZ Y LÓGICA
audio_file = st.file_uploader("Sube tu audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

if audio_file is not None:
    # Guardamos temporalmente el archivo
    with open("temp_audio.mp3", "wb") as f:
        f.write(audio_file.getbuffer())

    with st.spinner("🎧 Escuchando y detectando idioma..."):
        # Transcripción automática
        result = modelo_whisper.transcribe("temp_audio.mp3", fp16=False)
        texto = result["text"]
        idioma = result["language"] # Detecta 'es' o 'en'
        
    st.success(f"Transcripción completa (Idioma: {idioma})")
    st.write(texto)

    # Botón mágico
    if st.button("✨ Generar PowerPoint Profesional"):
        with st.spinner("🤖 Gemini está diseñando tus diapositivas..."):
            
            # PROMPT ESTRICTO PARA QUE SE VEA ORDENADO
            modelo_gemini = GenAI.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Act as a professional presentation designer.
            SOURCE TEXT: "{texto}"
            DETECTED LANGUAGE: {idioma}

            INSTRUCTIONS:
            1. Create 4 to 6 slides based on the text.
            2. The output MUST be in the language: {idioma}.
            3. FORMAT IS CRITICAL. Use this exact structure for every slide:

            --- SLIDE
            (Write here a Short and Catchy Title)
            - (Bullet point 1)
            - (Bullet point 2)
            - (Bullet point 3)

            Do not write "Slide 1" or labels. Just the separator, the title line, and the bullets.
            """
            
            respuesta = modelo_gemini.generate_content(prompt)
            
            # Mostramos el resultado y creamos el archivo
            st.markdown("### Vista Previa:")
            st.write(respuesta.text)
            
            archivo_pptx = crear_pptx(respuesta.text)
            
            st.download_button(
                label="📥 DESCARGAR POWERPOINT",
                data=archivo_pptx,
                file_name="Presentacion_Pro.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
