import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Recruiter Pro", page_icon="👔", layout="centered")

# --- GESTIÓN DE LA CLAVE API (SEGURIDAD) ---
# Intentamos obtener la clave desde los secretos de Streamlit (Nube)
# Si falla, busca en una variable local (para pruebas en tu PC)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # Opcional: Si quieres probar localmente, puedes descomentar la línea de abajo y pegar tu clave
    # api_key = "PEGA_TU_API_KEY_AQUÍ_SOLO_PARA_PRUEBAS_LOCALES" 
    st.error("No se encontró la API Key. Configúrala en los Secrets de Streamlit.")
    st.stop()

# Configurar Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Usamos Flash por rapidez

# --- INTERFAZ ---
st.title("🤖 Asistente de Selección de Talento")
st.markdown("Sube el CV en PDF para analizarlo contra la vacante activa.")

# --- SECCIÓN DE CONFIGURACIÓN (Oculta en un expander para que no moleste) ---
with st.expander("📝 Ver/Editar Descripción del Cargo (JD)"):
    default_jd = """
    [PEGA AQUÍ LA DESCRIPCIÓN DEL CARGO POR DEFECTO]
    Requisitos:
    - Experiencia en...
    - Conocimientos de...
    """
    jd_text = st.text_area("Descripción del Cargo", value=default_jd, height=150)

# --- CARGA DE ARCHIVO ---
uploaded_file = st.file_uploader("Sube el Curriculum Vitae (PDF)", type="pdf")

if uploaded_file is not None:
    if st.button("🔍 Analizar Candidato", type="primary"):
        with st.spinner('Leyendo PDF y analizando perfil... 🧠'):
            try:
                # 1. Extraer texto del PDF
                reader = PdfReader(uploaded_file)
                cv_text = ""
                for page in reader.pages:
                    cv_text += page.extract_text()

                # 2. Construir el Prompt
                prompt = f"""
                ACTÚA COMO: Reclutador Experto.
                
                MISIÓN: Analizar el siguiente CV contra la JD provista.
                
                ---
                DESCRIPCIÓN DEL CARGO (JD):
                {jd_text}
                ---
                
                CV DEL CANDIDATO:
                {cv_text}
                ---
                
                Genera un reporte estructurado en Markdown con:
                1. Decisión (Avanza/Descarta) y Puntaje de Ajuste (0-100%).
                2. Tabla de cumplimiento de requisitos clave.
                3. Fortalezas y Debilidades (Gaps).
                4. 3 Preguntas sugeridas para la entrevista técnica.
                """

                # 3. Llamar a la IA
                response = model.generate_content(prompt)
                
                # 4. Mostrar resultado
                st.success("¡Análisis Completado!")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

