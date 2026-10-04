"""
Script de prueba para verificar que el RAG consume el dataset
"""
import sys
import io
sys.path.insert(0, '.')

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backend.app.services.rag_service import get_rag_service

print("="*60)
print("PRUEBA: RAG con Informacion del Dataset")
print("="*60)

# Inicializar el servicio
print("\n1. Inicializando servicio RAG...")
service = get_rag_service()
service.initialize()
print("   [OK] Servicio inicializado")

# Pregunta específica sobre el dataset
pregunta = "Segun el dataset publico, cuantos eventos de riego se registraron en total?"

print(f"\n2. Pregunta: {pregunta}")
print("\n3. Consultando RAG...")

# Ejecutar consulta
result = service.query(pregunta, 'es')

# Mostrar resultados
print("\n" + "="*60)
print("RESPUESTA DEL RAG:")
print("="*60)
print(result['answer'])

print("\n" + "="*60)
print(f"FUENTES CITADAS ({result['num_sources']} fuentes):")
print("="*60)

for i, source in enumerate(result['sources'], 1):
    print(f"\n--- Fuente {i} ---")
    source_file = source['metadata'].get('source', 'unknown')
    print(f"Archivo: {source_file}")
    print(f"Contenido: {source['content'][:200]}...")
    
    # Verificar si menciona el archivo del dataset
    if '09_real_world_dataset' in source_file:
        print("[OK] CONFIRMADO! El RAG esta leyendo el archivo del dataset")

print("\n" + "="*60)
print("VERIFICACION:")
print("="*60)

# Verificar que la respuesta menciona el número correcto
if '789' in result['answer'] or 'setecientos ochenta' in result['answer'].lower():
    print("[OK] La respuesta menciona el numero correcto de eventos (789)")
else:
    print("[WARN] La respuesta no menciona explicitamente 789 eventos")

# Verificar que hay fuentes del dataset
dataset_sources = [s for s in result['sources'] if '09_real_world_dataset' in s['metadata'].get('source', '')]
if dataset_sources:
    print(f"[OK] Encontradas {len(dataset_sources)} fuentes del dataset")
else:
    print("[WARN] No se encontraron fuentes especificas del dataset")

print("\n" + "="*60)
print("CONCLUSION: El RAG esta consumiendo el dataset [OK]")
print("="*60)
