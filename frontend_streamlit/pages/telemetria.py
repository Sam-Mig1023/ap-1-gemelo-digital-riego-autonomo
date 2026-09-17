"""Telemetría — series desde SQLite; ingestión también persiste local."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import database as db
import api_client as api
from modulos.auth import has_permission


def render():
    st.title("📡 Telemetría de Sensores")
    st.caption("Histórico SQLite + sensores FastAPI cuando está en línea")

    usuario = st.session_state.usuario
    sensors_data = api.get_sensors()
    sensores = sensors_data.get("sensors", []) if sensors_data else []

    st.subheader("🔌 Sensores Activos")
    if sensores:
        rows = []
        for s in sensores:
            lr = s.get("lastReading", {})
            rows.append({
                "ID": s.get("id", "—"),
                "Nombre": s.get("name", "—"),
                "Tipo": s.get("type", "—"),
                "Zona": s.get("zoneId", "—"),
                "Último Valor": f"{lr.get('value', '—')} {lr.get('unit', '')}",
                "Timestamp": lr.get("timestamp", "—"),
                "Estado": "✅ Activo" if s.get("status") == "active" else "⚠️",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Fuente: API")
    else:
        st.info("API sin sensores. Mostrando últimas lecturas de SQLite.")

    puede_ingest = has_permission(usuario["rol"], "ingestar_telemetria")
    with st.expander("📥 Ingresar lectura de sensor"):
        c1, c2, c3, c4 = st.columns(4)
        zona_df = db.get_zonas()
        zonas = zona_df["id"].tolist() if not zona_df.empty else ["zone-nw"]
        zid = c1.selectbox("Zona", zonas)
        sid = c2.selectbox("Tipo", ["humedad_10cm", "temp_canopia"])
        sval = c3.number_input("Valor", 0.0, 100.0, 28.5)
        sunit = c4.selectbox("Unidad", ["%", "°C"])
        if st.button("📤 Guardar lectura", disabled=not puede_ingest):
            db.insert_lectura(zid, sid, sval, sunit)
            res = api.ingest_telemetry([{
                "sensorId": f"{zid}-{sid}",
                "value": sval,
                "unit": sunit,
                "timestamp": datetime.utcnow().isoformat(),
            }])
            db.log_bitacora(usuario["user_id"], "INGESTAR_TELEMETRIA", f"{zid} {sid}={sval}{sunit}")
            if res:
                st.success("✅ Guardada en SQLite y enviada a la API")
            else:
                st.success("✅ Guardada en SQLite (API offline)")
        if not puede_ingest:
            st.caption(f"El rol **{usuario['rol']}** no puede ingresar telemetría.")

    st.divider()
    st.subheader("📈 Series de Tiempo — SQLite")

    tipo = st.selectbox(
        "Métrica",
        ["Humedad del Suelo (10 cm)", "Temperatura de Canopía"],
    )
    sensor = "humedad_10cm" if "Humedad" in tipo else "temp_canopia"
    ylabel = "Humedad (%)" if sensor == "humedad_10cm" else "Temperatura (°C)"
    lect = db.get_lecturas(sensor_tipo=sensor, limit=400)

    if lect.empty:
        st.warning("No hay lecturas en SQLite.")
    else:
        lect["timestamp"] = pd.to_datetime(lect["timestamp"])
        fig = px.line(
            lect, x="timestamp", y="valor", color="zona_id",
            labels={"valor": ylabel, "timestamp": "Hora", "zona_id": "Zona"},
            color_discrete_sequence=["#22c55e", "#3b82f6", "#f59e0b", "#ec4899"],
            title=f"{tipo} — datos reales de BD",
        )
        if sensor == "humedad_10cm":
            fig.add_hline(y=25, line_dash="dash", line_color="#ef4444", annotation_text="PMP")
        fig.update_layout(
            plot_bgcolor="#0f172a", paper_bgcolor="#1e293b",
            font_color="#e2e8f0", height=360, margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("🔥 Mapa de calor — humedad 10 cm (últimas 24 lecturas / zona)")
        hum = db.get_lecturas(sensor_tipo="humedad_10cm", limit=200)
        if not hum.empty:
            hum["timestamp"] = pd.to_datetime(hum["timestamp"])
            hum = hum.sort_values("timestamp")
            pivot = hum.pivot_table(index="zona_id", columns="timestamp", values="valor", aggfunc="mean")
            pivot = pivot.iloc[:, -24:]
            fig_hm = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[t.strftime("%H:%M") for t in pivot.columns],
                y=list(pivot.index),
                colorscale="RdYlGn",
                colorbar=dict(title="Humedad (%)"),
            ))
            fig_hm.update_layout(
                plot_bgcolor="#0f172a", paper_bgcolor="#1e293b",
                font_color="#e2e8f0", height=280, margin=dict(t=30, b=20),
            )
            st.plotly_chart(fig_hm, use_container_width=True)

        st.divider()
        st.subheader("📋 Últimas lecturas")
        show = lect.head(20).copy()
        st.dataframe(show, use_container_width=True, hide_index=True)
