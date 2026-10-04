"""
Script rapido para verificar que el RAG funciona
Ejecutar ANTES de iniciar servidores
"""

import sys
import os
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 60)
print("VERIFICACION RAPIDA DEL SISTEMA RAG")
print("=" * 60)

# 1. Verificar archivos de conocimiento
print("\n[1/5] Verificando archivos de conocimiento...")
kb_path = backend_path / "data" / "knowledge_base"

if not kb_path.exists():
    print(f"ERROR: No existe {kb_path}")
    sys.exit(1)

md_files = list(kb_path.glob("*.md"))
print(f"OK - Encontrados {len(md_files)} archivos .md")
for md_file in md_files:
    print(f"  - {md_file.name}")

# 2. Verificar API key
print("\n[2/5] Verificando API key de Groq...")
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    # Cargar desde .env
    env_file = backend_path / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    groq_key = line.split("=", 1)[1].strip()
                    os.environ["GROQ_API_KEY"] = groq_key
                    break

if groq_key and len(groq_key) > 20:
    print(f"OK - API key configurada (largo: {len(groq_key)} chars)")
else:
    print("ERROR: GROQ_API_KEY no configurada o invalida")
    print("Edita backend/.env y agrega tu API key")
    sys.exit(1)

# 3. Verificar dependencias
print("\n[3/5] Verificando dependencias...")
required_modules = [
    "langchain",
    "langchain_groq",
    "langchain_community",
    "faiss",
    "sentence_transformers",
]

missing = []
for module_name in required_modules:
    try:
        if module_name == "faiss":
            __import__("faiss")
        else:
            __import__(module_name)
        print(f"  OK - {module_name}")
    except ImportError:
        missing.append(module_name)
        print(f"  ERROR - {module_name} NO INSTALADO")

if missing:
    print(f"\nERROR: Faltan dependencias: {', '.join(missing)}")
    print("Ejecuta: cd backend && pip install -r requirements.txt")
    sys.exit(1)

# 4. Inicializar RAG service
print("\n[4/5] Inicializando servicio RAG...")
print("NOTA: Primera vez descarga modelo de 1.11 GB (5-10 min)")
print("Espera pacientemente...")

try:
    from app.services.rag_service import RAGService
    
    rag = RAGService(
        knowledge_base_path=str(kb_path),
        groq_api_key=groq_key
    )
    
    print("Inicializando RAG (cargando documentos y embeddings)...")
    rag.initialize()
    
    print("OK - RAG inicializado correctamente")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Hacer pregunta de prueba
print("\n[5/5] Probando consulta RAG...")
print("Pregunta: '¿Cuantos eventos de riego hay en el dataset publico?'")

try:
    result = rag.query(
        question="¿Cuantos eventos de riego hay en el dataset publico?",
        language="es"
    )
    
    print("\n" + "=" * 60)
    print("RESPUESTA DEL RAG:")
    print("=" * 60)
    print(result["answer"])
    print(f"\nFuentes citadas: {result['num_sources']}")
    print(f"Modelo usado: {result['model']}")
    
    # Verificar que mencione "789"
    if "789" in result["answer"]:
        print("\nOK - El RAG esta leyendo correctamente el dataset!")
    else:
        print("\nADVERTENCIA: La respuesta no menciona '789 eventos'")
        print("Verifica que el archivo 09_real_world_dataset.md este en knowledge_base")
    
    print("\n" + "=" * 60)
    print("VERIFICACION COMPLETA - TODO OK")
    print("=" * 60)
    print("\nPROXIMOS PASOS:")
    print("1. Abre una terminal y ejecuta:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload")
    print("\n2. Abre otra terminal y ejecuta:")
    print("   cd backend")
    print("   streamlit run streamlit_backend.py")
    print("\n3. Abre http://localhost:8501 en tu navegador")
    print("4. Selecciona 'RAG Chat' en el menu lateral")
    print("\n")
    
except Exception as e:
    print(f"ERROR en consulta: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
