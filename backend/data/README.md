# Dataset de Riego Autónomo

Los datos crudos y procesados no se suben al repositorio por su tamaño. 
Para ejecutar el proyecto con datos reales, debes descargar el dataset manualmente.

**Enlace de descarga:**  
[https://data.mendeley.com/datasets/c837v6p8ph/2](https://data.mendeley.com/datasets/c837v6p8ph/2)

### Instrucciones
1. Descarga el archivo desde el enlace.
2. Descomprime el contenido.
3. Coloca las carpetas (`01_raw_data`, `02_processed_data`, etc.) dentro de este directorio (`backend/data/`).

### Calendario fenológico (`crop_calendar.csv`)

Este archivo es independiente del dataset de Mendeley. Se usa solo para mostrar
las fechas de siembra, floración y cosecha de las zonas del proyecto. Debe
contener las columnas `zona`, `cultivo`, `fecha_siembra`,
`fecha_floracion_esperada` y `fecha_cosecha`, con fechas verificadas para cada
zona. No se deben inferir esas fechas a partir del periodo de mediciones del
dataset. Mientras no se cuente con datos verificados, el calendario queda
vacío y las demás funciones del sistema pueden seguir utilizándose.
