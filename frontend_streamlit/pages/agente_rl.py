"""Agente RL — Inferencia PPO, aprobación/anulación y persistencia en SQLite"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import database as db
import api_client as api
from modulos.auth import has_permission
from modulos.rl_local import infer_vri_local


def _gauge(confianza: float):
    color = "#22c55e" if confianza > 0.9 else "#f59e0b" if confianza > 0.75 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confianza * 100,
        title={"text": "Confianza del Agente (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar":  {"color": color},
            "steps": [
                {"range": [0,  75], "color": "#1e293b"},
                {"range": [75, 90], "color": "#292524"},
                {"range": [90,100], "color": "#14532d"},
            ],
            "threshold": {"line": {"color": "#22c55e", "width": 4},
                          "thickness": 0.75, "value": 90},
        },
        number={"suffix": "%"},
    ))
    fig.update_layout(paper_bgcolor="#1e293b", font_color="#e2e8f0",
                      height=240, margin=dict(t=30, b=10))
    return fig


def _shap_chart(shap_values: list):
    features = [s["feature"] for s in shap_values]
    impacts  = [s["impact"]  for s in shap_values]
    fig = go.Figure(go.Bar(
        y=features, x=impacts, orientation="h",
        marker_color=["#22c55e" if v >= 0 else "#ef4444" for v in impacts],
        text=[f"{v:+.2f}" for v in impacts], textposition="outside",
    ))
    fig.update_layout(
        title="📊 Valores SHAP — Explicabilidad",
        xaxis_title="Impacto en la decisión",
        plot_bgcolor="#0f172a", paper_bgcolor="#1e293b",
        font_color="#e2e8f0", height=240, margin=dict(t=40, b=10),
    )
    return fig


def render():
    st.title("🤖 Agente de Aprendizaje por Refuerzo (PPO)")
    st.caption("Política PPO-VRI-DualReward · Decisiones persistidas en SQLite local")

    usuario  = st.session_state.usuario
    rol      = usuario["rol"]
    zonas_df = db.get_zonas()

    # ── Formulario de inferencia ───────────────────────────────────────────────
    st.subheader("⚡ Inferir Dosis de Riego")
    c1, c2, c3 = st.columns(3)
    zona_opts = zonas_df["nombre"].tolist() if not zonas_df.empty else ["zone-nw"]
    zona_nom  = c1.selectbox("Zona", zona_opts)
    zona_row  = zonas_df[zonas_df["nombre"] == zona_nom].iloc[0] if not zonas_df.empty else {}
    humedad   = c2.number_input("Humedad suelo 10cm (%)", 10.0, 50.0,
                                value=float(zona_row.get("humedad10", 28.0)), step=0.5)
    temp      = c3.number_input("Temperatura canopía (°C)", 15.0, 45.0,
                                value=float(zona_row.get("temp_canopia", 24.0)), step=0.5)

    puede_inferir = has_permission(rol, "inferencia_rl")
    if st.button("🚀 Ejecutar Inferencia RL", type="primary",
                 use_container_width=True, disabled=not puede_inferir):
        zona_id = str(zona_row.get("id", "zone-nw"))
        with st.spinner("Ejecutando política PPO…"):
            dec = api.infer_vri_rates(zona_id, humedad, temp)
            fuente = "API PPO"
            if not dec:
                dec = infer_vri_local(zona_id, humedad, temp)
                fuente = "regla local (API offline)"
        if dec:
            db.save_decision({
                "id":           dec["id"],
                "zona_id":      zona_id,
                "dosis_mm":     dec["recommendedDepthMm"],
                "volumen_m3":   dec["recommendedVolumeM3"],
                "confianza":    dec["confidenceScore"],
                "estado":       "pendiente",
                "razonamiento": dec.get("explanation", {}).get("reasoningText", ""),
                "timestamp":    dec["timestamp"],
            })
            db.log_bitacora(usuario["user_id"], "INFERENCIA_RL",
                            f"Zona {zona_id} — {dec['recommendedDepthMm']} mm ({fuente})")
            st.session_state["ultima_decision"] = {**dec, "zoneId": zona_id}
            st.success(f"✅ Inferencia completada ({fuente}) y guardada en BD")
        else:
            st.error("❌ No se pudo inferir (API y fallback fallaron).")

    # ── Resultado ─────────────────────────────────────────────────────────────
    dec = st.session_state.get("ultima_decision")
    if dec:
        st.divider()
        st.subheader("📋 Resultado de la Decisión RL")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💧 Dosis", f"{dec.get('recommendedDepthMm',0)} mm")
        c2.metric("🪣 Volumen", f"{dec.get('recommendedVolumeM3',0)} m³")
        c3.metric("🎯 Confianza", f"{dec.get('confidenceScore',0)*100:.1f}%")
        c4.metric("🔖 Política", dec.get("policyId","—"))

        v = dec.get("executionWindowHours", {})
        st.info(f"🕐 Ventana óptima: **{v.get('start','—')}** → **{v.get('end','—')}**")

        exp    = dec.get("explanation", {})
        shap   = exp.get("shapValues", [])
        razon  = exp.get("reasoningText", "")

        col_g, col_s = st.columns([1, 2])
        with col_g:
            st.plotly_chart(_gauge(dec.get("confidenceScore", 0)), use_container_width=True)
        with col_s:
            if shap:
                st.plotly_chart(_shap_chart(shap), use_container_width=True)

        if razon:
            st.markdown(f"> 🧠 **Razonamiento IA:** {razon}")

        st.divider()
        st.subheader("✅ Acciones sobre la Decisión")

        col_ap, col_ov = st.columns(2)
        with col_ap:
            st.markdown("**Aprobar decisión**")
            operador = st.text_input("Aprobado por", value=usuario["email"], key="aprobador")
            puede_aprobar = has_permission(rol, "aprobar_decisiones")
            if st.button("✅ Aprobar", disabled=not puede_aprobar, use_container_width=True):
                res = api.approve_decision(dec["id"], operador)
                if res:
                    db.update_decision_estado(dec["id"], "aprobado", operador)
                    db.log_bitacora(usuario["user_id"], "APROBAR_DECISION",
                                    f"Decisión {dec['id']} aprobada por {operador}")
                    st.success(f"Decisión aprobada por {operador}")
                else:
                    db.update_decision_estado(dec["id"], "aprobado", operador)
                    st.success(f"Aprobado en BD local (API offline)")
            if not puede_aprobar:
                st.caption(f"⚠️ El rol **{rol}** no puede aprobar decisiones.")

        with col_ov:
            st.markdown("**Anular manualmente**")
            nueva = st.number_input("Nueva dosis (mm)", 0.0, 20.0,
                                    value=float(dec.get("recommendedDepthMm", 5.0)),
                                    step=0.5, key="override_d")
            motivo = st.text_input("Motivo", "Ajuste de campo", key="override_m")
            if st.button("✏️ Anular y sobreescribir", use_container_width=True,
                         disabled=not has_permission(rol, "anular_decisiones")):
                res = api.override_decision(dec["id"], nueva, motivo)
                db.update_decision_estado(dec["id"], "anulado_manual", usuario["username"])
                db.log_bitacora(usuario["user_id"], "ANULAR_DECISION",
                                f"{dec['id']} → {nueva} mm. Motivo: {motivo}")
                if res:
                    st.warning(f"Decisión anulada en API. Nueva dosis: {nueva} mm")
                else:
                    st.warning(f"Anulada en BD local. Nueva dosis: {nueva} mm")
            if not has_permission(rol, "anular_decisiones"):
                st.caption(f"⚠️ El rol **{rol}** no puede anular decisiones.")

    st.divider()

    # ── Historial desde SQLite ─────────────────────────────────────────────────
    st.subheader("🗂️ Historial de Decisiones RL (BD Local)")
    dec_df = db.get_decisiones()
    if not dec_df.empty:
        dec_df["confianza_%"] = (dec_df["confianza"] * 100).round(1)
        cols = ["id", "zona_id", "dosis_mm", "volumen_m3", "confianza_%",
                "estado", "aprobado_por", "timestamp"]
        st.dataframe(dec_df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("Sin decisiones registradas aún. Ejecuta una inferencia.")

    # ── Inferencia batch ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔄 Inferencia en Todas las Zonas")
    if st.button("⚡ Inferir en todas las zonas", use_container_width=True,
                 disabled=not puede_inferir):
        resultados = []
        with st.spinner("Ejecutando PPO en todas las zonas…"):
            for _, z in zonas_df.iterrows():
                d = api.infer_vri_rates(z["id"], z["humedad10"], z["temp_canopia"])
                fuente = "API"
                if not d:
                    d = infer_vri_local(z["id"], z["humedad10"], z["temp_canopia"])
                    fuente = "local"
                if d:
                    db.save_decision({
                        "id": d["id"], "zona_id": z["id"],
                        "dosis_mm": d["recommendedDepthMm"],
                        "volumen_m3": d["recommendedVolumeM3"],
                        "confianza": d["confidenceScore"],
                        "estado": "pendiente",
                        "razonamiento": d.get("explanation", {}).get("reasoningText", ""),
                        "timestamp": d["timestamp"],
                    })
                    resultados.append({
                        "Zona": z["sector"],
                        "Dosis (mm)": d["recommendedDepthMm"],
                        "Volumen (m³)": d["recommendedVolumeM3"],
                        "Confianza (%)": f"{d['confidenceScore']*100:.1f}",
                        "Estado": f"⏳ Pendiente ({fuente})",
                    })
                else:
                    resultados.append({"Zona": z["sector"], "Dosis (mm)": "—",
                                       "Volumen (m³)": "—", "Confianza (%)": "—",
                                       "Estado": "❌ Sin resultado"})
        st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
        st.success("Decisiones guardadas en BD local.")
