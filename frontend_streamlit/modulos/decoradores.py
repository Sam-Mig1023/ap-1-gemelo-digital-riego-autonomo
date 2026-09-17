"""Decoradores de permiso — patrón gemelo_educativo_ett/modulo_seguridad/decoradores.py"""
from functools import wraps
import streamlit as st
from .auth import has_permission


def requiere_permiso(permiso: str):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            usuario = st.session_state.get("usuario") or {}
            rol = usuario.get("rol")
            if not rol or not has_permission(rol, permiso):
                st.error("🚫 Permiso insuficiente")
                st.info(f"Se requiere: **{permiso}**")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorador
