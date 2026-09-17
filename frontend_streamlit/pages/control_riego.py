"""Control de Riego — Ejecución con persistencia en SQLite y bitácora"""
import streamlit as st
import pandas as pd
import api_client as api
import database as db
from modulos.auth import has_permission


def render():
    st.title("Control de Riego VRI")
    usuario = st.session_state.usuario
    rol     = usuario["rol"]

    # ── Estado del sistema ────────────────────────────────────────────────────
    st.subheader("Estado del Sistema (API)")
    status = api.get_irrigation_status()
    zonas_df = db.get_zonas()
    zonas_opts = [{"id": r["id"], "nombre": r["nombre"]} for _, r in zonas_df.iterrows()]
    if not zonas_opts:
        zonas_opts = [{"id": "zone-nw", "nombre": "Zona 1 — Noroeste"}]
    if status:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sistema", "Operativo" if status.get("systemOperational") else "Falla")
        c2.metric("Hardware", "Conectado" if status.get("hardwareConnected") else "Desconectado")
        c3.metric("Presión", f"{status.get('waterPressureBar','—')} bar")
        c4.metric("Flujo", f"{status.get('flowRateLpm', 0)} L/min")

        zonas_st = status.get("zoneStatuses", [])
        if zonas_st:
            df = pd.DataFrame(zonas_st)
            df.columns = ["Zona", "Estado", "Última Ejecución", "Próximo Riego"]
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("API offline — mostrando estado de zonas desde SQLite")
        if not zonas_df.empty:
            st.dataframe(
                zonas_df[["id", "sector", "humedad10", "cwsi", "dosis_mm"]],
                use_container_width=True, hide_index=True,
            )

    # ── Parada de emergencia ──────────────────────────────────────────────────
    st.divider()
    col_stop, _ = st.columns([1, 3])
    with col_stop:
        st.markdown("### Parada de Emergencia")
        puede_parar = has_permission(rol, "parada_emergencia")
        confirmar = st.checkbox("Confirmo parada de emergencia", disabled=not puede_parar)
        if st.button("DETENER TODO EL RIEGO", type="primary",
                     disabled=not (puede_parar and confirmar), use_container_width=True):
            res = api.emergency_stop("field-001")
            db.log_bitacora(usuario["user_id"], "PARADA_EMERGENCIA",
                            "Todas las válvulas cerradas")
            msg = res.get("message", "Sistema detenido") if res else "Detenido localmente (API offline)"
            st.error(f"{msg}")
        if not puede_parar:
            st.caption(f"El rol {rol} no puede activar la parada de emergencia.")

    st.divider()

    # ── Ejecutar decisión RL aprobada ─────────────────────────────────────────
    st.subheader("Ejecutar Decisión RL Aprobada")
    dec = st.session_state.get("ultima_decision")
    puede_exec = has_permission(rol, "ejecutar_riego")

    if dec:
        c1, c2, c3 = st.columns(3)
        c1.metric("Decisión", str(dec.get("id","—"))[:16])
        c2.metric("Dosis", f"{dec.get('recommendedDepthMm',0)} mm")
        c3.metric("Zona", dec.get("zoneId","—"))

        if st.button("Ejecutar Decisión RL", disabled=not puede_exec,
                     use_container_width=True):
            res = api.execute_irrigation(
                dec["id"], dec.get("zoneId"), dec.get("recommendedDepthMm")
            )
            # Guardar ejecución en SQLite siempre
            db.save_ejecucion(
                zona_id=dec.get("zoneId","—"),
                dosis_mm=float(dec.get("recommendedDepthMm", 0)),
                tipo="automatico",
                ejecutado_por=usuario["username"],
            )
            db.log_bitacora(usuario["user_id"], "EJECUTAR_RIEGO",
                            f"Zona {dec.get('zoneId')} — {dec.get('recommendedDepthMm')} mm (RL)")
            if res:
                st.success(
                    f"Riego ejecutado — {res.get('irrigationDepthMm')} mm · "
                    f"{res.get('volumeDispatchedM3')} m³"
                )
            else:
                st.success("Ejecución registrada en BD local (API offline)")

        if not puede_exec:
            st.caption(f"El rol {rol} no puede ejecutar riegos.")
    else:
        pendientes = db.get_decisiones()
        if not pendientes.empty and "pendiente" in set(pendientes["estado"].tolist()):
            st.info("Hay decisiones pendientes en SQLite. Ejecuta una inferencia en Agente RL para cargar una en sesión, o usa el disparo manual.")
        else:
            st.info("Ve al módulo Agente RL, ejecuta una inferencia y aprueba la decisión primero.")

    st.divider()

    # ── Disparo manual ────────────────────────────────────────────────────────
    st.subheader("Disparo Manual de Riego")
    puede_manual = has_permission(rol, "riego_manual")

    c1, c2, c3 = st.columns(3)
    zona_m = c1.selectbox("Zona", [z["nombre"] for z in zonas_opts], key="man_zona")
    zona_id = next(z["id"] for z in zonas_opts if z["nombre"] == zona_m)
    dosis_m = c2.number_input("Dosis (mm)", 0.5, 20.0, 5.0, step=0.5, key="man_dosis")
    operador = c3.text_input("Operador", value=usuario["username"], key="man_op")

    if st.button("Disparar Riego Manual", disabled=not puede_manual,
                 use_container_width=True):
        res = api.manual_trigger(zona_id, dosis_m, operador)
        db.save_ejecucion(zona_id, dosis_m, "manual", operador)
        db.log_bitacora(usuario["user_id"], "RIEGO_MANUAL",
                        f"Zona {zona_id} — {dosis_m} mm por {operador}")
        if res:
            st.success(f"Riego manual — {zona_m} · {dosis_m} mm · Por: {operador}")
        else:
            st.success("Registrado localmente (API offline)")

    if not puede_manual:
        st.caption(f"El rol {rol} no tiene permiso para riego manual.")

    st.divider()

    # ── Historial de ejecuciones desde SQLite ─────────────────────────────────
    st.subheader("Historial de Ejecuciones (BD Local)")
    ej_df = db.get_ejecuciones(limit=30)
    if not ej_df.empty:
        ej_df.columns = ["ID", "Zona", "Dosis (mm)", "Volumen (m³)",
                         "Tipo", "Ejecutado por", "Fecha"]
        st.dataframe(ej_df, use_container_width=True, hide_index=True)
    else:
        st.info("Sin ejecuciones registradas aún.")

    # ── Programación (API) ────────────────────────────────────────────────────
    st.divider()
    st.subheader("Programación de Riegos (API)")
    sch = api.get_irrigation_schedule()
    if sch and sch.get("schedule"):
        df_sch = pd.DataFrame(sch["schedule"])
        df_sch.columns = ["Zona", "Hora Programada", "Dosis Estimada (mm)", "Estado"]
        st.dataframe(df_sch, use_container_width=True, hide_index=True)
        st.caption(f"Próxima ejecución: {sch.get('nextExecution','—')}")
    else:
        st.info("Sin programación disponible o API offline.")