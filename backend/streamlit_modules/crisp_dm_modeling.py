"""CRISP-DM modeling screen using the real per-zone prepared datasets."""

from pathlib import Path
from html import escape
from io import BytesIO
import json
import zipfile

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import t as student_t
import sklearn
import joblib


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "datasets"
TARGET = "target_mean_24h"
FORECAST_HORIZON = pd.Timedelta(hours=24)
PROTOCOL_ID = "rolling_origin_24h_embargo_v1"

# Explicit allowlist avoids target leakage from engineered future outcomes such
# as target_point_24h, water_vol_to_24h, and real_moisture_delta.
FEATURE_CANDIDATES = (
    "weather_temp",
    "weather_humidity",
    "weather_rain",
    "weather_pressure",
    "weather_wind_speed",
    "weather_radiation",
    "soil_temperature_0-7cm",
    "soil_temperature_7-18cm",
    "ec",
    "ph",
    "soil_moisture",
    "irrigation_duration_minutes",
    "month",
    "day",
    "hour",
    "day_period",
    "quarter",
    "water_vol_past_4h",
)


@st.cache_data(show_spinner="Cargando datos reales para modelado...")
def _load_zone_datasets(data_dir: str):
    root = Path(data_dir)
    datasets = {}
    errors = {}
    for zone in (1, 2, 3, 4, 5):
        path = root / f"dataset_zone_{zone}_preprocessed.csv"
        if not path.is_file():
            continue
        try:
            frame = pd.read_csv(path)
            if "ts" not in frame.columns:
                errors[zone] = "Falta la columna temporal `ts`."
                continue
            frame["ts"] = pd.to_datetime(frame["ts"], errors="coerce")
            datasets[zone] = frame
        except Exception as exc:
            errors[zone] = f"No se pudo leer el CSV: {exc}"
    return datasets, errors


def _prepare_zone(frame: pd.DataFrame):
    features = [column for column in FEATURE_CANDIDATES if column in frame.columns]
    if TARGET not in frame.columns:
        return None, features, f"Falta la variable objetivo `{TARGET}`."
    if not features:
        return None, features, "No hay variables predictoras permitidas disponibles."

    prepared = frame[["ts", TARGET, *features]].copy()
    prepared[TARGET] = pd.to_numeric(prepared[TARGET], errors="coerce")
    for column in features:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")
    prepared = prepared.dropna(subset=["ts", TARGET, *features])
    prepared = prepared.sort_values("ts", kind="stable").reset_index(drop=True)
    return prepared, features, None


def _expanding_window_splits(timestamps, n_splits=5, horizon=FORECAST_HORIZON):
    """Expanding chronological folds with a real-time embargo between labels."""
    times = pd.Series(pd.to_datetime(timestamps, errors="coerce")).reset_index(drop=True)
    count = len(times)
    validation_size = count // (n_splits + 1)
    if validation_size == 0:
        raise ValueError("Hay muy pocas observaciones para construir los pliegues temporales.")

    first_validation_start = count - n_splits * validation_size
    splits = []
    for fold in range(n_splits):
        validation_start = first_validation_start + fold * validation_size
        validation_end = min(count, validation_start + validation_size)
        cutoff = times.iloc[validation_start] - horizon
        train_indexes = np.flatnonzero((times < cutoff).to_numpy())
        validation_indexes = np.arange(validation_start, validation_end)
        if len(train_indexes) == 0:
            raise ValueError("El horizonte de 24 h deja un pliegue sin datos de entrenamiento.")
        splits.append((train_indexes, validation_indexes))
    return splits


def _chronological_holdout(prepared, train_fraction=0.8, horizon=FORECAST_HORIZON):
    """Reserve the latest block and purge training labels within its horizon."""
    split_at = int(len(prepared) * train_fraction)
    if split_at <= 0 or split_at >= len(prepared):
        raise ValueError("No se pudo formar la prueba cronológica con las filas disponibles.")
    test_start = prepared["ts"].iloc[split_at]
    cutoff = test_start - horizon
    train_mask = prepared["ts"] < cutoff
    embargo_mask = (prepared["ts"] >= cutoff) & (prepared["ts"] < test_start)
    return prepared.loc[train_mask].copy(), prepared.iloc[split_at:].copy(), prepared.loc[embargo_mask].copy()


def _new_models():
    return {
        "Ridge (regresión lineal regularizada)": make_pipeline(
            StandardScaler(), Ridge(alpha=1.0)
        ),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=42,
        ),
    }

def _holm_adjust(p_values):
    """Holm-Bonferroni adjusted p-values in the original comparison order."""
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running_max = 0.0
    for rank, index in enumerate(order):
        running_max = max(running_max, min(1.0, (len(values) - rank) * values[index]))
        adjusted[index] = running_max
    return adjusted


def _moving_block_bootstrap_ci(differences, block_length, repetitions=2000, seed=42):
    """Percentile CI for mean loss difference using moving temporal blocks."""
    values = np.asarray(differences, dtype=float)
    count = len(values)
    block_length = min(max(1, int(block_length)), count)
    block_count = int(np.ceil(count / block_length))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, count - block_length + 1, size=(repetitions, block_count))
    indexes = (starts[:, :, None] + np.arange(block_length)).reshape(repetitions, -1)[:, :count]
    means = values[indexes].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return float(low), float(high)


def _diebold_mariano(differences, horizon_steps):
    """Two-sided DM test with Bartlett HAC variance and HLN finite-sample correction."""
    values = np.asarray(differences, dtype=float)
    count = len(values)
    if count < 30 or horizon_steps >= count / 2:
        return None
    mean_difference = float(values.mean())
    centered = values - mean_difference
    hac_lags = min(max(0, int(horizon_steps) - 1), count - 1)
    long_run_variance = float(np.dot(centered, centered) / count)
    for lag in range(1, hac_lags + 1):
        covariance = float(np.dot(centered[lag:], centered[:-lag]) / count)
        weight = 1.0 - lag / (hac_lags + 1)
        long_run_variance += 2.0 * weight * covariance
    variance_of_mean = max(0.0, long_run_variance) / count
    if variance_of_mean == 0:
        statistic = 0.0 if mean_difference == 0 else float(np.sign(mean_difference) * np.inf)
        p_value = 1.0 if mean_difference == 0 else 0.0
        return statistic, p_value, hac_lags

    correction_squared = (
        count + 1 - 2 * horizon_steps + horizon_steps * (horizon_steps - 1) / count
    ) / count
    if correction_squared <= 0:
        return None
    statistic = mean_difference / np.sqrt(variance_of_mean) * np.sqrt(correction_squared)
    p_value = float(2 * student_t.sf(abs(statistic), df=count - 1))
    return float(statistic), p_value, hac_lags


def _compare_forecast_errors(test_frame, test_y, predictions, candidate):
    timestamps = pd.to_datetime(test_frame["ts"], errors="coerce").dropna().sort_values()
    if len(timestamps) < 2:
        return None, None, "Faltan marcas temporales válidas para estimar autocorrelación."
    median_step = timestamps.diff().dropna().median()
    if pd.isna(median_step) or median_step <= pd.Timedelta(0):
        return None, None, "No se pudo estimar el intervalo temporal del conjunto reservado."
    horizon_steps = int(np.ceil(pd.Timedelta(hours=24) / median_step))

    y_true = np.asarray(test_y, dtype=float)
    candidate_loss = np.abs(y_true - np.asarray(predictions[candidate], dtype=float))
    records = []
    loss_differences = {}
    for name, prediction in predictions.items():
        if name == candidate:
            continue
        other_loss = np.abs(y_true - np.asarray(prediction, dtype=float))
        differences = candidate_loss - other_loss  # Negative favors candidate.
        test_result = _diebold_mariano(differences, horizon_steps)
        if test_result is None:
            return None, None, (
                f"No se reportan p-valores: n={len(y_true)} no basta para un horizonte estimado "
                f"de {horizon_steps} registros con la corrección HAC/HLN."
            )
        statistic, p_value, hac_lags = test_result
        ci_low, ci_high = _moving_block_bootstrap_ci(differences, horizon_steps)
        records.append({
            "Comparación": f"{candidate} vs {name}",
            "Diferencia media MAE (puntos %)": float(differences.mean()),
            "IC 95% inferior": ci_low,
            "IC 95% superior": ci_high,
            "DM (HAC/HLN)": statistic,
            "p sin ajustar": p_value,
            "Pliegues HAC": hac_lags,
            "N": len(differences),
        })
        if name != "Persistencia (humedad actual)":
            loss_differences[name] = differences

    adjusted = _holm_adjust([row["p sin ajustar"] for row in records])
    for row, p_adjusted in zip(records, adjusted):
        row["p ajustado Holm"] = float(p_adjusted)
        if row["Comparación"].endswith("Persistencia (humedad actual)"):
            row["Conclusión"] = "Referencia descriptiva"
        elif p_adjusted < 0.05 and row["IC 95% superior"] < 0:
            row["Conclusión"] = "Candidato con menor MAE; diferencia significativa"
        elif p_adjusted < 0.05 and row["IC 95% inferior"] > 0:
            row["Conclusión"] = "Comparador con menor MAE; diferencia significativa"
        else:
            row["Conclusión"] = "Diferencia no concluyente"

    result = pd.DataFrame(records)
    model_comparisons = result[
        ~result["Comparación"].str.endswith("Persistencia (humedad actual)")
    ]
    superior = bool(
        len(model_comparisons) > 0
        and (model_comparisons["p ajustado Holm"] < 0.05).all()
        and (model_comparisons["IC 95% superior"] < 0).all()
    )
    conclusion = (
        "El candidato muestra menor error que los otros modelos entrenados con evidencia estadística "
        "en el periodo reservado."
        if superior
        else "No hay evidencia suficiente para afirmar que el candidato supere estadísticamente a todos "
        "los otros modelos entrenados en el periodo reservado."
    )
    return result, loss_differences, conclusion


def _html_table(frame: pd.DataFrame, digits=3):
    if frame is None or frame.empty:
        return "<p>No hay resultados disponibles.</p>"
    formatted = frame.copy()
    for column in formatted.select_dtypes(include=["number"]).columns:
        formatted[column] = formatted[column].map(
            lambda value: "" if pd.isna(value) else f"{value:.{digits}f}"
        )
    return formatted.to_html(index=False, border=0, classes="data-table", escape=True)


def _svg_lines(series_map, title, width=900, height=330):
    """Small dependency-free SVG line chart for self-contained HTML reports."""
    if not series_map:
        return "<p>Sin datos suficientes para la figura.</p>"
    colors = ["#1769aa", "#e67e22", "#138a72", "#8e44ad", "#c0392b"]
    numeric = [np.asarray(values, dtype=float) for values in series_map.values()]
    count = min(map(len, numeric))
    if count == 0:
        return "<p>Sin datos suficientes para la figura.</p>"
    numeric = [values[:count] for values in numeric]
    all_values = np.concatenate(numeric)
    low, high = float(np.nanmin(all_values)), float(np.nanmax(all_values))
    if not np.isfinite(low) or not np.isfinite(high):
        return "<p>Sin datos numéricos para la figura.</p>"
    if low == high:
        low, high = low - 1, high + 1
    left, right, top, bottom = 60, width - 20, 35, height - 55
    x_step = (right - left) / max(1, count - 1)
    y_map = lambda value: bottom - (float(value) - low) / (high - low) * (bottom - top)
    pieces = [f'<svg role="img" aria-label="{escape(title)}" viewBox="0 0 {width} {height}" class="chart">']
    pieces.append(f'<text x="{left}" y="20" class="chart-title">{escape(title)}</text>')
    pieces.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#94a3b8"/>')
    pieces.append(f'<text x="8" y="{top+6}" class="axis-label">{high:.2f}</text>')
    pieces.append(f'<text x="8" y="{bottom}" class="axis-label">{low:.2f}</text>')
    for index, (name, values) in enumerate(zip(series_map, numeric)):
        points = " ".join(
            f"{left + i*x_step:.1f},{y_map(value):.1f}"
            for i, value in enumerate(values) if np.isfinite(value)
        )
        color = colors[index % len(colors)]
        pieces.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>')
        legend_y = height - 24 - (index // 3) * 16
        legend_x = left + (index % 3) * ((right - left) / 3)
        pieces.append(f'<line x1="{legend_x:.1f}" y1="{legend_y}" x2="{legend_x+18:.1f}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>')
        pieces.append(f'<text x="{legend_x+23:.1f}" y="{legend_y+4}" class="legend">{escape(str(name)[:32])}</text>')
    pieces.append("</svg>")
    return "".join(pieces)


def _svg_bars(values, title, width=900, height=330, limit=16):
    series = pd.Series(values).dropna().sort_values(ascending=True).tail(limit)
    if series.empty:
        return "<p>Sin datos suficientes para la figura.</p>"
    left, right = 220, width - 25
    row_height = min(24, (height - 55) / len(series))
    max_value = max(float(series.max()), 1e-12)
    pieces = [f'<svg role="img" aria-label="{escape(title)}" viewBox="0 0 {width} {height}" class="chart">']
    pieces.append(f'<text x="10" y="20" class="chart-title">{escape(title)}</text>')
    for index, (label, value) in enumerate(series.items()):
        y = 38 + index * row_height
        bar_width = (right - left) * max(0, float(value)) / max_value
        pieces.append(f'<text x="8" y="{y+row_height*.72:.1f}" class="axis-label">{escape(str(label)[:34])}</text>')
        pieces.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="{max(4,row_height-4):.1f}" fill="#1769aa" rx="3"/>')
        pieces.append(f'<text x="{min(right-35,left+bar_width+5):.1f}" y="{y+row_height*.72:.1f}" class="axis-label">{float(value):.2f}</text>')
    pieces.append("</svg>")
    return "".join(pieces)


def _build_report_html(zone, prepared, features, train, test, result):
    """Assemble a portable HTML report from observed data and calculated results."""
    dataset_inventory = []
    data_quality = []
    moisture_summary = []
    missingness = []
    zones_data, _ = _load_zone_datasets(str(DATA_DIR))
    for zone_id, frame in zones_data.items():
        dataset_inventory.append({
            "Zona": zone_id,
            "Archivo": f"dataset_zone_{zone_id}_preprocessed.csv",
            "Filas": len(frame),
            "Variables": len(frame.columns),
            "Inicio": str(frame["ts"].min()),
            "Fin": str(frame["ts"].max()),
            "Faltantes (%)": float(frame.isna().to_numpy().mean() * 100),
        })
        data_quality.append({
            "Zona": zone_id,
            "Timestamps inválidos": int(frame["ts"].isna().sum()),
            "Timestamps duplicados": int(frame["ts"].duplicated().sum()),
            "Celdas faltantes": int(frame.isna().to_numpy().sum()),
            "Objetivo disponible": TARGET in frame.columns,
        })
        if "soil_moisture" in frame.columns:
            moisture = pd.to_numeric(frame["soil_moisture"], errors="coerce").dropna()
            if not moisture.empty:
                moisture_summary.append({
                    "Zona": zone_id,
                    "n": len(moisture),
                    "Media (%)": moisture.mean(),
                    "Desv. estándar": moisture.std(),
                    "Mediana (%)": moisture.median(),
                    "P05 (%)": moisture.quantile(0.05),
                    "P95 (%)": moisture.quantile(0.95),
                })
        for column in frame.columns:
            missingness.append({
                "Zona": zone_id,
                "Variable": column,
                "Faltantes": int(frame[column].isna().sum()),
                "Faltantes (%)": float(frame[column].isna().mean() * 100),
            })

    setup = pd.DataFrame([
        {"Elemento": "Zona modelada", "Valor": zone},
        {"Elemento": "Dataset", "Valor": f"dataset_zone_{zone}_preprocessed.csv"},
        {"Elemento": "Objetivo", "Valor": TARGET},
        {"Elemento": "Registros utilizables", "Valor": len(prepared)},
        {"Elemento": "Entrenamiento cronológico", "Valor": f"{len(train)} ({train['ts'].min()} a {train['ts'].max()})"},
        {"Elemento": "Prueba temporal reservada", "Valor": f"{len(test)} ({test['ts'].min()} a {test['ts'].max()})"},
        {"Elemento": "Variables predictoras", "Valor": ", ".join(features)},
        {"Elemento": "Faltantes", "Valor": "Filas incompletas excluidas; sin imputación"},
    ])

    tables = [
        ("Tabla 1 · Inventario real", pd.DataFrame(dataset_inventory)),
        ("Tabla 2 · Calidad de datos", pd.DataFrame(data_quality)),
        ("Tabla 3 · Faltantes por variable", pd.DataFrame(missingness)),
        ("Tabla 4 · Descriptivos de humedad", pd.DataFrame(moisture_summary)),
        ("Tabla 5 · Protocolo de modelado", setup),
        ("Tabla 6 · Validación cruzada temporal", result["cv_summary"]),
        ("Tabla 7 · Comparación en prueba reservada", result["metrics"]),
        ("Tabla 8 · Pruebas estadísticas", result["statistical_tests"]),
    ]

    figures = []
    if dataset_inventory:
        figures.append(("Figura 1 · Registros por zona", _svg_bars(
            pd.Series({f"Zona {row['Zona']}": row["Filas"] for row in dataset_inventory}),
            "Registros reales por zona",
        )))
    if missingness:
        missing_by_column = pd.DataFrame(missingness).groupby("Variable")["Faltantes (%)"].mean()
        missing_by_column = missing_by_column[missing_by_column > 0]
        figures.append(("Figura 2 · Porcentaje faltante", _svg_bars(missing_by_column, "Faltantes promedio (%)")))
    if zones_data:
        moisture_series = {}
        for zone_id, frame in zones_data.items():
            if "soil_moisture" in frame.columns:
                values = pd.to_numeric(frame["soil_moisture"], errors="coerce")
                moisture_series[f"Zona {zone_id}"] = values.dropna().to_numpy()[:500]
        if moisture_series:
            aligned = {name: values[:min(map(len, moisture_series.values()))] for name, values in moisture_series.items()}
            figures.append(("Figura 3 · Humedad observada", _svg_lines(aligned, "Humedad observada, primeras 500 lecturas")))
        weekly_series = {}
        for zone_id, frame in zones_data.items():
            if "soil_moisture" in frame.columns:
                temporal = frame[["ts", "soil_moisture"]].copy()
                temporal["soil_moisture"] = pd.to_numeric(temporal["soil_moisture"], errors="coerce")
                temporal = temporal.dropna().set_index("ts").resample("W")["soil_moisture"].mean().dropna()
                weekly_series[f"Zona {zone_id}"] = temporal.to_numpy()
        if weekly_series:
            length = min(map(len, weekly_series.values()))
            figures.append(("Figura 4 · Evolución semanal", _svg_lines(
                {name: values[:length] for name, values in weekly_series.items()},
                "Humedad media semanal por zona",
            )))

    predictions = result["predictions"]
    test_data = result["test"]
    count = min(400, len(test_data))
    prediction_series = {"Observado": test_data[TARGET].tail(count).to_numpy()}
    prediction_series.update({name: values[-count:] for name, values in predictions.items()})
    figures.append(("Figura 5 · Observado y predicciones", _svg_lines(prediction_series, "Humedad observada y pronosticada")))
    rf = result["estimators"].get("Random Forest")
    if rf is not None:
        figures.append(("Figura 6 · Importancia de variables", _svg_bars(
            pd.Series(rf.feature_importances_, index=features), "Importancia de Random Forest", limit=12
        )))
    if result["cv_folds"] is not None and not result["cv_folds"].empty:
        pivot = result["cv_folds"].pivot(index="Pliegue temporal", columns="Modelo", values="MAE (puntos %)")
        figures.append(("Figura 7 · MAE por pliegue", _svg_lines(
            {str(name): pivot[name].to_numpy() for name in pivot.columns},
            "Error MAE por pliegue temporal",
        )))
    if result["loss_differences"]:
        test_timestamps = result["test"]["ts"]
        median_step = test_timestamps.diff().dropna().median()
        window = max(1, int(np.ceil(pd.Timedelta(hours=24) / median_step))) if pd.notna(median_step) and median_step > pd.Timedelta(0) else 24
        figures.append(("Figura 8 · Diferencias móviles de error", _svg_lines(
            {f"vs {name}": pd.Series(values).rolling(window, min_periods=1).mean().to_numpy()[:400]
             for name, values in result["loss_differences"].items()},
            "Diferencia móvil de MAE (negativo favorece al candidato)",
        )))

    table_html = "".join(f"<section><h2>{title}</h2>{_html_table(frame)}</section>" for title, frame in tables)
    figure_html = "".join(f"<section><h2>{title}</h2>{svg}<p class='note'>Interpretar junto con la cobertura, el periodo y las métricas; las figuras describen patrones y no implican causalidad.</p></section>" for title, svg in figures)
    statistical_note = escape(result["statistical_conclusion"])
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reporte CRISP-DM · Zona {zone}</title><style>
body{{font:15px Arial,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#182433;line-height:1.5}}
h1,h2{{color:#155e75}}section{{margin:28px 0;page-break-inside:avoid}}.data-table{{border-collapse:collapse;width:100%;font-size:12px;display:block;overflow-x:auto}}
.data-table th{{background:#e5f2f7;text-align:left}}.data-table th,.data-table td{{border:1px solid #cbd5e1;padding:6px 8px}}
.chart{{width:100%;height:auto;border:1px solid #e2e8f0;background:#fff}}.chart-title{{font:bold 14px Arial;fill:#1f2937}}
.axis-label,.legend{{font:11px Arial;fill:#334155}}.note{{font-size:12px;color:#475569}}.warning{{padding:12px;background:#fff7ed;border-left:4px solid #ea580c}}
@media print{{body{{margin:10mm;max-width:none}}section{{page-break-inside:avoid}}}}
</style></head><body><h1>Reporte CRISP-DM · Predicción de humedad del suelo</h1>
<p><b>Fecha de generación:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} · <b>Zona:</b> {zone} · <b>Objetivo:</b> {TARGET}</p>
<p>Resultados calculados con los archivos CSV locales. No se generan registros artificiales. Filas incompletas se excluyen, no se imputan.</p>
<h2>Resumen ejecutivo</h2><p>{statistical_note}</p>
<p class="warning">El objetivo de error agronómicamente aceptable aún debe acordarse con el equipo. La inferencia estadística aplica solo a la zona y periodo de prueba incluidos; requiere replicación por zona antes de generalizar.</p>
<h2>Tablas</h2>{table_html}<h2>Figuras</h2>{figure_html}
<h2>Metodología y límites</h2><p>Partición cronológica 80/20 con embargo de 24 horas entre entrenamiento y prueba. Cinco pliegues de origen móvil, también separados por un embargo basado en timestamps, dentro del bloque de entrenamiento. Los modelos se comparan por MAE, RMSE y R². La prueba Diebold–Mariano usa varianza HAC/Newey–West, corrección HLN, bootstrap móvil por bloques de 24 horas y ajuste de Holm para comparaciones múltiples.</p>
<p>El reporte no determina causalidad ni valida directamente una política de riego. La variable objetivo es un pronóstico de humedad, no una prescripción agronómica.</p></body></html>"""


def _build_model_package(model, metadata):
    """Build an in-memory, versioned experimental model package for download."""
    model_buffer = BytesIO()
    joblib.dump(model, model_buffer, compress=3)
    metadata_buffer = json.dumps(metadata, ensure_ascii=False, indent=2).encode("utf-8")
    readme = """PAQUETE EXPERIMENTAL DE PREDICCION CRISP-DM

Contenido:
- modelo.joblib: estimador de scikit-learn entrenado con el bloque cronologico anterior al embargo.
- metadata.json: objetivo, zona, version de sklearn, columnas y protocolo.

Consumo con Python, joblib y pandas compatibles:

import json, joblib, pandas as pd
with open('metadata.json', encoding='utf-8') as file:
    metadata = json.load(file)
model = joblib.load('modelo.joblib')
sensor_data = {name: 0.0 for name in metadata['features']}  # Sustituir por mediciones reales
row = pd.DataFrame([sensor_data], columns=metadata['features'])
forecast = float(model.predict(row)[0])

IMPORTANTE: artefacto experimental, no es una política de riego y no debe accionar
válvulas de forma autónoma. Compruebe unidades, zona, variables y version de scikit-learn;
valide rendimiento agronomico antes de integrarlo en el gemelo operativo.
"""
    package = BytesIO()
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("modelo.joblib", model_buffer.getvalue())
        archive.writestr("metadata.json", metadata_buffer)
        archive.writestr("LEEME.txt", readme.encode("utf-8"))
    return package.getvalue()


def _score_models(train_x, train_y, train_timestamps, test_x, test_y, test_frame):
    cv_rows = []
    folds = _expanding_window_splits(train_timestamps, n_splits=5)

    # Cross-validation uses only the historical training period; the final 20%
    # remains untouched for a later one-time evaluation.
    for fold, (fit_indexes, validation_indexes) in enumerate(folds, start=1):
        fold_x = train_x.iloc[fit_indexes]
        fold_y = train_y.iloc[fit_indexes]
        validation_x = train_x.iloc[validation_indexes]
        validation_y = train_y.iloc[validation_indexes]

        for name, model in _new_models().items():
            model.fit(fold_x, fold_y)
            prediction = model.predict(validation_x)
            cv_rows.append({
                "Pliegue temporal": fold,
                "Modelo": name,
                "Filas de ajuste": len(fit_indexes),
                "Filas de validación": len(validation_indexes),
                "MAE (puntos %)": mean_absolute_error(validation_y, prediction),
                "RMSE (puntos %)": np.sqrt(mean_squared_error(validation_y, prediction)),
                "R²": r2_score(validation_y, prediction),
            })

        if "soil_moisture" in validation_x.columns:
            prediction = validation_x["soil_moisture"].to_numpy()
            cv_rows.append({
                "Pliegue temporal": fold,
                "Modelo": "Persistencia (humedad actual)",
                "Filas de ajuste": len(fit_indexes),
                "Filas de validación": len(validation_indexes),
                "MAE (puntos %)": mean_absolute_error(validation_y, prediction),
                "RMSE (puntos %)": np.sqrt(mean_squared_error(validation_y, prediction)),
                "R²": r2_score(validation_y, prediction),
            })

    cv_folds = pd.DataFrame(cv_rows)
    cv_summary = (
        cv_folds.groupby("Modelo", sort=False)
        .agg(**{
            "MAE medio (puntos %)": ("MAE (puntos %)", "mean"),
            "Desv. MAE entre pliegues": ("MAE (puntos %)", "std"),
            "RMSE medio (puntos %)": ("RMSE (puntos %)", "mean"),
            "R² medio": ("R²", "mean"),
        })
        .reset_index()
    )
    model_names = list(_new_models())
    eligible = cv_summary[cv_summary["Modelo"].isin(model_names)]
    provisional_winner = eligible.sort_values(
        ["MAE medio (puntos %)", "RMSE medio (puntos %)"], ascending=True
    ).iloc[0]["Modelo"]

    predictions = {}
    estimators = {}
    rows = []
    # Persistence baseline: assume the current measured soil moisture remains
    # the forecast. It is a benchmark, not one of the three trained algorithms.
    if "soil_moisture" in test_frame.columns:
        predictions["Persistencia (humedad actual)"] = test_frame["soil_moisture"].to_numpy()

    for name, model in _new_models().items():
        model.fit(train_x, train_y)
        prediction = model.predict(test_x)
        estimators[name] = model
        predictions[name] = prediction
        rows.append({
            "Modelo": name,
            "MAE (puntos %)": mean_absolute_error(test_y, prediction),
            "RMSE (puntos %)": np.sqrt(mean_squared_error(test_y, prediction)),
            "R²": r2_score(test_y, prediction),
        })

    if "Persistencia (humedad actual)" in predictions:
        prediction = predictions["Persistencia (humedad actual)"]
        rows.append({
            "Modelo": "Persistencia (humedad actual)",
            "MAE (puntos %)": mean_absolute_error(test_y, prediction),
            "RMSE (puntos %)": np.sqrt(mean_squared_error(test_y, prediction)),
            "R²": r2_score(test_y, prediction),
        })

    statistical_tests, loss_differences, statistical_conclusion = _compare_forecast_errors(
        test_frame, test_y, predictions, provisional_winner
    )
    return (
        pd.DataFrame(rows), predictions, estimators, cv_folds, cv_summary,
        provisional_winner, statistical_tests, loss_differences, statistical_conclusion,
    )


def render_crisp_dm_modeling():
    st.subheader("CRISP-DM · Modelado y entrenamiento")
    st.caption(
        "Entrena tres modelos de regresión con los CSV reales. La evaluación usa una partición "
        "cronológica y validación cruzada de origen móvil; las diferencias se contrastan en el periodo "
        "reservado con pruebas pareadas y ajuste por comparaciones múltiples."
    )
    st.info(
        "Objetivo provisional: `target_mean_24h`, humedad media del suelo prevista a 24 horas. "
        "No se incluyen columnas derivadas del futuro para evitar fuga de información. "
        "Los registros incompletos para las variables seleccionadas se excluyen, sin imputarlos."
    )

    datasets, errors = _load_zone_datasets(str(DATA_DIR))
    if not datasets:
        st.error(f"No se encontraron datasets reales en `{DATA_DIR}`.")
        for zone, message in errors.items():
            st.warning(f"Zona {zone}: {message}")
        return

    zones = sorted(datasets)
    zone = st.selectbox("Zona para entrenar", zones, format_func=lambda value: f"Zona {value}")
    prepared, features, error = _prepare_zone(datasets[zone])
    if error:
        st.error(error)
        return
    if prepared is None or len(prepared) < 30:
        st.error("Se requieren al menos 30 filas completas para una partición temporal exploratoria.")
        return

    try:
        train, test, embargo = _chronological_holdout(prepared)
    except ValueError as exc:
        st.error(str(exc))
        return
    setup = pd.DataFrame([
        {"Elemento": "Archivo", "Valor": f"dataset_zone_{zone}_preprocessed.csv"},
        {"Elemento": "Objetivo", "Valor": TARGET},
        {"Elemento": "Filas completas usadas", "Valor": f"{len(prepared):,}"},
        {"Elemento": "Entrenamiento anterior al embargo", "Valor": f"{len(train):,} · {train['ts'].min()} a {train['ts'].max()}"},
        {"Elemento": "Embargo temporal (excluido)", "Valor": f"{len(embargo):,} filas entre el entrenamiento y la prueba; 24 h"},
        {"Elemento": "Prueba (último 20% temporal)", "Valor": f"{len(test):,} · {test['ts'].min()} a {test['ts'].max()}"},
        {"Elemento": "Variables predictoras", "Valor": ", ".join(features)},
        {"Elemento": "Tratamiento de faltantes", "Valor": "Exclusión de filas incompletas; sin imputación"},
        {"Elemento": "Orden", "Valor": "Cronológico; sin barajar filas"},
    ])
    st.markdown("#### Protocolo reproducible de entrenamiento")
    st.dataframe(setup, use_container_width=True, hide_index=True)
    st.caption(
        "Se excluye un embargo de 24 horas entre entrenamiento y prueba para reducir el solapamiento "
        "de las etiquetas objetivo futuras. Los pliegues internos aplican el mismo embargo por timestamps."
    )

    st.markdown("#### Modelos candidatos")
    st.write(
        "Ridge captura relaciones aproximadamente lineales con regularización; Random Forest modela "
        "interacciones no lineales mediante árboles; HistGradientBoosting aprende patrones no lineales "
        "por etapas. Se añade persistencia como referencia simple, no como modelo entrenado."
    )

    if st.button("Entrenar y validar modelos con esta zona", type="primary"):
        with st.spinner("Entrenando modelos y calculando cinco pliegues temporales..."):
            (
                metrics, predictions, estimators, cv_folds, cv_summary, provisional_winner,
                statistical_tests, loss_differences, statistical_conclusion,
            ) = _score_models(
                train[features], train[TARGET], train["ts"], test[features], test[TARGET], test
            )
        st.session_state["crisp_dm_model_result"] = {
            "protocol": PROTOCOL_ID,
            "zone": zone,
            "features": features,
            "metrics": metrics,
            "predictions": predictions,
            "estimators": estimators,
            "cv_folds": cv_folds,
            "cv_summary": cv_summary,
            "provisional_winner": provisional_winner,
            "statistical_tests": statistical_tests,
            "loss_differences": loss_differences,
            "statistical_conclusion": statistical_conclusion,
            "test": test[["ts", TARGET]].reset_index(drop=True),
        }

    result = st.session_state.get("crisp_dm_model_result")
    if not result or result.get("protocol") != PROTOCOL_ID or result.get("zone") != zone:
        st.info("Pulsa «Entrenar y validar modelos» para calcular resultados con el dataset real de la zona seleccionada.")
        return

    report_html = _build_report_html(zone, prepared, features, train, test, result)
    st.markdown("#### Reporte científico reproducible")
    st.write(
        "El reporte reúne auditoría de los CSV reales, protocolo de partición, validación cruzada, "
        "comparación temporal, pruebas estadísticas y figuras con leyendas interpretables. "
        "Puedes descargarlo como HTML autocontenido y guardarlo como PDF desde la función Imprimir del navegador."
    )
    col_report, col_tables = st.columns(2)
    col_report.download_button(
        "Descargar reporte completo (HTML)",
        data=report_html.encode("utf-8"),
        file_name=f"reporte_crisp_dm_zona_{zone}.html",
        mime="text/html",
        type="primary",
    )
    report_tables = {
        "inventario": pd.DataFrame([
            {"Zona": zone_id, "Archivo": f"dataset_zone_{zone_id}_preprocessed.csv", "Filas": len(frame),
             "Variables": len(frame.columns), "Faltantes (%)": frame.isna().to_numpy().mean() * 100}
            for zone_id, frame in _load_zone_datasets(str(DATA_DIR))[0].items()
        ]),
        "validacion_cruzada": result["cv_summary"],
        "prueba_temporal": result["metrics"],
        "pruebas_estadisticas": result["statistical_tests"] if result["statistical_tests"] is not None else pd.DataFrame(),
    }
    csv_payload = "\n\n".join(
        f"## {name}\n{frame.to_csv(index=False)}" for name, frame in report_tables.items()
    )
    col_tables.download_button(
        "Descargar tablas de resultados (CSV)",
        data=csv_payload.encode("utf-8"),
        file_name=f"tablas_crisp_dm_zona_{zone}.csv",
        mime="text/csv",
    )
    st.markdown("#### CRISP-DM · Despliegue experimental del candidato")
    candidate_name = result["provisional_winner"]
    statistically_supported = result["statistical_conclusion"].startswith(
        "El candidato muestra menor error"
    )
    cv_row = result["cv_summary"].loc[
        result["cv_summary"]["Modelo"] == candidate_name
    ].iloc[0]
    model_metadata = {
        "model_name": candidate_name,
        "status": (
            "experimental_candidate_statistically_supported_for_this_zone"
            if statistically_supported
            else "experimental_candidate_not_statistically_confirmed"
        ),
        "zone": int(zone),
        "dataset_file": f"dataset_zone_{zone}_preprocessed.csv",
        "target": TARGET,
        "features": result["features"],
        "feature_order_must_be_preserved": True,
        "trained_on_rows": int(len(train)),
        "training_start": str(train["ts"].min()),
        "training_end": str(train["ts"].max()),
        "validation_method": "5 expanding chronological folds with a timestamp-based 24-hour embargo",
        "cv_mean_mae": float(cv_row["MAE medio (puntos %)" ]),
        "cv_mae_std": float(cv_row["Desv. MAE entre pliegues"]),
        "statistical_conclusion": result["statistical_conclusion"],
        "scikit_learn_version": sklearn.__version__,
        "target_units": "percentage points of soil moisture",
        "generated_at": pd.Timestamp.now().isoformat(),
    }
    model_package = _build_model_package(result["estimators"][candidate_name], model_metadata)
    st.download_button(
        "Descargar candidato experimental (JOBLIB + metadatos)",
        data=model_package,
        file_name=f"candidato_crisp_dm_zona_{zone}.zip",
        mime="application/zip",
    )
    if statistically_supported:
        st.success(
            f"{candidate_name} muestra menor MAE que los otros modelos entrenados con evidencia estadística "
            f"en la zona {zone} y en el periodo reservado. Sigue siendo un prototipo experimental; "
            "no se habilita el control autónomo del riego."
        )
    else:
        st.warning(
            f"Se exporta {candidate_name}, seleccionado por MAE promedio de validación cruzada. "
            "El análisis no confirmó superioridad sobre todos los modelos; el paquete es para "
            "reproducibilidad y pruebas controladas, no para accionar riego ni operar autónomamente."
        )
    st.caption(
        "El HTML contiene ocho tablas y hasta ocho figuras interpretables. El archivo se genera con los resultados "
        "ya calculados en esta sesión; si cambias zona o datos, vuelve a entrenar y descarga el reporte actualizado."
    )

    metrics = result["metrics"]
    st.markdown("#### Validación cruzada temporal · cinco pliegues de origen móvil")
    st.caption(
        "Cada pliegue ajusta con un bloque histórico y valida con el bloque cronológicamente siguiente, "
        "separados por un embargo de 24 horas calculado a partir de timestamps. La prueba final más reciente permanece reservada."
    )
    st.dataframe(
        result["cv_summary"].style.format({
            "MAE medio (puntos %)": "{:.3f}",
            "Desv. MAE entre pliegues": "{:.3f}",
            "RMSE medio (puntos %)": "{:.3f}",
            "R² medio": "{:.4f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
    cv_mae_by_fold = result["cv_folds"].pivot(
        index="Pliegue temporal", columns="Modelo", values="MAE (puntos %)"
    )
    st.markdown("##### Figura · Estabilidad del MAE entre pliegues temporales")
    st.line_chart(cv_mae_by_fold, use_container_width=True)
    st.caption(
        "Cada punto muestra el MAE de un modelo en un periodo futuro distinto. Una línea más baja "
        "indica menor error; cambios pronunciados entre pliegues sugieren que el rendimiento varía "
        "con el periodo y se deben considerar al interpretar el candidato líder."
    )
    with st.expander("Detalle de métricas por pliegue"):
        st.dataframe(
            result["cv_folds"].style.format({
                "MAE (puntos %)": "{:.3f}",
                "RMSE (puntos %)": "{:.3f}",
                "R²": "{:.4f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    st.caption(
        "La desviación entre pliegues muestra cuánto cambia el MAE entre periodos. Los resultados "
        "dependen de esta zona y las variables incluidas; no demuestran por sí solos que las diferencias "
        "entre algoritmos sean estadísticamente significativas."
    )
    if result["statistical_conclusion"].startswith("El candidato muestra menor error"):
        st.success(
            f"Candidato respaldado para esta zona: {result['provisional_winner']}. "
            "La evidencia está limitada al periodo y los modelos evaluados."
        )
    else:
        st.info(
            f"Candidato por validación cruzada: {result['provisional_winner']}. "
            "Las pruebas aún no confirman superioridad estadística."
        )

    st.markdown("#### Tabla · Comparación exploratoria en el tramo de prueba")
    st.dataframe(
        metrics.style.format({"MAE (puntos %)": "{:.3f}", "RMSE (puntos %)": "{:.3f}", "R²": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "MAE y RMSE se expresan en puntos porcentuales de humedad; valores menores indican menor error. "
        "R² resume variación explicada y puede ser negativo si el modelo rinde peor que predecir la media. "
        "Esta prueba temporal informa el rendimiento en el periodo reservado; la selección provisional se basa "
        "en el MAE medio de validación cruzada. El bloque siguiente contrasta las diferencias de error de forma pareada."
    )

    st.markdown("#### Pruebas estadísticas pareadas en el periodo reservado")
    if result["statistical_tests"] is None:
        st.warning(result["statistical_conclusion"])
    else:
        statistical_tests = result["statistical_tests"]
        st.dataframe(
            statistical_tests.style.format({
                "Diferencia media MAE (puntos %)": "{:.4f}",
                "IC 95% inferior": "{:.4f}",
                "IC 95% superior": "{:.4f}",
                "DM (HAC/HLN)": "{:.3f}",
                "p sin ajustar": "{:.4g}",
                "p ajustado Holm": "{:.4g}",
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "La diferencia es MAE del candidato menos MAE del comparador: valores negativos favorecen al candidato. "
            "Diebold–Mariano contrasta igualdad de pérdida con varianza HAC/Newey–West y corrección HLN; "
            "el intervalo se calcula con bootstrap móvil por bloques de 24 h y los p-valores se ajustan con Holm."
        )
        st.info(
            "La persistencia se incluye como referencia descriptiva. Las conclusiones de superioridad se limitan "
            "a los otros modelos entrenados y al periodo reservado."
        )
        if result["loss_differences"]:
            timestamps = result["test"]["ts"]
            median_step = timestamps.diff().dropna().median()
            if pd.notna(median_step) and median_step > pd.Timedelta(0):
                rolling_window = min(
                    max(1, int(np.ceil(pd.Timedelta(hours=24) / median_step))),
                    len(timestamps),
                )
                loss_chart = pd.DataFrame({
                    f"vs {name}": pd.Series(values).rolling(rolling_window, min_periods=1).mean().to_numpy()
                    for name, values in result["loss_differences"].items()
                }, index=timestamps)
                st.markdown("##### Figura · Diferencia móvil de error absoluto frente a cada modelo")
                st.line_chart(loss_chart, use_container_width=True)
                st.caption(
                    "La línea muestra el promedio móvil de la diferencia entre errores absolutos del candidato y cada modelo. "
                    "Valores bajo cero favorecen al candidato; periodos con valores altos o bajos revelan cambios "
                    "temporales del rendimiento. La figura describe el patrón y no sustituye las pruebas formales."
                )
        st.markdown(f"**Lectura estadística:** {result['statistical_conclusion']}")

    test_data = result["test"]
    predictions = result["predictions"]
    display_count = min(400, len(test_data))
    chart = pd.DataFrame({"Observado": test_data[TARGET].tail(display_count).to_numpy()})
    for name, values in predictions.items():
        chart[name] = values[-display_count:]
    chart.index = test_data["ts"].tail(display_count).to_numpy()
    st.markdown("#### Figura · Humedad observada y predicciones en el tramo más reciente")
    st.line_chart(chart, use_container_width=True)
    st.caption(
        "Cada línea corresponde a observaciones reales del periodo reservado y a predicciones de cada método. "
        "La cercanía visual describe ajuste temporal, pero no sustituye las métricas ni una validación robusta."
    )

    forest = result["estimators"].get("Random Forest")
    if forest is not None:
        importance = pd.Series(
            forest.feature_importances_, index=result["features"], name="Importancia relativa"
        ).sort_values(ascending=False).head(12)
        st.markdown("#### Figura · Variables más influyentes según Random Forest")
        st.bar_chart(importance, use_container_width=True)
        st.caption(
            "La importancia mide cuánto contribuye cada variable a las particiones del bosque en este ajuste. "
            "No demuestra causalidad y puede repartir importancia entre variables correlacionadas."
        )

    st.warning(
        "La inferencia se limita a esta zona, a este periodo reservado y a los modelos comparados. "
        "Debe replicarse por zona antes de generalizar a todo el sistema."
    )
