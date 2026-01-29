#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Libraries
import streamlit as st 
import whisper         
import os              
import fpdf as FPDF
import google.generativeai as GenAI
from fpdf import FPDF
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# This is the visual part of the page 
st.set_page_config(page_title="Gen", page_icon="🪄")
st.title("🪄 Transcription and Slide Creator")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Enter your API KEY here 
GenAI.configure(api_key=st.secrets["API_KEY"])
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#PDF Function
def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Reemplazamos caracteres que dan error en PDF básicos
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    # 1. Guardar y Transcribir
    with open("temp_audio.mp3", "wb") as f:
        f.write(Audio_fill.getbuffer())
        
    # Mostramos un mensaje de carga para que el usuario espere
    with st.spinner("Whisper is pr"):
        modelo_whisper = whisper.load_model("base")
        resultado = modelo_whisper.transcribe("temp_audio.mp3")

    st.success("Transcription success")
    st.subheader("Este es el texto extraído:")
    st.write(resultado["text"])


    if st.button("✨ Generative Slides"):
        
        with st.spinner("Gemini está creando tus diapositivas..."):
          
            modelo_gemini = GenAI.GenerativeModel('models/gemini-2.5-flash')
            
            instruction = f"""
  
Analyze the following audio/text: {resultado['text']} and generate ONLY clearly separated slides.

### MANDATORY RULES:

1. LANGUAGE & TRANSLATION:
- TRANSCRIPTION: Must be written in the ORIGINAL language of the audio (Spanish or English).
- SLIDE CONTENT: All slides MUST be generated EXCLUSIVELY in PROFESSIONAL ENGLISH, regardless of the audio's original language.
- If the audio is in Spanish, you must translate the content into English for the slides.

2. TRANSCRIPTION FORMAT:
- Include the complete transcription of the audio.
- Write it only in the original language.
- Place it at the beginning under the header:
  === TRANSCRIPTION ===

3. INSTRUCTION DETECTION:
- Determine if the audio contains a clear instruction to create specific content.

4. IF A CLEAR INSTRUCTION EXISTS:
- Generate a presentation with a MINIMUM of 5 SLIDES.
- Each slide must be clearly separated and numbered.
- Each slide must represent a distinct idea or part of the requested content.
- Use EXACTLY this separator for each slide:
  --- SLIDE N ---

5. IF NO CLEAR INSTRUCTION EXISTS:
- Generate ONLY ONE slide.
- Clearly state in English that an explicit instruction is needed from the audio.

6. MAC AUDIO & ANTI-HALLUCINATION:
- This is a native Mac recording; ignore background static, clicks, or metallic interference.
- STRICT PROHIBITION: Do not use Arabic, Asian, or any non-Latin characters.
- If the audio is unclear, default to Spanish or English as the source.

7. FORMATTING:
- Do not write additional explanations.
- Do not add comments outside of the transcription and the slides.
                        
            """

            # Esto detecta si es un archivo de Mac y lo procesa correctamente
            mime_actual = "video/mp4" if "mp4" in Audio_fill.name else Audio_fill.type
            answer = modelo_gemini.generate_content([instruction, {"mime_type": mime_actual, "data": Audio_fill.read()}])
            
            st.markdown("---")
            st.header("📝 Generated Content")
            st.write(answer.text)
            pdf_bytes = crear_pdf(answer.text)
            st.download_button(
                label="💾 Download PDF",
                data=pdf_bytes,
                file_name="Presentation PDF",
                mime="application/pdf"
            )
            
        
            
            

        st.balloons() 


