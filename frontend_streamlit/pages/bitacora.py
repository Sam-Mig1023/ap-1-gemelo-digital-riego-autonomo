"""Bitácora de auditoría — filtros, KPIs y CSV."""
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import database as db
from modulos.decoradores import requiere_permiso


@requiere_permiso("ver_bitacora")
def render():
    st.title("📝 Bitácora de Auditoría")
    st.caption("Trazabilidad de accesos, navegación y acciones de riego")

    resumen = db.get_resumen_bitacora(300)
    if not resumen.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Tipos de acción", len(resumen))
        c2.metric("Eventos (muestra)", int(resumen["n"].sum()))
        top = resumen.iloc[0]
        c3.metric("Más frecuente", f"{top['accion']} ({int(top['n'])})")
        fig = px.bar(resumen, x="accion", y="n", title="Eventos por tipo")
        fig.update_layout(
            plot_bgcolor="#0f172a", paper_bgcolor="#1e293b",
            font_color="#e2e8f0", height=260, margin=dict(t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    col_f, col_r = st.columns(2)
    limite = col_f.slider("Últimas N entradas", 10, 500, 100, step=10)
    filtro = col_r.text_input("Filtrar por acción", placeholder="LOGIN, INFERENCIA_RL…")

    df = db.get_bitacora(limit=limite)
    if filtro and not df.empty:
        df = df[df["accion"].str.contains(filtro, case=False, na=False)]

    if not df.empty:
        show = df.copy()
        show.columns = ["Fecha/Hora", "Acción", "Detalle", "Usuario", "Nombre", "Rol"]
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(show)} registros")
        csv = show.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar CSV",
            data=csv,
            file_name=f"bitacora_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay registros en la bitácora aún.")

    if st.button("🔄 Actualizar"):
        st.rerun()
