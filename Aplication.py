import streamlit as st 
import google.generativeai as GenAI
from fpdf import FPDF

# 1. Configuración de la página
st.set_page_config(page_title="Gen", page_icon="🪄")
st.title("🪄 Transcription and Slide Creator")

# 2. API KEY desde Secrets
GenAI.configure(api_key=st.secrets["API_KEY"])

# 3. Función PDF CORREGIDA (Sin error de encoding)
def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Limpiamos el texto para que FPDF no explote con tildes o símbolos
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    # Retornamos los bytes directamente (esto arregla tu error)
    return pdf.output(dest='S').encode('latin-1')

# 4. Carga de Archivo
Audio_fill = st.file_uploader("Upload your audio", type=["mp3", "mp4" ,"wav", "m4a"])

if Audio_fill is not None:
    st.audio(Audio_fill) # Para que verifiques que el audio subió bien

    if st.button("✨ Generative Slides"):
        with st.spinner("Gemini is analyzing your Mac audio..."):
            try:
                # Usamos 1.5-flash por estabilidad y cuota
                modelo_gemini = GenAI.GenerativeModel('models/gemini-1.5-flash')
                
                instruction = """
                Analiza el audio proporcionado y genera ÚNICAMENTE diapositivas claramente separadas.
                Reglas obligatorias:
                1. TRANSCRIPCIÓN: Escribe el texto EXACTO del audio en su IDIOMA ORIGINAL bajo === TRANSCRIPCIÓN ===.
                2. IDIOMA DIAPOSITIVAS: Genera las diapositivas EXCLUSIVAMENTE EN INGLÉS.
                3. FILTRO MAC: Ignora ruidos de estática. PROHIBIDO usar árabe o caracteres extraños.
                4. ESTRUCTURA: Mínimo 5 diapositivas separadas por --- DIAPOSITIVA N ---.
                """

                # ENVIAMOS DIRECTO A GEMINI (Sin Whisper)
                # Usamos video/mp4 porque es como Mac guarda esos archivos
                response = modelo_gemini.generate_content([
                    instruction, 
                    {"mime_type": "video/mp4", "data": Audio_fill.read()}
                ])
                
                st.markdown("---")
                st.header("📝 Generated Content")
                st.write(response.text)
                
                # Generar y descargar PDF
                pdf_bytes = crear_pdf(response.text)
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_bytes,
                    file_name="presentation.pdf",
                    mime="application/pdf"
                )
                st.balloons()

            except Exception as e:
                st.error(f"Hubo un error: {e}")
