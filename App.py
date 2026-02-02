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
# Puedes usar un link directo de Pinterest o de cualquier página
url_imagen = ""

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{url_imagen}");
        background-size: cover; /* Cubre toda la pantalla sin deformarse */
        background-position: center; /* Centrado para computadoras */
        background-repeat: no-repeat;
        background-attachment: fixed; /* La imagen no se mueve al bajar la página */
    }}

    /* Ajuste para que en CELULAR se vea la mejor parte de la foto */
    @media (max-width: 768px) {{
        .stApp {{
            background-position: center center; 
        }}
    }}
    
    /* Capa para que el contenido sea legible sobre la imagen */
    .main {{
        background-color: rgba(0, 0, 0, 0.4); 
        padding: 20px;
        border-radius: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
st.title("🪄 Transcription and Slide Creator")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Enter your API KEY here 
GenAI.configure(api_key=st.secrets["API_KEY"])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PowerPoint Function
def crear_pptx(texto_generado):
    prs = Presentation() # Crea un archivo limpio
    
    # Dividimos el texto en trozos (cada trozo es una diapositiva)
    slides_content = texto_generado.split("--- SLIDE")

    for slide_text in slides_content:
        if slide_text.strip():
            # Usamos el diseño 'Título y Objetos' (índice 1 en PowerPoint)
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)

            # Separamos las líneas: la 1ra es Título, las demás son Cuerpo
            lineas = slide_text.strip().split('\n')
            titulo_texto = lineas[0].strip()
            cuerpo_texto = "\n".join(lineas[1:]).strip()

            # Insertamos el Título en el lugar correcto
            if slide.shapes.title:
                slide.shapes.title.text = titulo_texto
            
            # Insertamos los puntos (bullets) en el cuadro principal
            if len(slide.placeholders) > 1:
                slide.placeholders[1].text = cuerpo_texto

    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" , "opus" ,"wav", "m4a"])

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

            Detect the main language of the audio.

            ALL generated content MUST be EXCLUSIVELY in that language.

            Do not mix languages or translate.

            2. TRANSCRIPTION:

            Include the complete transcription of the audio.

            Write it only in the original language.

            Place it at the beginning under the heading:

            === TRANSCRIPTION ===

            3. INSTRUCTION DETECTION:

            Determine whether the audio contains a clear instruction to create content.

            4. IF A CLEAR INSTRUCTION EXISTS:

            Generate a presentation with a MINIMUM of 5 SLIDES.

            Each slide must be clearly separated and numbered.

            Each slide must represent a distinct idea or part of the requested content.

            The content may be continuous text or in lines.

            Inside each slide:

            The first line must be a short Title.

            The following lines must be bullet-point content.

            Use EXACTLY this separator for each slide:

            --- SLIDE N ---

            5. IF NO CLEAR INSTRUCTION EXISTS:

            Generate ONLY ONE slide.

            Clearly indicate that an explicit instruction is needed in the audio.

            6. SPEAKER NOTES (MANDATORY):

            Every slide MUST include real speaker notes.

            Speaker notes must NOT be included in the slide body.

            Speaker notes must be written as full explanatory text intended for a presenter.

            Speaker notes must be placed exclusively in the PowerPoint field:

            notes_slide

            7. FORMAT RESTRICTIONS:

            Do not write additional explanations.

            Do not add comments outside the defined structure.

            Output must be strictly structured for PowerPoint slide + notes separation.

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










