import json
import time
from datetime import date, timedelta

import streamlit as st
from openai import OpenAI

# ----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AeroSubsa - Planificador Inteligente de Viajes",
    page_icon="✈️",
    layout="centered",
)

AZUL = "#103580"
ROJO = "#db0032"

# ----------------------------------------------------------------------------
# ESTILOS PERSONALIZADOS (paleta institucional AeroPlan)
# ----------------------------------------------------------------------------
st.markdown(
    f"""
<style>
    .stApp {{
        background-color: #f5f6fa;
    }}
    .aeroplan-header {{
        background: linear-gradient(135deg, {AZUL} 0%, #1a4bb8 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }}
    .aeroplan-header h1 {{
        color: white;
        margin-bottom: 0.2rem;
        font-size: 2.1rem;
    }}
    .aeroplan-header p {{
        color: #d8e0ff;
        font-size: 1rem;
        margin: 0;
    }}
    .aeroplan-badge {{
        display: inline-block;
        background-color: {ROJO};
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        letter-spacing: 0.5px;
    }}
    .section-card {{
        background-color: white;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        border-left: 6px solid {AZUL};
        box-shadow: 0 2px 8px rgba(16, 53, 128, 0.08);
    }}
    .section-card h3 {{
        color: {AZUL};
        margin-top: 0;
    }}
    .warning-box {{
        background-color: #fff2f2;
        border: 1.5px solid {ROJO};
        border-radius: 12px;
        padding: 1rem 1.3rem;
        color: #7a0021;
        font-size: 0.9rem;
        margin-top: 1.5rem;
    }}
    div.stButton > button {{
        background-color: {ROJO};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: 0.2s;
    }}
    div.stButton > button:hover {{
        background-color: #a80027;
        color: white;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {AZUL};
        font-weight: 600;
    }}

    div[data-testid="stSelectbox"]
    div[data-baseweb="select"] > div {{
        background-color: {AZUL} !important;
        border: 1px solid {AZUL} !important;
        border-radius: 8px !important;
    }}

    /* Clase interna SingleValue de BaseWeb */
    div[data-testid="stSelectbox"]
    div[data-baseweb="select"]
    div[class*="singleValue"] {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* Cubre el texto visible si Streamlit lo renderiza dentro de otro div */
    div[data-testid="stSelectbox"]
    div[data-baseweb="select"] > div > div {{
        color: #ffffff !important;
    }}

    div[data-testid="stSelectbox"]
    div[data-baseweb="select"] > div > div > div {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* Flecha del select cerrado */
    div[data-testid="stSelectbox"]
    div[data-baseweb="select"] svg {{
        color: #ffffff !important;
        fill: #ffffff !important;
    }}

    /* ---------------------------------------------------------
       FECHA DE SALIDA Y FECHA DE REGRESO
       --------------------------------------------------------- */

    div[data-testid="stDateInput"] {{
        color: #ffffff !important;
    }}

    div[data-testid="stDateInput"]
    div[data-baseweb="input"] {{
        background-color: {AZUL} !important;
        border: 1px solid {AZUL} !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stDateInput"] input {{
        background-color: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
        caret-color: #ffffff !important;
    }}

    /* También cubre inputs internos creados por BaseWeb */
    div[data-testid="stDateInput"]
    div[data-baseweb="input"] input[type="text"] {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    div[data-testid="stDateInput"] svg {{
        color: #ffffff !important;
        fill: #ffffff !important;
    }}

    /* ---------------------------------------------------------
       MENÚS DESPLEGABLES
       Se mantienen con texto oscuro sobre fondo claro
       --------------------------------------------------------- */

    div[data-baseweb="popover"] [role="listbox"],
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] [role="option"] div,
    div[data-baseweb="popover"] [role="option"] span {{
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
    }}

    .st-emotion-cache-1wda8v2, .st-emotion-cache-1eamic5 {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }}
    .st-emotion-cache-m4cypv {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }}
    .st-emotion-cache-1ia0tqe, .st-emotion-cache-14pzdj6  {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }}
   </style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# DATOS SIMULADOS DE LA AEROLÍNEA
# ----------------------------------------------------------------------------
RUTAS_SIMULADAS = [
    "Ciudad de México",
    "Cancún",
    "Monterrey",
    "Guadalajara",
    "Mérida",
]

TARIFA_BASE = {
    "Económico": 2200,
    "Equilibrado": 3800,
    "Cómodo": 6500,
}

# ----------------------------------------------------------------------------
# CLIENTE DE IA
# ----------------------------------------------------------------------------
# TODO

# ----------------------------------------------------------------------------
# ENCABEZADO
# ----------------------------------------------------------------------------
st.markdown(
    f"""
<div class="aeroplan-header">
    <div class="aeroplan-badge">PROTOTIPO ACADÉMICO</div>
    <h1>✈️ AeroSubsa</h1>
    <p>Planea tu próximo viaje con ayuda de la inteligencia artificial</p>
</div>
""",
    unsafe_allow_html=True,
)

st.caption(
    "AeroPlan Airlines · Tu asistente inteligente para planificar viajes (aerolínea ficticia)"
)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

# ----------------------------------------------------------------------------
# PANTALLA 1 — FORMULARIO
# ----------------------------------------------------------------------------
with st.form("formulario_viaje"):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🧭 Cuéntanos sobre tu viaje")

    col1, col2 = st.columns(2)
    with col1:
        origen = st.selectbox("Origen", RUTAS_SIMULADAS, index=0)
    with col2:
        destinos_disponibles = [r for r in RUTAS_SIMULADAS if r != origen]
        destino = st.selectbox("Destino", destinos_disponibles, index=0)

    col3, col4 = st.columns(2)
    with col3:
        salida = st.date_input(
            "Fecha de salida", value=date.today() + timedelta(days=30)
        )
    with col4:
        regreso = st.date_input(
            "Fecha de regreso", value=date.today() + timedelta(days=35)
        )

    col5, col6 = st.columns(2)
    with col5:
        pasajeros = st.number_input(
            "Número de pasajeros", min_value=1, max_value=10, value=2
        )
    with col6:
        presupuesto = st.number_input(
            "Presupuesto aproximado (MXN)", min_value=1000, step=500, value=25000
        )

    estilo = st.radio(
        "Preferencia de viaje", ["Económico", "Equilibrado", "Cómodo"], horizontal=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 Generar mi viaje")

# ----------------------------------------------------------------------------
# PANTALLA 2 — PROCESAMIENTO Y PANTALLA 3 — RESULTADO
# ----------------------------------------------------------------------------
if submitted:
    if regreso <= salida:
        st.error("La fecha de regreso debe ser posterior a la fecha de salida.")
    else:
        noches = (regreso - salida).days
        client, model_name = get_client()

        if client is None:
            st.error(
                "No se encontró una clave de API configurada en los secretos de la aplicación."
            )
        else:
            with st.spinner("✨ Analizando tus preferencias de viaje..."):
                try:
                    prompt = construir_prompt(
                        origen,
                        destino,
                        salida,
                        regreso,
                        pasajeros,
                        presupuesto,
                        estilo,
                        noches,
                    )
                    propuesta = generar_propuesta_ia(client, model_name, prompt)
                    st.session_state.resultado = {
                        "propuesta": propuesta,
                        "origen": origen,
                        "destino": destino,
                        "salida": salida,
                        "regreso": regreso,
                        "pasajeros": pasajeros,
                        "presupuesto": presupuesto,
                        "estilo": estilo,
                        "noches": noches,
                    }
                except Exception as e:
                    st.error(f"Ocurrió un error al generar la propuesta: {e}")
                    st.session_state.resultado = None

if st.session_state.resultado:
    r = st.session_state.resultado
    propuesta = r["propuesta"]

    st.markdown(
        f"""
    <div class="section-card">
        <h3>✈️ Tu viaje: {r['origen']} → {r['destino']}</h3>
        <p>{propuesta.get('resumen', '')}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
        <div class="section-card">
            <h3>📅 Información del viaje</h3>
            <p><b>Salida:</b> {r['salida'].strftime('%d/%m/%Y')}<br>
            <b>Regreso:</b> {r['regreso'].strftime('%d/%m/%Y')}<br>
            <b>Duración:</b> {r['noches']} noches<br>
            <b>Pasajeros:</b> {r['pasajeros']}<br>
            <b>Presupuesto:</b> ${r['presupuesto']:,.0f} MXN</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="section-card">
            <h3>🧳 Estilo de viaje</h3>
            <p style="font-size:1.3rem; font-weight:700; color:{ROJO};">{r['estilo']}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-card"><h3>🗓️ Itinerario recomendado</h3>',
        unsafe_allow_html=True,
    )
    for dia in propuesta.get("itinerario", []):
        st.markdown(f"**{dia.get('dia')}** — {dia.get('actividad')}")
    st.markdown("<​/div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-card"><h3>📍 Actividades recomendadas</h3>',
        unsafe_allow_html=True,
    )
    for rec in propuesta.get("recomendaciones", []):
        st.markdown(f"- {rec}")
    st.markdown("<​/div>", unsafe_allow_html=True)

    presupuesto_dist = calcular_presupuesto_estimado(
        r["presupuesto"], r["estilo"], r["pasajeros"]
    )
    st.markdown(
        '<div class="section-card"><h3>💰 Presupuesto estimado</h3>',
        unsafe_allow_html=True,
    )
    for concepto, monto in presupuesto_dist.items():
        st.markdown(f"- **{concepto}:** ${monto:,.0f} MXN")
    st.markdown("<​/div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="warning-box">
    ⚠️ <b>Aviso:</b> La información presentada es una simulación generada con
    fines académicos. No representa tarifas, disponibilidad, itinerarios ni
    reservaciones reales de AeroPlan Airlines ni de ninguna aerolínea existente.
    </div>
    """,
        unsafe_allow_html=True,
    )
