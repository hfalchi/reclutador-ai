import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- 1. CONFIGURACIÓN DE LA VACANTE (JD) ---
# PEGA AQUÍ ABAJO LA DESCRIPCIÓN DEL CARGO QUE QUIERES QUE APAREZCA POR DEFECTO.
# (Mantén las tres comillas al principio y al final)
JD_PREDEFINIDA = """
TITULO DEL CARGO: [Escribe aquí el nombre del cargo, ej: Ejecutivo de Ventas]

RESPONSABILIDADES:
- [Pega aquí las responsabilidades...]
- ...

REQUISITOS EXCLUYENTES:
- [Pega aquí los requisitos...]
- ...

HABILIDADES DESEABLES:
- [Pega aquí lo deseable...]
"""

# --- 2. CONFIGURACIÓN DE LA APP Y CLAVES ---
st.set_page_config(page_title="AI Recruiter", page_icon="👔", layout="centered")

# Intentamos obtener la clave desde los secretos de Streamlit (Nube)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # Si quieres probar en tu PC sin configurar secrets, descomenta la línea de abajo:
    # api_key = "TU_CLAVE_AIza_AQUI"
    st.error("⚠️ No se encontró la API Key. Configúrala en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') 

# --- 3. INTERFAZ DE USUARIO ---
st.title("🤖 Asistente de Selección")
st.markdown("Revisión inteligente de perfiles contra la vacante activa.")

# SECCIÓN A: La Descripción del Cargo (Ya rellena pero editable)
with st.expander("📝 Ver o Editar Descripción del Cargo (JD)", expanded=False):
    st.info("ℹ️ Puedes modificar este texto si la vacante ha cambiado.")
    # Aquí usamos la variable JD_PREDEFINIDA como valor inicial
    jd_actual = st.text_area("Descripción de la Vacante", value=JD_PREDEFINIDA, height=250)

# SECCIÓN B: Carga del CV
st.subheader("Cargar Candidato")
uploaded_file = st.file_uploader("Sube el Curriculum Vitae (PDF)", type="pdf")

# --- 4. LÓGICA DE ANÁLISIS ---
if uploaded_file is not None:
    # Botón de acción
    if st.button("Analizar Candidato", type="primary"):
        with st.spinner('Leyendo documento y analizando... 🧠'):
            try:
                # A) Extraer texto del PDF
                reader = PdfReader(uploaded_file)
                cv_text = ""
                for page in reader.pages:
                    cv_text += page.extract_text()

                # B) Crear el Prompt (Usamos jd_actual, que es lo que hay en la caja de texto)
                prompt = f"""
                ROL: Eres un experto en Selección de Personal (Recruiter).
                TAREA: Analiza el siguiente CV basándote ESTRICTAMENTE en la Descripción del Cargo (JD) proporcionada.
                
                ---
                DESCRIPCIÓN DEL CARGO (JD):
                {jd_actual}
                ---
                
                CV DEL CANDIDATO:
                {cv_text}
                ---
                
                SALIDA ESPERADA (Formato Markdown):
                1. **DECISIÓN FINAL:** (🟢 AVANZA / 🟡 REVISAR / 🔴 DESCARTAR) + Breve justificación.
                2. **PUNTAJE DE AJUSTE:** (0-100%).
                3. **TABLA DE REQUISITOS:** Lista los requisitos clave de la JD y marca si el CV los cumple (✅/❌) con evidencia.
                4. **OBSERVACIONES:** Fortalezas principales y Riesgos detectados.
                5. **PREGUNTAS SUGERIDAS:** 3 preguntas técnicas para la entrevista.
                """

                # C) Llamar a Gemini
                response = model.generate_content(prompt)
                
                # D) Mostrar resultado
                st.success("Análisis Completado")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Ocurrió un error al procesar: {e}")
