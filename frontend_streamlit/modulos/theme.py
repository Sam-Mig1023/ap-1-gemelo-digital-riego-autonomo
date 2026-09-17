"""
Utilidades de tema para gráficos Plotly.
Detecta si Streamlit está en modo oscuro y devuelve el template correcto.
"""
import streamlit as st


def _is_dark() -> bool:
    """Devuelve True si el tema activo es oscuro."""
    try:
        theme = st.get_option("theme.backgroundColor") or "#ffffff"
        # Manejar el caso en que theme podría ser None
        if not theme:
            return False
        # Extraer valores RGB del color hexadecimal
        hex_color = theme.lstrip("#")
        if len(hex_color) >= 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.5
        return False
    except Exception:
        return False


def plotly_template() -> str:
    """Devuelve el template de Plotly según el tema."""
    return "plotly_dark" if _is_dark() else "plotly_white"


def plotly_layout(height: int = 320, margin: dict | None = None) -> dict:
    """
    Devuelve kwargs de update_layout adaptados al tema activo.
    Uso: fig.update_layout(**theme.plotly_layout())
    """
    template = plotly_template()
    
    # Configuraciones base que funcionan con ambos templates
    base_layout = {
        "template": template,
        "height": height,
        "margin": margin or {"t": 40, "b": 20, "l": 10, "r": 10},
        "font": {"size": 12},
        "hovermode": "x unified",
    }
    
    # Ajustes específicos para modo oscuro
    if _is_dark():
        base_layout.update({
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
        })
    
    return base_layout


def plotly_colors() -> list[str]:
    """Paleta de líneas/barras coherente en ambos temas."""
    return ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#0891b2", "#9333ea", "#db2777"]


def status_colors() -> dict:
    """Colores semánticos que funcionan en ambos temas."""
    return {
        "success": "#16a34a",
        "warning": "#d97706",
        "error": "#dc2626",
        "info": "#2563eb",
        "neutral": "#64748b",
        "primary": "#2563eb",
        "secondary": "#7c3aed",
    }


def get_text_color() -> str:
    """Devuelve el color de texto apropiado para el tema actual."""
    return "#e2e8f0" if _is_dark() else "#0f172a"


def get_background_color() -> str:
    """Devuelve el color de fondo apropiado para el tema actual."""
    return "#0f172a" if _is_dark() else "#ffffff"


def get_secondary_background() -> str:
    """Devuelve el color de fondo secundario para el tema actual."""
    return "#1e293b" if _is_dark() else "#f8fafc"