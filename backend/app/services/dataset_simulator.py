"""
Dataset Simulator Service
Loads real VRI agronomic datasets (Mendeley VRI Dataset) and simulates real-time sensor streams.
"""
import os
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DatasetSimulator:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.current_index = 0
        self.total_rows = 0
        self.is_loaded = False
        self.dataset_name = "None"
        self.lock = threading.Lock()

        # Load dataset during init or on first access
        self.load_datasets()

    def load_datasets(self):
        """Carga los sectores válidos del dataset procesado (1, 2, 4 y 5)."""
        try:
            # Preferir las copias incluidas en el proyecto y luego el directorio
            # de preprocesamiento de Mendeley. No cargar CSV arbitrarios ni el
            # sector 3, excluido por fallas de la sonda.
            candidate_dirs = [
                os.path.join(self.data_dir, "datasets"),
                os.path.join(self.data_dir, "02_processed_data", "preprocessed"),
            ]
            found_files = {}
            for zone_idx in (1, 2, 4, 5):
                filenames = (
                    f"dataset_zone_{zone_idx}_preprocessed.csv",
                    f"dataset_zone_{zone_idx}.csv",
                )
                for directory in candidate_dirs:
                    match = next(
                        (os.path.join(directory, name) for name in filenames
                         if os.path.isfile(os.path.join(directory, name))),
                        None,
                    )
                    if match:
                        found_files[zone_idx] = match
                        break

            if not found_files:
                logger.warning(f"No se encontraron CSV de sectores válidos en {self.data_dir}. Usando modo sintético.")
                self.is_loaded = False
                return

            # Mantener los identificadores reales de sector: el sector 3 no
            # debe desplazar al sector 4 ni al 5 en el mapa del sistema.
            loaded_count = 0
            min_rows = 9999999

            for zone_idx, file_path in found_files.items():
                filename = os.path.basename(file_path)
                zone_key = f"zone_{zone_idx}"
                logger.info(f"Cargando {filename} para {zone_key}...")

                # Cargamos las primeras 5000 filas para velocidad y memoria ligera
                df = pd.read_csv(file_path, nrows=5000)

                # Rellenar nulos con ffill/bfill y valores predeterminados seguros
                df = df.ffill().bfill()

                # Si aún quedan columnas con NaNs
                defaults = {
                    'weather_temp': 22.0,
                    'outside_temperature': 23.0,
                    'inside_temperature': 24.0,
                    'outside_humidity': 60.0,
                    'weather_humidity': 62.0,
                    'weather_radiation': 250.0,
                    'weather_wind_speed': 10.0,
                    'soil_temperature_0-7cm': 21.0,
                    'soil_temperature_7-18cm': 20.5,
                    'soil_moisture': 24.0,
                    'ec': 180.0,
                    'ph': 6.5
                }
                for col, def_val in defaults.items():
                    if col in df.columns:
                        df[col] = df[col].fillna(def_val)
                    else:
                        df[col] = def_val

                # El dataset expresa humedad relativa en porcentaje; conservar
                # mediciones válidas, incluso cuando superan 40%.
                if 'soil_moisture' in df.columns:
                    def sanitize_moisture(val):
                        try:
                            v = float(val)
                            if np.isnan(v):
                                return 24.0
                            if v < 0 or v > 100:
                                return 24.0
                            return round(v, 1)
                        except Exception:
                            return 24.0
                    df['soil_moisture'] = df['soil_moisture'].apply(sanitize_moisture)

                self.datasets[zone_key] = df
                min_rows = min(min_rows, len(df))
                loaded_count += 1

            if self.datasets:
                self.total_rows = min_rows if min_rows != 9999999 else 0
                self.is_loaded = True
                self.dataset_name = ", ".join(os.path.basename(path) for path in found_files.values())
                # Iniciar en una fila donde los datos sean estables (fila 250 por ejemplo)
                if self.total_rows > 300:
                    self.current_index = 250
                logger.info(f"Dataset cargado exitosamente. {loaded_count} zonas, {self.total_rows} registros por zona.")

        except Exception as e:
            logger.error(f"Error cargando dataset VRI: {str(e)}", exc_info=True)
            self.is_loaded = False

    def advance_step(self, steps: int = 1) -> bool:
        """Avanza el índice de simulación."""
        with self.lock:
            if not self.is_loaded or self.total_rows == 0:
                return False
            self.current_index = (self.current_index + steps) % self.total_rows
            return True

    def set_step(self, index: int) -> bool:
        """Fija un índice específico."""
        with self.lock:
            if not self.is_loaded or self.total_rows == 0:
                return False
            self.current_index = max(0, min(index, self.total_rows - 1))
            return True

    def get_simulation_status(self) -> Dict[str, Any]:
        """Retorna información general de la simulación."""
        with self.lock:
            current_ts = "N/A"
            if self.is_loaded and "zone_1" in self.datasets and self.total_rows > 0:
                df1 = self.datasets["zone_1"]
                if "ts" in df1.columns and self.current_index < len(df1):
                    current_ts = str(df1.iloc[self.current_index]["ts"])

            return {
                "is_loaded": self.is_loaded,
                "dataset_name": self.dataset_name,
                "total_zones_loaded": len(self.datasets),
                "total_rows": self.total_rows,
                "current_index": self.current_index,
                "current_timestamp": current_ts,
                "simulated_time": datetime.utcnow().isoformat() + "Z"
            }

    def get_all_sensors_telemetry(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de telemetría de sensores en el formato exacto SensorTelemetry
        esperado por el frontend React y por la consola Streamlit.
        """
        with self.lock:
            if not self.is_loaded or not self.datasets:
                return self._get_fallback_telemetry()

            sensors = []
            idx = self.current_index
            now_iso = datetime.utcnow().isoformat() + "Z"

            # Coordenadas y configuraciones por zona
            zone_configs = [
                {
                    "zoneId": "zone-1-nw",
                    "zoneKey": "zone_1",
                    "soilLat": -14.0645, "soilLng": -75.7335,
                    "irtLat": -14.0640, "irtLng": -75.7340,
                    "flowRate": 4.8
                },
                {
                    "zoneId": "zone-2-ne",
                    "zoneKey": "zone_2",
                    "soilLat": -14.0645, "soilLng": -75.7285,
                    "irtLat": -14.0640, "irtLng": -75.7280,
                    "flowRate": 5.2
                },
                {
                    "zoneId": "zone-3-sw",
                    "zoneKey": "zone_4",
                    "soilLat": -14.0695, "soilLng": -75.7335,
                    "irtLat": -14.0690, "irtLng": -75.7340,
                    "flowRate": 0.0
                },
                {
                    "zoneId": "zone-4-se",
                    "zoneKey": "zone_5",
                    "soilLat": -14.0695, "soilLng": -75.7285,
                    "irtLat": -14.0690, "irtLng": -75.7280,
                    "flowRate": 6.1
                }
            ]

            # Estación Meteorológica Global (usando datos de Zone 1)
            df_base = self.datasets.get("zone_1", list(self.datasets.values())[0])
            row_base = df_base.iloc[idx % len(df_base)]

            amb_temp = float(row_base.get("weather_temp", 22.4))
            amb_hum = float(row_base.get("weather_humidity", 65.0))
            solar_rad = float(row_base.get("weather_radiation", 310.0))
            wind_spd = float(row_base.get("weather_wind_speed", 8.5))

            sensors.append({
                "id": "sn-weather-main",
                "sensorId": "SEN-MET-01",
                "zoneId": "zone-1-nw",
                "timestamp": now_iso,
                "sensorType": "weather_station",
                "location": {"lat": -14.0660, "lng": -75.7310},
                "status": "online",
                "batteryLevel": 98,
                "rssi": -55,
                "readings": {
                    "ambientAirTempC": round(amb_temp, 2),
                    "relativeHumidityPct": round(amb_hum, 1),
                    "solarRadiationWm2": round(solar_rad, 1),
                    "windSpeedMs": round(wind_spd / 3.6, 2)
                },
                "qualityScore": 99
            })

            # Sensores de cada zona
            for i, zc in enumerate(zone_configs):
                df_z = self.datasets.get(zc["zoneKey"], df_base)
                row_z = df_z.iloc[idx % len(df_z)]

                raw_moisture = float(row_z.get("soil_moisture", 22.0))
                soil_t_sup = float(row_z.get("soil_temperature_0-7cm", 21.5))
                soil_t_deep = float(row_z.get("soil_temperature_7-18cm", 20.8))

                m10 = round(raw_moisture, 1)
                m30 = max(12.0, min(48.0, round(m10 * 1.08, 1)))
                m60 = max(14.0, min(50.0, round(m30 * 1.10, 1)))

                # Sensor de Humedad Multiprofundidad
                sensors.append({
                    "id": f"sn-soil-{i+1:02d}",
                    "sensorId": f"SEN-SOIL-Z{i+1}",
                    "zoneId": zc["zoneId"],
                    "timestamp": now_iso,
                    "sensorType": "soil_moisture_multi",
                    "location": {"lat": zc["soilLat"], "lng": zc["soilLng"]},
                    "status": "online",
                    "batteryLevel": 92 - (i * 2),
                    "rssi": -65 - (i * 3),
                    "readings": {
                        "volumetricWaterContent_10cm": m10,
                        "volumetricWaterContent_30cm": m30,
                        "volumetricWaterContent_60cm": m60,
                        "soilTempC": round(soil_t_sup, 1)
                    },
                    "qualityScore": 96
                })

                # Sensor Térmico IRT (Canopia)
                # La temperatura de canopia suele subir si el suelo está más seco
                canopy_t = round(amb_temp + (2.5 if m10 < 18 else -1.2), 1)
                sensors.append({
                    "id": f"sn-irt-{i+1:02d}",
                    "sensorId": f"SEN-IRT-Z{i+1}",
                    "zoneId": zc["zoneId"],
                    "timestamp": now_iso,
                    "sensorType": "canopy_temperature_irt",
                    "location": {"lat": zc["irtLat"], "lng": zc["irtLng"]},
                    "status": "online",
                    "batteryLevel": 88 - (i * 2),
                    "rssi": -68 - (i * 2),
                    "readings": {
                        "canopyTemperatureC": canopy_t,
                        "ambientAirTempC": round(amb_temp, 1)
                    },
                    "qualityScore": 95
                })

                # Sensor de Caudal/Flujo
                sensors.append({
                    "id": f"sn-flow-{i+1:02d}",
                    "sensorId": f"SEN-FLOW-Z{i+1}",
                    "zoneId": zc["zoneId"],
                    "timestamp": now_iso,
                    "sensorType": "flow_meter",
                    "location": {"lat": zc["soilLat"] + 0.0002, "lng": zc["soilLng"] + 0.0002},
                    "status": "online",
                    "batteryLevel": 95,
                    "rssi": -60,
                    "readings": {
                        "flowRateLps": zc["flowRate"]
                    },
                    "qualityScore": 98
                })

            return sensors

    def get_current_sensors(self) -> Dict[str, Dict[str, Any]]:
        """Devuelve diccionario mapeado por id para compatibilidad retroactiva."""
        telemetry = self.get_all_sensors_telemetry()
        return {s["sensorId"]: s for s in telemetry}

    def _get_fallback_telemetry(self) -> List[Dict[str, Any]]:
        """Datos de respaldo en caso de que no haya dataset cargado."""
        now_iso = datetime.utcnow().isoformat() + "Z"
        return [
            {
                "id": "sn-01",
                "sensorId": "SEN-SOIL-NW01",
                "zoneId": "zone-1-nw",
                "timestamp": now_iso,
                "sensorType": "soil_moisture_multi",
                "location": {"lat": -14.0645, "lng": -75.7335},
                "status": "online",
                "batteryLevel": 94,
                "rssi": -68,
                "readings": {
                    "volumetricWaterContent_10cm": 14.8,
                    "volumetricWaterContent_30cm": 16.2,
                    "volumetricWaterContent_60cm": 18.0,
                    "soilTempC": 22.4
                },
                "qualityScore": 98
            },
            {
                "id": "sn-02",
                "sensorId": "SEN-IRT-NW02",
                "zoneId": "zone-1-nw",
                "timestamp": now_iso,
                "sensorType": "canopy_temperature_irt",
                "location": {"lat": -14.0640, "lng": -75.7340},
                "status": "online",
                "batteryLevel": 89,
                "rssi": -72,
                "readings": {
                    "canopyTemperatureC": 29.8,
                    "ambientAirTempC": 26.4
                },
                "qualityScore": 95
            }
        ]

# Instancia global del simulador
data_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
simulator = DatasetSimulator(data_dir=data_directory)
