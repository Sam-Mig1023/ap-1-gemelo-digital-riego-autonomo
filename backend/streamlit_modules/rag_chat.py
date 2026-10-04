"""
Módulo RAG Chat para Streamlit
Permite consultar el sistema RAG con conocimiento agronómico
"""
import streamlit as st
import requests
from datetime import datetime


def render_rag_chat(base_url: str):
    """Renderiza el módulo de chat con RAG"""
    
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 Chat RAG - Asistente Agronómico")
    st.markdown("Consulta la base de conocimiento agronómico usando RAG (Retrieval-Augmented Generation)")
    
    # Verificar salud del servicio RAG
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔍 Verificar Estado RAG", use_container_width=True):
            with st.spinner("Verificando..."):
                try:
                    response = requests.get(f"{base_url}/chat/health", timeout=5)
                    if response.status_code == 200:
                        health = response.json()
                        if health.get("initialized"):
                            st.success("✅ RAG Sistema Operativo")
                        else:
                            st.warning("⚠️ RAG no inicializado")
                        
                        # Mostrar detalles en un expander
                        with st.expander("Ver Detalles"):
                            st.json(health)
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ No se pudo conectar: {str(e)}")
    
    st.markdown("---")
    
    # Inicializar historial de chat en session_state
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []
    
    # Área de chat
    st.markdown("#### 💬 Conversación")
    
    # Mostrar historial de mensajes
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.rag_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 12px; border-radius: 8px; margin: 8px 0;">
                    <strong>👤 Tú:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #f5f5f5; padding: 12px; border-radius: 8px; margin: 8px 0;">
                    <strong>🤖 Asistente:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar fuentes si existen
                if "sources" in msg and msg["sources"]:
                    with st.expander(f"📚 Ver {len(msg['sources'])} Fuentes"):
                        for i, source in enumerate(msg["sources"], 1):
                            st.markdown(f"**Fuente {i}:** `{source.get('metadata', {}).get('source', 'unknown')}`")
                            st.text(source.get('content', '')[:200] + "...")
                            st.markdown("---")
    
    # Input para nueva pregunta
    st.markdown("#### 📝 Nueva Consulta")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_question = st.text_input(
            "Pregunta",
            placeholder="Ejemplo: ¿Cuántos eventos de riego hubo en el dataset público?",
            label_visibility="collapsed"
        )
    
    with col2:
        language = st.selectbox(
            "Idioma",
            options=["es", "en"],
            format_func=lambda x: "🇪🇸 ES" if x == "es" else "🇬🇧 EN",
            label_visibility="collapsed"
        )
    
    col_send, col_clear = st.columns([1, 1])
    
    with col_send:
        send_button = st.button("🚀 Enviar", use_container_width=True, type="primary")
    
    with col_clear:
        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            st.session_state.rag_messages = []
            st.rerun()
    
    # Procesar envío
    if send_button and user_question.strip():
        # Agregar mensaje del usuario
        st.session_state.rag_messages.append({
            "role": "user",
            "content": user_question,
            "timestamp": datetime.now().isoformat()
        })
        
        # Llamar a la API RAG
        with st.spinner("🔍 Consultando base de conocimiento..."):
            try:
                response = requests.post(
                    f"{base_url}/chat",
                    json={
                        "question": user_question,
                        "language": language
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Agregar respuesta del asistente
                    st.session_state.rag_messages.append({
                        "role": "assistant",
                        "content": result.get("answer", "No se recibió respuesta"),
                        "sources": result.get("sources", []),
                        "model": result.get("model", "unknown"),
                        "num_sources": result.get("num_sources", 0),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    st.success(f"✅ Respuesta generada con {result.get('num_sources', 0)} fuentes")
                    st.rerun()
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout: La consulta tardó demasiado. Intenta de nuevo.")
            except Exception as e:
                st.error(f"❌ Error al consultar RAG: {str(e)}")
    
    # Sugerencias de preguntas
    st.markdown("---")
    st.markdown("#### 💡 Preguntas Sugeridas")
    
    suggestions = [
        "¿Cuántos eventos de riego se registraron en el dataset público?",
        "¿Qué tipos de suelo son mejores para riego por aspersión?",
        "¿Cuánta agua necesita el maíz durante la floración?",
        "¿Cuáles son las normativas de riego en zonas áridas?",
        "¿Qué cultivos se monitorearon en el dataset de Italia?"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"💬 {suggestion[:50]}...", key=f"sug_{i}", use_container_width=True):
                st.session_state.rag_messages.append({
                    "role": "user",
                    "content": suggestion,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Auto-enviar la pregunta
                with st.spinner("🔍 Consultando..."):
                    try:
                        response = requests.post(
                            f"{base_url}/chat",
                            json={
                                "question": suggestion,
                                "language": "es"
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.rag_messages.append({
                                "role": "assistant",
                                "content": result.get("answer", "No se recibió respuesta"),
                                "sources": result.get("sources", []),
                                "model": result.get("model", "unknown"),
                                "num_sources": result.get("num_sources", 0),
                                "timestamp": datetime.now().isoformat()
                            })
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Información adicional
    with st.expander("ℹ️ Sobre el Sistema RAG"):
        st.markdown("""
        **RAG (Retrieval-Augmented Generation)** combina:
        
        1. **Búsqueda Semántica**: Encuentra información relevante en la base de conocimiento
        2. **Generación de Respuestas**: Usa Groq LLM (llama-3.3-70b) para crear respuestas contextuales
        
        **Base de Conocimiento Incluye:**
        - 🌽 Información de cultivos (maíz, trigo)
        - 🌱 Tipos de suelo y sensores
        - 💧 Sistemas de riego VRI
        - 📋 Normativas y regulaciones
        - 📊 Dataset público de Italia 2025 (789 eventos de riego)
        
        **Ventajas:**
        - ✅ Respuestas con fuentes citadas
        - ✅ Información verificable
        - ✅ Soporte bilingüe (ES/EN)
        - ✅ Actualizable sin reentrenar
        """)
