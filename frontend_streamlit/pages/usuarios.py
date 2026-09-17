"""Gestión de usuarios — alta, rol, baja y reset de contraseña."""
import streamlit as st
import pandas as pd
import database as db
from modulos.auth import PERMISOS
from modulos.decoradores import requiere_permiso


@requiere_permiso("gestionar_usuarios")
def render():
    st.title("👥 Gestión de Usuarios")
    usuario = st.session_state.usuario

    st.subheader("📋 Usuarios del Sistema")
    df = db.get_all_users()
    show = df.copy()
    show["activo"] = show["activo"].apply(lambda x: "✅ Activo" if x == 1 else "❌ Inactivo")
    st.dataframe(show, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🔑 Permisos por Rol")
    filas = []
    for rol, perms in PERMISOS.items():
        fila = {"Rol": rol}
        fila.update({k: "✅" if v else "❌" for k, v in perms.items()})
        filas.append(fila)
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("➕ Crear Usuario")
    with st.form("nuevo_usuario"):
        c1, c2 = st.columns(2)
        uname = c1.text_input("Usuario")
        nombre = c1.text_input("Nombre")
        apell = c2.text_input("Apellido")
        email = c2.text_input("Email")
        rol = c1.selectbox("Rol", ["Administrador", "Agronomo", "Productor", "Tecnico"])
        pwd = c2.text_input("Contraseña temporal", type="password")
        enviar = st.form_submit_button("➕ Crear Usuario", use_container_width=True)
        if enviar:
            if not all([uname, nombre, apell, email, pwd]):
                st.error("Completa todos los campos.")
            else:
                ok, msg = db.registrar_usuario(uname, pwd, nombre, apell, email, rol)
                if ok:
                    db.log_bitacora(usuario["user_id"], "CREAR_USUARIO",
                                    f"Usuario '{uname}' creado con rol {rol}")
                    st.success(f"✅ {msg}: **{uname}**")
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()
    st.subheader("🛠️ Editar usuario existente")
    if df.empty:
        return
    uid = st.selectbox(
        "Usuario",
        df["id"].tolist(),
        format_func=lambda i: f"{df[df['id']==i]['username'].iloc[0]} ({df[df['id']==i]['rol'].iloc[0]})",
    )
    row = df[df["id"] == uid].iloc[0]
    c1, c2, c3 = st.columns(3)
    nuevo_rol = c1.selectbox(
        "Rol", ["Administrador", "Agronomo", "Productor", "Tecnico"],
        index=["Administrador", "Agronomo", "Productor", "Tecnico"].index(row["rol"]),
    )
    nuevo_pwd = c2.text_input("Nueva contraseña (vacío = no cambiar)", type="password")
    activo = c3.checkbox("Activo", value=bool(row["activo"]))

    if st.button("💾 Guardar cambios", use_container_width=True):
        if uid == usuario["user_id"] and not activo:
            st.error("No puedes desactivar tu propio usuario.")
        else:
            db.cambiar_rol(uid, nuevo_rol)
            db.set_user_activo(uid, 1 if activo else 0)
            if nuevo_pwd:
                db.cambiar_password(uid, nuevo_pwd)
            db.log_bitacora(
                usuario["user_id"], "EDITAR_USUARIO",
                f"id={uid} rol={nuevo_rol} activo={activo}",
            )
            st.success("Cambios guardados.")
            st.rerun()
