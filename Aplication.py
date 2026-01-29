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
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Transcription Function
Audio_fill = st.file_uploader("Upload your audio so we can transcribe", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:

    MAX_FILE_SIZE = 10 * 1024
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
            
            instruction = f
            """
  
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
                === TRANSCRIPTION ===

            3. INSTRUCTION DETECTION:
            - Determine whether the audio contains a clear instruction to create content.

            4. IF A CLEAR INSTRUCTION EXISTS:
            - Generate a presentation with a MINIMUM of 5 SLIDES.
            - Each slide must be clearly separated and numbered.
            - Each slide must represent a distinct idea or part of the requested content.
            - The content may be continuous text or in lines; there are no internal formatting restrictions.

            Use EXACTLY this separator for each slide:

            --- SLIDE N ---

            5. IF NO CLEAR INSTRUCTION EXISTS:
            - Generate ONLY ONE slide.
            - Clearly indicate that an explicit instruction is needed in the audio.

            6. FORMAT:
            - Do not write additional explanations.
            - Do not add comments outside the transcription and the slides.
            """
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            answer = modelo_gemini.generate_content(instruction)

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


