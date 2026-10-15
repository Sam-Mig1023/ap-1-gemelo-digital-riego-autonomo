"""CRISP-DM data understanding screen backed only by local real datasets."""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "datasets"
EXPECTED_ZONES = (1, 2, 3, 4, 5)
MOISTURE_TARGET = "target_mean_24h"


@st.cache_data(show_spinner="Leyendo los CSV reales disponibles...")
def _load_zone_datasets(data_dir: str):
    """Load only the repository's prepared per-zone datasets; never synthesize rows."""
    root = Path(data_dir)
    datasets = {}
    errors = {}

    for zone in EXPECTED_ZONES:
        path = root / f"dataset_zone_{zone}_preprocessed.csv"
        if not path.is_file():
            continue
        try:
            frame = pd.read_csv(path)
            if "ts" not in frame.columns:
                errors[zone] = "Falta la columna temporal requerida `ts`."
                continue
            frame["ts"] = pd.to_datetime(frame["ts"], errors="coerce")
            datasets[zone] = frame
        except Exception as exc:  # show data-read failures in the UI, not as fake data
            errors[zone] = f"No se pudo leer el CSV: {exc}"

    return datasets, errors


def _build_inventory(datasets):
    records = []
    for zone, frame in datasets.items():
        timestamps = frame["ts"].dropna()
        records.append({
            "Zona": f"Zona {zone}",
            "Archivo": f"dataset_zone_{zone}_preprocessed.csv",
            "Filas": len(frame),
            "Variables": len(frame.columns),
            "Inicio": timestamps.min() if not timestamps.empty else pd.NaT,
            "Fin": timestamps.max() if not timestamps.empty else pd.NaT,
            "Objetivo target_mean_24h": "Disponible" if MOISTURE_TARGET in frame.columns else "Ausente",
            "Faltantes (%)": round(float(frame.isna().to_numpy().mean() * 100), 2) if frame.size else 0.0,
            "Tamaño (MiB)": round(
                (DATA_DIR / f"dataset_zone_{zone}_preprocessed.csv").stat().st_size / (1024 ** 2), 2
            ),
        })
    return pd.DataFrame(records)


def _build_quality_table(datasets):
    records = []
    for zone, frame in datasets.items():
        duplicate_timestamps = int(frame["ts"].duplicated().sum())
        records.append({
            "Zona": f"Zona {zone}",
            "Filas": len(frame),
            "Timestamps no interpretables": int(frame["ts"].isna().sum()),
            "Timestamps duplicados": duplicate_timestamps,
            "Celdas faltantes": int(frame.isna().to_numpy().sum()),
            "Celdas totales": int(frame.size),
            "Objetivo disponible": MOISTURE_TARGET in frame.columns,
            "Humedad disponible": "soil_moisture" in frame.columns,
        })
    return pd.DataFrame(records)


def _build_moisture_summary(datasets):
    records = []
    for zone, frame in datasets.items():
        if "soil_moisture" not in frame.columns:
            continue
        values = pd.to_numeric(frame["soil_moisture"], errors="coerce").dropna()
        if values.empty:
            continue
        records.append({
            "Zona": f"Zona {zone}",
            "n válido": int(values.count()),
            "Media (%)": round(float(values.mean()), 3),
            "Desv. estándar": round(float(values.std()), 3) if len(values) > 1 else None,
            "Mediana (%)": round(float(values.median()), 3),
            "P05 (%)": round(float(values.quantile(0.05)), 3),
            "P95 (%)": round(float(values.quantile(0.95)), 3),
            "Mínimo (%)": round(float(values.min()), 3),
            "Máximo (%)": round(float(values.max()), 3),
        })
    return pd.DataFrame(records)


def _build_missingness_table(datasets):
    records = []
    for zone, frame in datasets.items():
        for column in frame.columns:
            missing_count = int(frame[column].isna().sum())
            records.append({
                "Zona": f"Zona {zone}",
                "Variable": column,
                "Faltantes": missing_count,
                "Filas": len(frame),
                "Faltantes (%)": round(missing_count / len(frame) * 100, 3) if len(frame) else 0.0,
            })
    return pd.DataFrame(records)


def render_crisp_dm_data():
    st.subheader("CRISP-DM · Comprensión del problema y de los datos")
    st.caption(
        "Avance por etapas: el objetivo de predicción está propuesto; esta pantalla desarrolla "
        "la comprensión de los datos con los CSV reales presentes en el proyecto."
    )

    phase_columns = st.columns(6)
    phases = (
        ("1. Negocio", "Objetivo propuesto; falta umbral agronómico"),
        ("2. Datos", "EDA implementado con CSV locales"),
        ("3. Preparación", "Filtrado de filas completas documentado"),
        ("4. Modelado", "Tres algoritmos y validación temporal"),
        ("5. Evaluación", "Métricas y contrastes en pantalla de modelado"),
        ("6. Despliegue", "Reporte y candidato experimental descargables"),
    )
    for column, (title, status) in zip(phase_columns, phases):
        column.markdown(f"**{title}**")
        column.caption(status)

    st.markdown("#### 1. Comprensión del negocio · propuesta para validar")
    st.info(
        "Pregunta de trabajo: ¿qué tan bien se puede anticipar la humedad media del suelo "
        "a 24 horas (`target_mean_24h`) para apoyar la planificación del riego? "
        "El umbral de error agronómicamente aceptable aún no está definido; no se asumirá uno."
    )
    st.markdown("#### 2. Comprensión de los datos · auditoría de archivos disponibles")

    datasets, errors = _load_zone_datasets(str(DATA_DIR))
    if not DATA_DIR.is_dir():
        st.error(f"No existe el directorio esperado de datasets: `{DATA_DIR}`")
        st.stop()
    if not datasets:
        st.error(
            f"No se encontraron CSV preprocesados de zona en `{DATA_DIR}`. "
            "No se mostrarán datos de ejemplo."
        )
        for zone, message in errors.items():
            st.warning(f"Zona {zone}: {message}")
        st.stop()

    if errors:
        for zone, message in errors.items():
            st.warning(f"Zona {zone}: {message}")

    available_zones = sorted(datasets)
    missing_zones = sorted(set(EXPECTED_ZONES) - set(available_zones))
    if missing_zones:
        st.warning(
            "No hay archivo preprocesado local para: "
            + ", ".join(f"zona {zone}" for zone in missing_zones)
            + ". Estas zonas no se completan ni se simulan."
        )

    selected_zones = st.multiselect(
        "Zonas incluidas en la exploración",
        options=available_zones,
        default=available_zones,
        format_func=lambda zone: f"Zona {zone}",
    )
    selected = {zone: datasets[zone] for zone in selected_zones}
    if not selected:
        st.info("Selecciona al menos una zona para explorar sus datos.")
        st.stop()

    inventory = _build_inventory(selected)
    quality = _build_quality_table(selected)
    moisture_summary = _build_moisture_summary(selected)
    missingness = _build_missingness_table(selected)
    combined = pd.concat(
        [frame.assign(zone=f"Zona {zone}") for zone, frame in selected.items()],
        ignore_index=True,
        sort=False,
    )

    total_rows = int(inventory["Filas"].sum())
    total_size = float(inventory["Tamaño (MiB)"].sum())
    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos reales cargados", len(selected))
    col2.metric("Filas leídas", f"{total_rows:,}")
    col3.metric("Tamaño total", f"{total_size:.2f} MiB")

    st.markdown("##### Tabla 1 · Inventario y cobertura de los datasets")
    st.dataframe(inventory, use_container_width=True, hide_index=True)
    st.caption(
        "Cada fila resume el CSV local de una zona. El periodo se obtiene de `ts`; "
        "el porcentaje de faltantes usa las celdas realmente leídas."
    )

    st.markdown("##### Tabla 2 · Controles básicos de calidad")
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.caption(
        "Los duplicados se cuentan por timestamp dentro de cada zona. Esta auditoría "
        "describe los archivos; todavía no elimina ni imputa observaciones."
    )

    with st.expander("Tabla 3 · Faltantes por zona y variable"):
        st.dataframe(missingness, use_container_width=True, hide_index=True)
        st.caption("Cada porcentaje usa como denominador las filas del archivo de esa zona.")

    if not moisture_summary.empty:
        st.markdown("##### Tabla 4 · Estadística descriptiva de humedad observada")
        st.dataframe(moisture_summary, use_container_width=True, hide_index=True)
        st.caption(
            "Media, dispersión, mediana y cuantiles se calculan sobre los valores no faltantes "
            "de `soil_moisture` en cada archivo seleccionado."
        )

    left, right = st.columns(2)
    with left:
        st.markdown("##### Figura 1 · Registros por zona")
        row_chart = inventory.set_index("Zona")[["Filas"]]
        st.bar_chart(row_chart, y="Filas", use_container_width=True)
        st.caption("Compara el volumen observado por archivo; una barra mayor indica más filas disponibles.")

    with right:
        st.markdown("##### Figura 2 · Faltantes por variable")
        missing_counts = {}
        observed_counts = {}
        for frame in selected.values():
            for column in frame.columns:
                missing_counts[column] = missing_counts.get(column, 0) + int(frame[column].isna().sum())
                observed_counts[column] = observed_counts.get(column, 0) + len(frame)
        missing = pd.Series({
            column: missing_counts[column] / observed_counts[column] * 100
            for column in missing_counts
            if observed_counts[column]
        })
        missing = missing[missing > 0].sort_values(ascending=False).head(20)
        if missing.empty:
            st.info("No se observaron celdas faltantes en las variables cargadas.")
        else:
            st.bar_chart(missing.rename("Faltantes (%)"), use_container_width=True)
        st.caption(
            "Porcentaje de celdas ausentes por variable, ponderado por las filas de las zonas seleccionadas. "
            "Solo se muestran las 20 variables con más faltantes."
        )

    if "soil_moisture" in combined.columns:
        st.markdown("##### Figura 3 · Distribución observada de humedad por zona")
        distributions = {}
        for zone, frame in selected.items():
            if "soil_moisture" in frame.columns:
                values = pd.to_numeric(frame["soil_moisture"], errors="coerce").dropna()
                if not values.empty:
                    distributions[f"Zona {zone}"] = values.reset_index(drop=True)
        if distributions:
            all_values = pd.concat(distributions.values(), ignore_index=True)
            low, high = float(all_values.min()), float(all_values.max())
            if low == high:
                low, high = low - 0.5, high + 0.5
            edges = pd.interval_range(start=low, end=high, periods=20)
            histogram = {}
            for zone, values in distributions.items():
                buckets = pd.cut(values, bins=edges, include_lowest=True)
                counts = buckets.value_counts(sort=False)
                histogram[zone] = counts.to_numpy()
            labels = [f"{interval.left:.1f}–{interval.right:.1f}" for interval in edges]
            distribution_frame = pd.DataFrame(histogram, index=labels)
            distribution_frame.index.name = "Humedad observada (%)"
            st.bar_chart(distribution_frame, use_container_width=True)
            st.caption(
                "Cada barra cuenta observaciones reales dentro del mismo intervalo de humedad; "
                "las zonas comparten los intervalos para facilitar la comparación. "
                "No se han añadido ni imputado observaciones."
            )

        st.markdown("##### Figura 4 · Evolución semanal de humedad media")
        temporal_frames = []
        for zone, frame in selected.items():
            if "soil_moisture" not in frame.columns:
                continue
            temporal = frame[["ts", "soil_moisture"]].copy()
            temporal["soil_moisture"] = pd.to_numeric(temporal["soil_moisture"], errors="coerce")
            temporal = temporal.dropna(subset=["ts", "soil_moisture"])
            if not temporal.empty:
                temporal["Zona"] = f"Zona {zone}"
                temporal_frames.append(temporal)
        if temporal_frames:
            temporal_data = pd.concat(temporal_frames, ignore_index=True)
            weekly = (
                temporal_data.groupby([pd.Grouper(key="ts", freq="W"), "Zona"])["soil_moisture"]
                .mean()
                .unstack("Zona")
                .sort_index()
            )
            if not weekly.empty:
                st.line_chart(weekly, use_container_width=True)
                st.caption(
                    "Cada punto es la media semanal de las lecturas observadas en esa zona. "
                    "Los huecos indican semanas sin lecturas válidas; no se interpolan en esta etapa."
                )

    with st.expander("Vista de filas reales (sin modificar)"):
        zone_to_preview = st.selectbox(
            "Zona para inspección",
            options=selected_zones,
            index=0,
            format_func=lambda zone: f"Zona {zone}",
            key="crisp_dm_preview_zone",
        )
        st.dataframe(selected[zone_to_preview].head(25), use_container_width=True)
        st.caption("Muestra de las primeras 25 filas del CSV local seleccionado; no son registros generados.")

    st.markdown("#### Lectura y límites de esta etapa")
    st.write(
        "Esta pantalla documenta cobertura, faltantes y distribución de las observaciones disponibles. "
        "Esta vista describe los datos sin imputarlos. La pantalla «CRISP-DM - Modelado» permite entrenar "
        "tres algoritmos, ejecutar validación temporal y contrastar errores. Los reportes se habilitan "
        "después de entrenar; no se calculan métricas hasta que el usuario ejecuta ese flujo."
    )
