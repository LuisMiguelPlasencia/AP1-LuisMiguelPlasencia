import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ——————————————————————————————————————
# 1. Configuración de la página y tema
# ——————————————————————————————————————
st.set_page_config(
    page_title="Dashboard Créditos 13 MBID",
    page_icon="💳",
    layout="wide"
)

# ——————————————————————————————————————
# 2. Caché de datos con el decorador moderno
# ——————————————————————————————————————
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, sep=";")

df = load_data("../data/final/datos_finales.csv")

# ——————————————————————————————————————
# 3. Sidebar de filtros interactivos
# ——————————————————————————————————————
st.sidebar.header("Filtros")
objetivos = st.sidebar.multiselect(
    "Objetivo del Crédito",
    options=df["objetivo_credito"].unique(),
    default=df["objetivo_credito"].unique()
)
estados = st.sidebar.multiselect(
    "Estado del Crédito",
    options=df["estado_credito_N"].unique(),
    default=df["estado_credito_N"].unique()
)
r_min, r_max = st.sidebar.slider(
    "Rango de Importe (€)",
    float(df["importe_solicitado"].min()),
    float(df["importe_solicitado"].max()),
    (
        float(df["importe_solicitado"].quantile(0.05)),
        float(df["importe_solicitado"].quantile(0.95))
    )
)

# Aplicar filtros
df_filt = df[
    df["objetivo_credito"].isin(objetivos) &
    df["estado_credito_N"].isin(estados) &
    df["importe_solicitado"].between(r_min, r_max)
].copy()

# ——————————————————————————————————————
# 4. Preparar columna booleana para 'mora'
# ——————————————————————————————————————
# Asumimos que 'falta_pago' está codificado como 'Y' (sí) y 'N' (no)
df_filt["en_mora"] = df_filt["falta_pago"] == "Y"

# ——————————————————————————————————————
# 5. KPI principales en columnas
# ——————————————————————————————————————
st.header("📊 Visualización de Gráficos - 13MBID")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Créditos", f"{len(df_filt):,}")
c2.metric("Importe Promedio", f"€{df_filt['importe_solicitado'].mean():,.0f}")
c3.metric("Duración Promedio", f"{df_filt['duracion_credito'].mean():.1f} meses")
c4.metric("Clientes en Mora", int(df_filt["en_mora"].sum()))

st.markdown("---")

# ——————————————————————————————————————
# 6. Gráficos organizados en pestañas
# ——————————————————————————————————————
tab1, tab2, tab3 = st.tabs(["Histogramas", "Correlación", "Sunburst"])

with tab1:
    st.subheader("📈 Histogramas")
    colA, colB = st.columns(2)
    with colA:
        hist_obj = px.histogram(
            df_filt,
            x="objetivo_credito",
            color="estado_credito_N",
            barmode="group",
            title="Créditos por Objetivo y Estado",
            labels={"objetivo_credito": "Objetivo", "estado_credito_N": "Estado"}
        )
        st.plotly_chart(hist_obj, use_container_width=True)
    with colB:
        hist_imp = px.histogram(
            df_filt,
            x="importe_solicitado",
            nbins=20,
            title="Importes Solicitados",
            labels={"importe_solicitado": "Importe (€)"}
        )
        st.plotly_chart(hist_imp, use_container_width=True)

with tab2:
    st.subheader("🧮 Mapa de Calor de Correlaciones")
    corr = df_filt[["importe_solicitado", "duracion_credito", "personas_a_cargo"]].corr()
    heatmap = px.imshow(
        corr,
        text_auto=".2f",
        title="Correlaciones (ρ)",
        labels={"color": "ρ"}
    )
    heatmap.update_xaxes(side="top")
    st.plotly_chart(heatmap, use_container_width=True)

with tab3:
    st.subheader("🌐 Sunburst de Importes")
    sunb = px.sunburst(
        df_filt,
        path=["objetivo_credito", "antiguedad_cliente"],
        values="importe_solicitado",
        color="importe_solicitado",
        color_continuous_scale="Blues",
        labels={"objetivo_credito": "Objetivo", "antiguedad_cliente": "Antigüedad"}
    )
    sunb.update_traces(
        hovertemplate="<b>%{label}</b><br>Importe Total: %{value:$,.0f}<br>Parte: %{percentParent:.1%}"
    )
    st.plotly_chart(sunb, use_container_width=True)

st.markdown("---")

# ——————————————————————————————————————
# 7. Detalle de datos y descarga
# ——————————————————————————————————————
with st.expander("Ver Detalle de Datos Filtrados"):
    st.dataframe(df_filt, use_container_width=True)

csv_bytes = df_filt.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Descargar datos filtrados",
    data=csv_bytes,
    file_name="datos_filtrados.csv",
    mime="text/csv"
)

# ——————————————————————————————————————
# 8. Pie de página
# ——————————————————————————————————————
st.markdown("---")
st.caption("Desarrollado por Miguel Plasencia – Práctica 2 | 13 MBID")
