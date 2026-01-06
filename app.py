import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- 1. CONFIGURACIÓN DE LA VACANTE (JD) ---
# PEGA AQUÍ ABAJO LA DESCRIPCIÓN DEL CARGO QUE QUIERES QUE APAREZCA POR DEFECTO.
# (Mantén las tres comillas al principio y al final)
JD_PREDEFINIDA = """
TITULO DEL CARGO: Analista de Control de Gestión (Servicios, Proyectos y Soporte)

Descripción de la empresa
En Envision, somos una empresa líder en tecnología en Chile, Microsoft Gold Partner, y trabajamos con algunas de las empresas más grandes del país, impulsando proyectos y servicios tecnológicos de alto impacto. Buscamos un/a Analista de Control de Gestión que asegure el orden, trazabilidad y control de nuestras propuestas, proyectos en ejecución y operación de soporte, levantando alertas oportunas y generando visibilidad clara del consumo y cumplimiento.

Objetivo del cargo
Asegurar el control y seguimiento de la operación de servicios (proyectos llave en mano, bolsas de horas y soporte), manteniendo información crítica actualizada, monitoreando consumo de HH, avances, SLA y garantías, y levantando alertas para una toma de decisiones rápida y basada en datos.

PRINCIPALES RESPONSABILIDADES
Control y seguimiento de propuestas y proyectos
Mantener actualizadas todas las propuestas vendidas (proyectos, bolsa de horas, soportes), registrando hitos, HH estimadas y días estimados al momento de la venta.
Mantener actualizadas las propuestas en curso post levantamiento, registrando hitos, HH estimadas y días estimados, junto con el equipo técnico asignado.
Registrar y controlar fechas de adjudicación versus fecha de kick-off de cada proyecto.
Realizar entrevistas semanales con el equipo técnico para registrar imputación de HH y etapa de avance de los proyectos.
Levantar alertas cuando los hitos alcancen el 50% y 75% de las HH estimadas post levantamiento.
Mantener registro y seguimiento de correos de cierre de cada proyecto (JP con cliente), independiente del estatus de facturación.
Mantener actualizado el registro y seguimiento de fechas de inicio y término de garantías.
Mantener actualizado el equipo técnico con HH contratadas disponibles, en coordinación con RR.HH.

Control y seguimiento de Soporte / Mesa de ayuda
Revisión diaria de cumplimiento de SLA de soportes.
Revisión mensual del estatus de la plataforma de soportes para informes de horas a clientes.
Reunión semanal de seguimiento de soporte, con análisis de consumo y alertas.

REQUISITOS EXCLUYENTES
Formación: Control de Gestión o Ingeniería Comercial (o carrera afín con foco en control/gestión).
Al menos 2 años de experiencia laboral en cargos similares
Alta prolijidad y capacidad de mantener información crítica actualizada y consistente.
Manejo intermedio/avanzado de Excel/Google Sheets (idealmente con tablas dinámicas y control de indicadores).
Habilidad para coordinar entrevistas, recopilar información y generar alertas con criterio.

HABILIDADES DESEABLES (no excluyente)
Experiencia previa en empresas de tecnología y/o en control de gestión en empresas de servicios (consultoría, software factory, outsourcing, operación de soporte).
Familiaridad con conceptos de HH, hitos, SLA, garantías, operación de mesa de ayuda y seguimiento de consumo.
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


