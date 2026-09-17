"""Dashboard — KPIs reales desde SQLite + API, alertas CWSI y refresco."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import database as db
import api_client as api
from modulos.theme import plotly_layout, plotly_colors, status_colors


def render():
    st.title("Dashboard")
    st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    zonas_df = db.get_zonas()
    lect_df  = db.get_lecturas(sensor_tipo="humedad_10cm", limit=100)
    dec_df   = db.get_decisiones()
    ej_df    = db.get_ejecuciones(limit=50)
    irr_st   = api.get_irrigation_status()
    campo    = api.get_field("field-001")

    # ── Alertas ───────────────────────────────────────────────────────────────
    alertas = db.get_alertas_zonas()
    if alertas:
        st.subheader("Alertas hídricas")
        for a in alertas:
            if a["nivel"] == "critico":
                st.error(a["mensaje"])
            elif a["nivel"] == "alto":
                st.warning(a["mensaje"])
            else:
                st.info(a["mensaje"])
    else:
        st.success("Sin alertas activas — CWSI y humedad dentro de umbrales.")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.subheader("KPIs en tiempo real")
    c1, c2, c3, c4, c5 = st.columns(5)
    hum_prom  = zonas_df["humedad10"].mean() if not zonas_df.empty else 0
    cwsi_prom = zonas_df["cwsi"].mean()      if not zonas_df.empty else 0
    
    c1.metric("Humedad media 10 cm", f"{hum_prom:.1f} %")
    c2.metric(
        "CWSI promedio", f"{cwsi_prom:.2f}",
        delta="Crítico" if cwsi_prom > 0.5 else "Normal",
        delta_color="inverse" if cwsi_prom > 0.5 else "normal",
    )
    c3.metric("Decisiones RL", str(len(dec_df)))
    c4.metric("Riegos ejecutados", str(len(ej_df)))
    c5.metric("Zonas monitoreadas", str(len(zonas_df)))

    st.divider()

    # ── Info de campo + gráfico de humedad ───────────────────────────────────
    col_info, col_bar = st.columns([1, 1])

    with col_info:
        st.subheader("Campo agrícola")
        if campo and "name" in campo:
            st.markdown(f"""
| Parámetro | Valor |
|---|---|
| **Nombre** | {campo.get('name', '—')} |
| **Cultivo** | {campo.get('cropName', '—')} |
| **Variedad** | {campo.get('cropVariety', '—')} |
| **Etapa** | {campo.get('cropStage', '—')} |
| **Área** | {campo.get('areaHectares', '—')} ha |
| **Suelo** | {campo.get('soilType', '—')} |
| **Riego** | {campo.get('irrigationMethod', '—')} |
""")
            st.caption("Fuente: API FastAPI")
        else:
            st.markdown("""
| Parámetro | Valor |
|---|---|
| **Nombre** | Campo San Pablo Sector A |
| **Cultivo** | Maíz Amarillo Duro |
| **Área** | 150.5 ha |
| **Riego** | Pivote Central VRI |
""")
            st.caption("Fuente: SQLite — API no disponible")

    with col_bar:
        st.subheader("Humedad 10 cm por zona")
        if not zonas_df.empty:
            colors = status_colors()
            fig = go.Figure(go.Bar(
                x=zonas_df["sector"].tolist(),
                y=zonas_df["humedad10"].tolist(),
                marker_color=[
                    colors["success"] if h > 27 else colors["warning"]
                    for h in zonas_df["humedad10"]
                ],
                text=[f"{h:.1f}%" for h in zonas_df["humedad10"]],
                textposition="outside",
            ))
            fig.add_hline(
                y=25, 
                line_dash="dash", 
                line_color=colors["error"],
                annotation_text="PMP 25%",
                annotation_font_color=colors["error"]
            )
            fig.update_layout(
                yaxis_range=[0, 50],
                yaxis_title="Humedad (%)",
                **plotly_layout(height=280, margin=dict(t=10, b=10)),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Tendencia temporal ────────────────────────────────────────────────────
    st.subheader("Tendencia de humedad — últimas 48 h")
    if not lect_df.empty:
        lect_df["timestamp"] = pd.to_datetime(lect_df["timestamp"])
        fig2 = px.line(
            lect_df, x="timestamp", y="valor", color="zona_id",
            labels={"valor": "Humedad (%)", "timestamp": "Hora", "zona_id": "Zona"},
            color_discrete_sequence=plotly_colors(),
        )
        colors = status_colors()
        fig2.add_hline(
            y=25, 
            line_dash="dash", 
            line_color=colors["error"],
            annotation_text="PMP",
            annotation_font_color=colors["error"]
        )
        fig2.update_layout(**plotly_layout(height=320, margin=dict(t=20, b=10)))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Estado del sistema + tabla de zonas ───────────────────────────────────
    col_st, col_z = st.columns([1, 2])

    with col_st:
        st.subheader("Sistema de riego")
        if irr_st:
            st.metric("Estado", "Operativo" if irr_st.get("systemOperational") else "Falla")
            st.metric("Presión", f"{irr_st.get('waterPressureBar', '—')} bar")
            st.metric("Flujo", f"{irr_st.get('flowRateLpm', 0)} L/min")
            st.metric("Hardware", "Conectado" if irr_st.get("hardwareConnected") else "Desconectado")
        else:
            st.info("API offline — sistema en modo local.")

    with col_z:
        st.subheader("Resumen de zonas")
        if not zonas_df.empty:
            cols_show = ["sector", "humedad10", "temp_canopia", "cwsi", "dosis_mm", "tipo_suelo"]
            df_show   = zonas_df[cols_show].copy()
            df_show.columns = ["Zona", "Hum. 10 cm (%)", "Temp. Canopía (°C)",
                               "CWSI", "Dosis RL (mm)", "Tipo de suelo"]
            st.dataframe(
                df_show.style.background_gradient(subset=["CWSI"], cmap="RdYlGn_r"),
                use_container_width=True, hide_index=True,
            )

    if st.button("Actualizar datos"):
        st.rerun()