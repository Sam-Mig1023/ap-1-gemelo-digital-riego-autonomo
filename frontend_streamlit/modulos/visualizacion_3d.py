"""
Visualización 3D georreferenciada del Gemelo Digital de Riego.
Patrón: gemelo_educativo_ett/modulo_visualizacion_3d/gemelo_3d.py (pydeck ColumnLayer).
Datos: zonas SQLite del campo VRI (Ica, Perú).
"""
import pandas as pd
import streamlit as st
import pydeck as pdk
import database as db

# Bbox del campo (mismo polígono que src/data/mockData.ts del frontend React)
CAMPO_LNG_W, CAMPO_LNG_E = -75.7365, -75.7255
CAMPO_LAT_N, CAMPO_LAT_S = -14.0615, -14.0725
CAMPO_LNG_MID = (CAMPO_LNG_W + CAMPO_LNG_E) / 2
CAMPO_LAT_MID = (CAMPO_LAT_N + CAMPO_LAT_S) / 2

# Polígonos [lng, lat] de cada cuadrante (anillo cerrado)
POLIGONOS_ZONA = {
    "NW": [
        [CAMPO_LNG_W, CAMPO_LAT_N],
        [CAMPO_LNG_MID, CAMPO_LAT_N],
        [CAMPO_LNG_MID, CAMPO_LAT_MID],
        [CAMPO_LNG_W, CAMPO_LAT_MID],
        [CAMPO_LNG_W, CAMPO_LAT_N],
    ],
    "NE": [
        [CAMPO_LNG_MID, CAMPO_LAT_N],
        [CAMPO_LNG_E, CAMPO_LAT_N],
        [CAMPO_LNG_E, CAMPO_LAT_MID],
        [CAMPO_LNG_MID, CAMPO_LAT_MID],
        [CAMPO_LNG_MID, CAMPO_LAT_N],
    ],
    "SW": [
        [CAMPO_LNG_W, CAMPO_LAT_MID],
        [CAMPO_LNG_MID, CAMPO_LAT_MID],
        [CAMPO_LNG_MID, CAMPO_LAT_S],
        [CAMPO_LNG_W, CAMPO_LAT_S],
        [CAMPO_LNG_W, CAMPO_LAT_MID],
    ],
    "SE": [
        [CAMPO_LNG_MID, CAMPO_LAT_MID],
        [CAMPO_LNG_E, CAMPO_LAT_MID],
        [CAMPO_LNG_E, CAMPO_LAT_S],
        [CAMPO_LNG_MID, CAMPO_LAT_S],
        [CAMPO_LNG_MID, CAMPO_LAT_MID],
    ],
}


def _color_cwsi(cwsi: float) -> list[int]:
    if cwsi >= 0.6:
        return [220, 38, 38, 200]
    if cwsi >= 0.3:
        return [245, 158, 11, 200]
    return [22, 163, 74, 200]


def _nivel(cwsi: float) -> str:
    if cwsi >= 0.6:
        return "CRÍTICO"
    if cwsi >= 0.3:
        return "VIGILANCIA"
    return "NORMAL"


def _preparar_dataframe(zonas: list[dict], metrica: str) -> pd.DataFrame:
    filas = []
    for z in zonas:
        sector = z.get("sector")
        cwsi = float(z.get("cwsi") or 0)
        hum = float(z.get("humedad10") or 0)
        dosis = float(z.get("dosis_mm") or 0)
        if metrica == "CWSI":
            valor, altura = cwsi, max(cwsi, 0.05) * 900
        elif metrica == "Humedad 10 cm":
            valor, altura = hum, max(hum, 1) * 18
        else:
            valor, altura = dosis, max(dosis, 0.3) * 80

        filas.append({
            "id": z.get("id"),
            "nombre": z.get("nombre"),
            "sector": sector,
            "latitud": float(z.get("latitud") or CAMPO_LAT_MID),
            "longitud": float(z.get("longitud") or CAMPO_LNG_MID),
            "poligono": POLIGONOS_ZONA.get(sector, POLIGONOS_ZONA["NW"]),
            "humedad10": hum,
            "temp_canopia": float(z.get("temp_canopia") or 0),
            "cwsi": cwsi,
            "dosis_mm": dosis,
            "area_ha": float(z.get("area_ha") or 0),
            "tipo_suelo": z.get("tipo_suelo") or "—",
            "valor": round(valor, 2),
            "altura": altura,
            "color": _color_cwsi(cwsi),
            "nivel_riesgo": _nivel(cwsi),
        })
    return pd.DataFrame(filas)


def mostrar_gemelo_3d(zonas: list[dict] | None = None):
    """Renderiza el gemelo 3D georreferenciado (patrón educativo: ColumnLayer + pitch)."""
    if zonas is None:
        df_z = db.get_zonas()
        zonas = [] if df_z.empty else df_z.to_dict("records")

    if not zonas:
        st.warning("No hay zonas en SQLite para el gemelo 3D.")
        return

    st.markdown("### 📍 Visualización georreferenciada 3D — Campo San Pablo (Ica)")

    criticos = sum(1 for z in zonas if float(z.get("cwsi") or 0) >= 0.6)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌾 Zonas", len(zonas))
    c2.metric("📐 Área", f"{sum(float(z.get('area_ha') or 0) for z in zonas):.1f} ha")
    c3.metric("🌡️ CWSI medio", f"{sum(float(z.get('cwsi') or 0) for z in zonas) / len(zonas):.2f}")
    c4.metric("🚨 Zonas en crítico", criticos)

    st.info("""
    📖 **Leyenda del Gemelo 3D** (mismo criterio que el educativo del profe):
    - 📏 **Altura de columna** = magnitud de la métrica elegida (CWSI, humedad o dosis RL)
    - 🔴 **Rojo** = CWSI ≥ 0.60 → estrés crítico
    - 🟡 **Ámbar** = CWSI 0.30–0.59 → vigilancia
    - 🟢 **Verde** = CWSI < 0.30 → normal
    - Arrastra el mapa: inclinación (`pitch`) y rotación (`bearing`) como en el gemelo educativo.
    """)

    metrica = st.radio(
        "Métrica de elevación 3D",
        ["CWSI", "Humedad 10 cm", "Dosis RL (mm)"],
        horizontal=True,
        key="gemelo3d_metrica",
    )
    c_pitch, c_bear = st.columns(2)
    pitch = c_pitch.slider("Inclinación (pitch)", 0, 70, 45, key="gemelo3d_pitch")
    bearing = c_bear.slider("Rotación (bearing)", -180, 180, 20, key="gemelo3d_bearing")

    df = _preparar_dataframe(zonas, metrica)

    records = df.to_dict("records")

    capa_suelo = pdk.Layer(
        "PolygonLayer",
        data=records,
        get_polygon="poligono",
        get_fill_color="color",
        get_line_color=[15, 23, 42],
        line_width_min_pixels=2,
        opacity=0.35,
        pickable=True,
        auto_highlight=True,
    )
    capa_columnas = pdk.Layer(
        "ColumnLayer",
        data=records,
        get_position=["longitud", "latitud"],
        get_elevation="altura",
        elevation_scale=1,
        radius=120,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )
    capa_pivote = pdk.Layer(
        "ScatterplotLayer",
        data=[{"latitud": CAMPO_LAT_MID, "longitud": CAMPO_LNG_MID, "nombre": "Pivote central VRI"}],
        get_position=["longitud", "latitud"],
        get_fill_color=[100, 116, 139, 230],
        get_radius=55,
        pickable=True,
    )

    vista = pdk.ViewState(
        latitude=float(df["latitud"].mean()),
        longitude=float(df["longitud"].mean()),
        zoom=13.6,
        pitch=pitch,
        bearing=bearing,
    )
    tooltip = {
        "html": """
        <div style="font-family: Arial; padding: 10px; min-width: 200px;">
            <b>{nombre}</b><br/>
            <small>Sector {sector} · {area_ha} ha · {tipo_suelo}</small>
            <hr style="margin: 5px 0;"/>
            🌡️ CWSI: <b>{cwsi}</b> ({nivel_riesgo})<br/>
            💧 Humedad 10 cm: <b>{humedad10} %</b><br/>
            💦 Dosis RL: <b>{dosis_mm} mm</b><br/>
            📏 Elevación ({valor})
        </div>
        """,
        "style": {"backgroundColor": "white", "color": "#1e293b", "borderRadius": "8px"},
    }
    mapa = pdk.Deck(
        layers=[capa_suelo, capa_columnas, capa_pivote],
        initial_view_state=vista,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )
    st.pydeck_chart(mapa, use_container_width=True)

    st.markdown("### 📋 Resumen georreferenciado por zona")
    mostrar = df[[
        "sector", "nombre", "latitud", "longitud", "cwsi",
        "humedad10", "dosis_mm", "nivel_riesgo",
    ]].copy()
    mostrar.columns = [
        "Sector", "Nombre", "Latitud", "Longitud", "CWSI",
        "Humedad 10 cm (%)", "Dosis RL (mm)", "Nivel",
    ]

    def colorear_nivel(fila):
        if fila["Nivel"] == "CRÍTICO":
            return ["background-color: #fee2e2"] * len(fila)
        if fila["Nivel"] == "VIGILANCIA":
            return ["background-color: #fef3c7"] * len(fila)
        return ["background-color: #dcfce7"] * len(fila)

    st.dataframe(
        mostrar.style.apply(colorear_nivel, axis=1),
        use_container_width=True,
        hide_index=True,
    )
