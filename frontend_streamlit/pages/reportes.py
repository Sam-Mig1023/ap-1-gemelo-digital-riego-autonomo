"""
Reportes — PDF/Word/Excel reales generados en Python
Patrón: gemelo_digital_minero/modules/reportes.py del profesor
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import database as db
import api_client as api
from modulos.auth import has_permission
from modulos import reportes as rep


def render():
    st.title("📄 Generación de Reportes")
    st.caption("Reportes generados directamente en Python con ReportLab, python-docx y openpyxl")

    usuario = st.session_state.usuario
    rol     = usuario["rol"]
    puede   = has_permission(rol, "generar_reportes")

    # ── Panel de generación (patrón tarjetas del minero) ──────────────────────
    st.subheader("📝 Generar Reporte")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div style='background:#dc2626;padding:18px;border-radius:10px;text-align:center'>
            <h3 style='color:white;margin:0'>📄 PDF</h3>
            <p style='color:#fecaca;margin:6px 0 0'>Reporte ejecutivo con KPIs,
            tablas de zonas, decisiones RL y recomendaciones</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Generar PDF", type="primary",
                     use_container_width=True, disabled=not puede):
            with st.spinner("Generando PDF con ReportLab…"):
                try:
                    data = rep.generar_pdf(usuario=f"{usuario['nombre']} {usuario['apellido']}")
                    db.log_bitacora(usuario["user_id"], "GENERAR_PDF",
                                    "Reporte ejecutivo generado")
                    st.download_button(
                        "⬇️ Descargar PDF",
                        data=data,
                        file_name=f"Reporte_VRI_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error generando PDF: {e}")

    with c2:
        st.markdown("""
        <div style='background:#2563eb;padding:18px;border-radius:10px;text-align:center'>
            <h3 style='color:white;margin:0'>📝 Word</h3>
            <p style='color:#bfdbfe;margin:6px 0 0'>Informe técnico detallado
            con tablas de zonas, decisiones y conclusiones</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Generar Word", type="primary",
                     use_container_width=True, disabled=not puede):
            with st.spinner("Generando Word con python-docx…"):
                try:
                    data = rep.generar_word(usuario=f"{usuario['nombre']} {usuario['apellido']}")
                    db.log_bitacora(usuario["user_id"], "GENERAR_WORD",
                                    "Informe técnico generado")
                    st.download_button(
                        "⬇️ Descargar Word",
                        data=data,
                        file_name=f"Informe_VRI_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error generando Word: {e}")

    with c3:
        st.markdown("""
        <div style='background:#16a34a;padding:18px;border-radius:10px;text-align:center'>
            <h3 style='color:white;margin:0'>📊 Excel</h3>
            <p style='color:#bbf7d0;margin:6px 0 0'>Datos completos con múltiples
            hojas: Zonas, Sensores, Decisiones RL, Ejecuciones y KPIs</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Generar Excel", type="primary",
                     use_container_width=True, disabled=not puede):
            with st.spinner("Generando Excel con openpyxl…"):
                try:
                    data = rep.generar_excel(usuario=f"{usuario['nombre']} {usuario['apellido']}")
                    db.log_bitacora(usuario["user_id"], "GENERAR_EXCEL",
                                    "Reporte Excel multi-hoja generado")
                    st.download_button(
                        "⬇️ Descargar Excel",
                        data=data,
                        file_name=f"Datos_VRI_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error generando Excel: {e}")

    if not puede:
        st.warning(f"⚠️ El rol **{rol}** no tiene permiso para generar reportes.")

    st.divider()

    # ── Vista previa de datos ─────────────────────────────────────────────────
    st.subheader("📊 Vista Previa — Datos a incluir en el reporte")

    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Zonas", "🤖 Decisiones RL",
                                       "💧 Ejecuciones", "📡 Últimas Lecturas"])

    with tab1:
        zonas_df = db.get_zonas()
        if not zonas_df.empty:
            st.dataframe(
                zonas_df.style.background_gradient(subset=["cwsi"], cmap="RdYlGn_r"),
                use_container_width=True, hide_index=True
            )

    with tab2:
        dec_df = db.get_decisiones()
        if not dec_df.empty:
            dec_df["confianza_%"] = (dec_df["confianza"] * 100).round(1)
            st.dataframe(dec_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sin decisiones registradas aún.")

    with tab3:
        ej_df = db.get_ejecuciones()
        if not ej_df.empty:
            st.dataframe(ej_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sin ejecuciones registradas aún.")

    with tab4:
        lect_df = db.get_lecturas(limit=40)
        if not lect_df.empty:
            st.dataframe(lect_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Descarga CSV directa (como el proyecto educativo) ─────────────────────
    st.subheader("⬇️ Descarga Rápida CSV")
    zonas_df = db.get_zonas()
    if not zonas_df.empty:
        csv = zonas_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Descargar Zonas CSV",
            data=csv,
            file_name=f"zonas_vri_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
