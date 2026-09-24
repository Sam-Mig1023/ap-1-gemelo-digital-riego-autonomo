# Real-World Irrigation Dataset / Dataset Real de Riego

## English

### Overview
This document describes the public dataset integrated into the VRI Digital Twin system for enhanced RAG (Retrieval-Augmented Generation) responses and model training.

**Dataset:** Soil Moisture, Irrigation Actuator and Weather Dataset from a Multi-Sector Precision-Irrigation Field Trial  
**Location:** Arnesano, Apulia, Italy  
**Period:** February–September 2025 (full growing season)  
**License:** CC BY 4.0  
**Citation:** Dataset available at Mendeley Data (2026)

### Key Features
- **Real actuator telemetry**: Applied water volume is measured, not assumed
- **Multi-crop configuration**: 4 different crop/substrate setups sharing same weather
- **Validated irrigation events**: 789 events reconstructed from noisy valve signals
- **ML-ready format**: Features and 24-hour targets pre-aligned
- **Weather integration**: ERA5 reanalysis data from Open-Meteo

### Sectors Included in This System

| Sector | Crop Type | Substrate | Rows | Date Range | File |
|--------|-----------|-----------|------|------------|------|
| 1 | Tomato | Open field | 9,531 | 2025-02-28 to 2025-09-04 | dataset_zone_1_preprocessed.csv |
| 2 | Tomato | Open field | 11,929 | 2025-02-28 to 2025-09-23 | dataset_zone_2_preprocessed.csv |
| 4 | Zucchini | Open field | 12,676 | 2025-03-01 to 2025-09-23 | dataset_zone_4_preprocessed.csv |
| 5 | Blueberry | Open field | 11,814 | 2025-02-11 to 2025-09-22 | dataset_zone_5_preprocessed.csv |

*Note: Sector 3 (tomato in pots, 1,118 rows) was excluded due to probe failure in June.*

### Data Structure

Each CSV file contains 10-minute resolution time series with:

**Sensor Variables:**
- `humidity_percentage`: Soil moisture (0-100%, relative volumetric water content)
- `soil_ph`: Soil pH (3-9 typical range)
- `soil_ce`: Electrical conductivity (µS/cm)
- `humidity_status`: Agronomic class (0=danger, 1=stress, 2=optimal, 3=excess, 4=saturation)

**Weather Variables (ERA5 reanalysis):**
- `weather_temp`: Air temperature (°C)
- `weather_humidity`: Relative humidity (%)
- `weather_rain`: Precipitation (mm)
- `weather_pressure`: Atmospheric pressure (hPa)
- `weather_wind_speed`: Wind speed (km/h)
- `weather_radiation`: Solar radiation (W/m²)

**Irrigation Variables:**
- `irrigation_duration_minutes`: Minutes of irrigation in 10-min window (0-10)
- `water_vol_to_24h`: Litres applied over next 24 hours (forward-looking)
- `water_vol_past_4h`: Litres applied in past 4 hours

**Targets (24-hour horizon):**
- `target_point_24h`: Soil moisture 24 hours ahead
- `target_mean_24h`: Mean soil moisture over next 24 hours
- `real_moisture_delta`: Realized moisture change (do not use as feature - forward-looking)

**Temporal Features:**
- `month`, `day`, `hour`, `day_period`, `quarter`

### Key Statistics

**Irrigation Events (reconstructed from valve telemetry):**
- Total validated events: 789
- Standard irrigations: 432
- Fertigations: 357
- Date range: 2025-02-17 to 2025-08-31
- Median duration: ~45 minutes
- Maximum duration: 9.53 hours (long fertigations)

**Soil Moisture Thresholds by Crop:**

| Crop | PWP | MADP | FC | SP | Start Irrig | Stop Irrig |
|------|-----|------|----|----|-------------|------------|
| Tomato (open) | 20% | 40% | 60% | 80% | <40% | >60% |
| Tomato (pot) | 30% | 60% | 80% | 90% | <60% | >80% |
| Zucchini | 40% | 80% | 90% | 95% | <80% | >90% |
| Blueberry | 35% | 70% | 90% | 95% | <50% | >60% |

*PWP = Permanent Wilting Point, MADP = Management Allowed Depletion Point, FC = Field Capacity, SP = Saturation Point*

### Use Cases for RAG System

When users ask about:
1. **Real-world irrigation patterns**: Reference the 789 validated events
2. **Soil moisture dynamics**: Cite actual moisture ranges and temporal behavior
3. **Weather-irrigation relationships**: Explain correlations observed in the dataset
4. **Crop water requirements**: Compare theoretical FAO-56 Kc with measured consumption
5. **Sensor reliability**: Discuss dropout handling and quality filtering applied
6. **ML model training**: Describe features, targets, and preprocessing pipeline

### Example Queries the RAG Can Answer

- "What was the average soil moisture in tomato fields during the 2025 trial?"
- "How many irrigation events occurred in the zucchini sector?"
- "What is the relationship between precipitation and irrigation frequency?"
- "Show me typical irrigation duration for blueberries."
- "What soil moisture threshold triggers irrigation in open-field tomatoes?"

### Data Quality Notes

- **Raw layer published**: Includes sensor dropouts, flatlines, and spikes for transparency
- **Preprocessing applied**: Time-based interpolation (2-step limit), despiking (15% threshold), flatline removal
- **Missing data**: Rows dropped if soil moisture cannot be interpolated
- **Weather source**: Open-Meteo Historical Weather API (ERA5), linearly interpolated to minute resolution

### Physical Validation

The dataset includes physical consistency checks:
- Spearman correlation between `water_vol_to_24h` and `real_moisture_delta` computed per sector
- Irrigation events constrained to allowed window (06:00–18:00)
- Fertigation timeout prevents runaway events
- Soil moisture physically clamped to 0-100% range

---

## Español

### Resumen
Este documento describe el dataset público integrado en el sistema VRI Digital Twin para mejorar las respuestas RAG (Generación Aumentada por Recuperación) y el entrenamiento de modelos.

**Dataset:** Datos de Humedad del Suelo, Actuadores de Riego y Clima de un Ensayo de Riego de Precisión Multi-Sector  
**Ubicación:** Arnesano, Apulia, Italia  
**Período:** Febrero–Septiembre 2025 (temporada completa de cultivo)  
**Licencia:** CC BY 4.0  
**Citación:** Dataset disponible en Mendeley Data (2026)

### Características Clave
- **Telemetría real de actuadores**: Volumen de agua aplicado medido, no asumido
- **Configuración multi-cultivo**: 4 configuraciones diferentes compartiendo el mismo clima
- **Eventos de riego validados**: 789 eventos reconstruidos a partir de señales ruidosas de válvulas
- **Formato listo para ML**: Características y objetivos de 24 horas pre-alineados
- **Integración climática**: Datos de reanálisis ERA5 de Open-Meteo

### Sectores Incluidos en Este Sistema

| Sector | Tipo de Cultivo | Sustrato | Filas | Rango de Fechas | Archivo |
|--------|----------------|----------|-------|-----------------|---------|
| 1 | Tomate | Campo abierto | 9,531 | 2025-02-28 a 2025-09-04 | dataset_zone_1_preprocessed.csv |
| 2 | Tomate | Campo abierto | 11,929 | 2025-02-28 a 2025-09-23 | dataset_zone_2_preprocessed.csv |
| 4 | Calabacín | Campo abierto | 12,676 | 2025-03-01 a 2025-09-23 | dataset_zone_4_preprocessed.csv |
| 5 | Arándano | Campo abierto | 11,814 | 2025-02-11 a 2025-09-22 | dataset_zone_5_preprocessed.csv |

*Nota: Sector 3 (tomate en macetas, 1,118 filas) fue excluido debido a falla de sonda en junio.*

### Estructura de Datos

Cada archivo CSV contiene series temporales de resolución de 10 minutos con:

**Variables de Sensores:**
- `humidity_percentage`: Humedad del suelo (0-100%, contenido volumétrico de agua relativo)
- `soil_ph`: pH del suelo (rango típico 3-9)
- `soil_ce`: Conductividad eléctrica (µS/cm)
- `humidity_status`: Clase agronómica (0=peligro, 1=estrés, 2=óptimo, 3=exceso, 4=saturación)

**Variables Climáticas (reanálisis ERA5):**
- `weather_temp`: Temperatura del aire (°C)
- `weather_humidity`: Humedad relativa (%)
- `weather_rain`: Precipitación (mm)
- `weather_pressure`: Presión atmosférica (hPa)
- `weather_wind_speed`: Velocidad del viento (km/h)
- `weather_radiation`: Radiación solar (W/m²)

**Variables de Riego:**
- `irrigation_duration_minutes`: Minutos de riego en ventana de 10 min (0-10)
- `water_vol_to_24h`: Litros aplicados en las próximas 24 horas (forward-looking)
- `water_vol_past_4h`: Litros aplicados en las últimas 4 horas

**Objetivos (horizonte de 24 horas):**
- `target_point_24h`: Humedad del suelo 24 horas adelante
- `target_mean_24h`: Humedad media del suelo en las próximas 24 horas
- `real_moisture_delta`: Cambio de humedad realizado (no usar como característica - forward-looking)

**Características Temporales:**
- `month`, `day`, `hour`, `day_period`, `quarter`

### Estadísticas Clave

**Eventos de Riego (reconstruidos de telemetría de válvulas):**
- Total de eventos validados: 789
- Riegos estándar: 432
- Fertigaciones: 357
- Rango de fechas: 2025-02-17 a 2025-08-31
- Duración mediana: ~45 minutos
- Duración máxima: 9.53 horas (fertigaciones largas)

**Umbrales de Humedad del Suelo por Cultivo:**

| Cultivo | PMP | PMAD | CC | PS | Iniciar Riego | Detener Riego |
|---------|-----|------|----|----| --------------|---------------|
| Tomate (abierto) | 20% | 40% | 60% | 80% | <40% | >60% |
| Tomate (maceta) | 30% | 60% | 80% | 90% | <60% | >80% |
| Calabacín | 40% | 80% | 90% | 95% | <80% | >90% |
| Arándano | 35% | 70% | 90% | 95% | <50% | >60% |

*PMP = Punto de Marchitez Permanente, PMAD = Punto de Agotamiento de Manejo Permitido, CC = Capacidad de Campo, PS = Punto de Saturación*

### Casos de Uso para el Sistema RAG

Cuando los usuarios pregunten sobre:
1. **Patrones de riego del mundo real**: Referenciar los 789 eventos validados
2. **Dinámicas de humedad del suelo**: Citar rangos de humedad reales y comportamiento temporal
3. **Relaciones clima-riego**: Explicar correlaciones observadas en el dataset
4. **Requerimientos hídricos de cultivos**: Comparar Kc teórico FAO-56 con consumo medido
5. **Confiabilidad de sensores**: Discutir manejo de caídas y filtrado de calidad aplicado
6. **Entrenamiento de modelos ML**: Describir características, objetivos y pipeline de preprocesamiento

### Consultas Ejemplo que el RAG Puede Responder

- "¿Cuál fue la humedad promedio del suelo en campos de tomate durante el ensayo de 2025?"
- "¿Cuántos eventos de riego ocurrieron en el sector de calabacín?"
- "¿Cuál es la relación entre precipitación y frecuencia de riego?"
- "Muéstrame la duración típica de riego para arándanos."
- "¿Qué umbral de humedad del suelo activa el riego en tomates de campo abierto?"

### Notas de Calidad de Datos

- **Capa raw publicada**: Incluye caídas de sensores, lecturas constantes y picos para transparencia
- **Preprocesamiento aplicado**: Interpolación basada en tiempo (límite de 2 pasos), eliminación de picos (umbral 15%), remoción de constantes
- **Datos faltantes**: Filas eliminadas si la humedad del suelo no puede interpolarse
- **Fuente climática**: Open-Meteo Historical Weather API (ERA5), interpolado linealmente a resolución de minutos

### Validación Física

El dataset incluye verificaciones de consistencia física:
- Correlación de Spearman entre `water_vol_to_24h` y `real_moisture_delta` calculada por sector
- Eventos de riego limitados a ventana permitida (06:00–18:00)
- Timeout de fertigación previene eventos descontrolados
- Humedad del suelo físicamente limitada al rango 0-100%

---

## References / Referencias

- Dataset source: Arnesano precision irrigation trial, Italy, 2025
- Weather data: Open-Meteo Historical Weather API (ERA5 reanalysis)
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Processing pipeline: Available in dataset documentation
- CSV files location: `backend/data/datasets/dataset_zone_[1,2,4,5]_preprocessed.csv`
