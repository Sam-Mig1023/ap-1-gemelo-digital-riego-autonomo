"""Gemelo Digital — visualización 3D georreferenciada + mapa 2D desde SQLite."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import database as db
from modulos.theme import plotly_layout, plotly_colors, status_colors


def _color_estres(cwsi: float) -> str:
    colors = status_colors()
    if cwsi < 0.3:
        return colors["success"]
    if cwsi < 0.6:
        return colors["warning"]
    return colors["error"]


def _zonas_list():
    df = db.get_zonas()
    return [] if df.empty else df.to_dict("records")


def _mapa_campo(zonas: list, capa: str) -> go.Figure:
    pos = {"NW": (0, 1), "NE": (1, 1), "SW": (0, 0), "SE": (1, 0)}
    fig = go.Figure()

    for z in zonas:
        sector = z["sector"]
        if sector not in pos:
            continue
        x0, y0 = pos[sector]
        x1, y1 = x0 + 0.95, y0 + 0.95

        if capa == "Estrés Hídrico (CWSI)":
            val   = float(z["cwsi"])
            color = _color_estres(val)
            label = f"CWSI: {val:.2f}"
        elif capa == "Humedad Suelo (10 cm)":
            val   = float(z["humedad10"])
            colors_list = plotly_colors()
            color = colors_list[0] if val > 28 else status_colors()["warning"]
            label = f"H: {val:.1f}%"
        else:
            val   = float(z["dosis_mm"])
            color = "#7c3aed"
            label = f"Dosis: {val:.1f} mm"

        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=color, opacity=0.75,
                      line_color="rgba(0,0,0,0.3)", line_width=2)
        fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2 + 0.12,
                           text=f"<b>{sector}</b>", showarrow=False,
                           font=dict(color="white", size=18))
        fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2 - 0.12,
                           text=label, showarrow=False,
                           font=dict(color="white", size=13))

    fig.add_shape(type="circle", x0=0.8, y0=0.8, x1=1.2, y1=1.2,
                  fillcolor="#64748b", opacity=0.9,
                  line_color="#94a3b8", line_width=2)
    fig.add_annotation(x=1, y=1, text="VRI", showarrow=False,
                       font=dict(color="white", size=11, family="monospace"))
    fig.update_xaxes(visible=False, range=[-0.05, 2])
    fig.update_yaxes(visible=False, range=[-0.05, 2])
    fig.update_layout(
        title="Campo San Pablo Sector A — 150.5 ha",
        **plotly_layout(height=400, margin=dict(t=50, b=10, l=10, r=10)),
    )
    return fig


def render():
    st.title("Gemelo Digital 3D")
    st.caption("Visualización georreferenciada (pydeck) y mapa 2D — datos de SQLite")

    zonas = _zonas_list()
    if not zonas:
        st.warning("No hay zonas en la base de datos local.")
        return

    # ── Vista 3D principal ────────────────────────────────────────────────────
    from modulos.visualizacion_3d import mostrar_gemelo_3d
    mostrar_gemelo_3d(zonas)

    st.divider()

    # ── Vista 2D complementaria ───────────────────────────────────────────────
    with st.expander("Vista 2D por cuadrantes", expanded=False):
        capa = st.radio(
            "Capa de visualización",
            ["Estrés Hídrico (CWSI)", "Humedad Suelo (10 cm)", "Dosis RL Recomendada"],
            horizontal=True,
            key="gemelo2d_capa",
        )
        st.plotly_chart(_mapa_campo(zonas, capa), use_container_width=True)

    st.divider()

    # ── Detalle por zona ──────────────────────────────────────────────────────
    st.subheader("Detalle por zona")
    zona_sel = st.selectbox("Zona", [z["nombre"] for z in zonas])
    z = next(x for x in zonas if x["nombre"] == zona_sel)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{z['nombre']}**")
        st.markdown(f"""
| Parámetro | Valor |
|---|---|
| **Área** | {z['area_ha']} ha |
| **Temp. Canopía** | {z['temp_canopia']} °C |
| **CWSI** | {z['cwsi']} |
| **Dosis RL** | {z['dosis_mm']} mm |
""")
        cwsi = float(z["cwsi"])
        if cwsi < 0.3:
            st.success("Sin estrés hídrico")
        elif cwsi < 0.6:
            st.warning("Estrés moderado — riego recomendado")
        else:
            st.error("Estrés crítico — riego urgente")

    with col2:
        perfiles = pd.DataFrame({
            "Profundidad": ["10 cm", "30 cm", "60 cm"],
            "Humedad (%)": [z["humedad10"], z["humedad30"], z["humedad60"]],
        })
        fig_perf = px.bar(
            perfiles, x="Profundidad", y="Humedad (%)",
            color="Humedad (%)",
            color_continuous_scale=["#dc2626", "#d97706", "#16a34a"],
            range_color=[20, 45], text_auto=True,
            title="Perfil de humedad por profundidad",
        )
        colors = status_colors()
        fig_perf.add_hline(
            y=25, 
            line_dash="dash", 
            line_color=colors["error"],
            annotation_text="PMP 25%",
            annotation_font_color=colors["error"]
        )
        fig_perf.update_layout(
            coloraxis_showscale=False,
            **plotly_layout(height=280, margin=dict(t=40, b=20)),
        )
        st.plotly_chart(fig_perf, use_container_width=True)

    st.divider()

    # ── Resumen general ───────────────────────────────────────────────────────
    st.subheader("Resumen de zonas")
    df_zonas = pd.DataFrame([{
        "Zona":              z["sector"],
        "Humedad 10 cm (%)": z["humedad10"],
        "Humedad 30 cm (%)": z["humedad30"],
        "Humedad 60 cm (%)": z["humedad60"],
        "Temp. Canopía (°C)":z["temp_canopia"],
        "CWSI":              z["cwsi"],
        "Dosis RL (mm)":     z["dosis_mm"],
    } for z in zonas])
    st.dataframe(
        df_zonas.style
            .background_gradient(subset=["CWSI"],              cmap="RdYlGn_r")
            .background_gradient(subset=["Humedad 10 cm (%)"], cmap="Blues"),
        use_container_width=True, hide_index=True,
    )