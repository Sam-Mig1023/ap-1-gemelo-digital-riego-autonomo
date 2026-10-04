# Integración de Langflow en el Gemelo Digital VRI

Este documento explica cómo hemos integrado [Langflow](https://www.langflow.org/) en nuestra arquitectura backend de FastAPI para permitir la creación visual de flujos RAG y Agentes Agronómicos sin escribir código (No-Code).

## Arquitectura de la Integración

Nuestro sistema consta de un frontend en **React**, un backend en **FastAPI** y el motor de IA. En lugar de procesar los prompts de Groq/Llama directamente en el código de React o de FastAPI, hemos creado un router puente (`langflow_router.py`) que se comunica con una instancia de Langflow ejecutándose en tu máquina o en la nube.

**El Flujo:**
1. El usuario hace una pregunta en el Chatbot Agronómico en React.
2. React envía la pregunta al nuevo endpoint del backend FastAPI: `POST /api/v1/langflow/chat-langflow`.
3. FastAPI toma esa pregunta y la empaqueta en el formato exacto que espera Langflow, y se la reenvía a `http://127.0.0.1:7860/api/v1/run/{FLOW_ID}`.
4. **Langflow** (la UI visual) recibe el texto, lo pasa por tu grafo (buscando en FAISS, usando LLMs, formateando), y devuelve la respuesta final a FastAPI.
5. FastAPI se la sirve al frontend.

---

## Cómo Ejecutarlo

### 1. Iniciar Langflow Visual
Abre una nueva terminal en tu proyecto y ejecuta:

```bash
cd backend
pip install langflow
python -m langflow run
```

Esto levantará el servidor visual en `http://127.0.0.1:7860`. Entra a esa URL en tu navegador.

### 2. Construir tu Agente Visual (No-Code)
1. En Langflow, haz clic en **New Project** y selecciona una plantilla de "Chatbot" o "Vector Store RAG".
2. Configura tu LLM (arrastra un bloque de **Groq** u OpenAI) y conéctalo al bloque de "Chat Input" y "Chat Output".
3. Guarda el flujo. Ve a los ajustes del flujo (icono de engranaje) y copia el **Flow ID** (un código largo como `f3e4d5c6-1234-abcd-xyz...`).

### 3. Conectar FastAPI a Langflow
Configura las siguientes variables de entorno antes de levantar el backend de FastAPI (o ponlas en un archivo `.env`):

```bash
export LANGFLOW_API_URL="http://127.0.0.1:7860/api/v1/run"
export LANGFLOW_FLOW_ID="tu-flow-id-copiado"
```

Luego, simplemente levanta el servidor backend como siempre:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4. Pruébalo desde el Frontend
Ahora, el frontend puede consumir la IA visual llamando al endpoint:
`http://localhost:8000/api/v1/langflow/chat-langflow`

## Beneficios para la Sustentación del Proyecto
Si tus profesores preguntan por qué Langflow:
* **Mantenibilidad:** Si las leyes agronómicas o la fuente del Dataset cambian, un ingeniero agrónomo puede actualizar el flujo entrando a la web de Langflow, subir el nuevo PDF y listo, sin tocar una sola línea de Python o React.
* **Flexibilidad:** Permite cambiar el cerebro del Gemelo Digital (ej. pasar de Llama-3 a Gemini 1.5) visualmente en 1 segundo.
* **Modularidad:** Separa por completo la lógica de negocio (FastAPI) de la lógica de razonamiento de IA (Langflow).
