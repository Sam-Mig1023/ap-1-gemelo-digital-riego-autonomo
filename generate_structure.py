import os
import pathlib
import sys

def generate_tree(root='.', exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'node_modules', 'venv', '.git', '__pycache__', 'dist', 'build', '.kiro', '.vscode', '.idea'}
    
    tree_lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Excluir directorios no deseados
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        rel_path = os.path.relpath(dirpath, root)
        depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1
        indent = ('│   ' * (depth - 1)) + ('├── ' if depth > 0 else '')
        
        if rel_path != '.':
            tree_lines.append(f"{indent}{os.path.basename(dirpath)}/")
        
        file_indent = '│   ' * depth + '├── '
        for f in sorted(filenames):
            # Excluir archivos de cache y temporales
            if not f.endswith(('.pyc', '.pyo', '.log', '.tmp')):
                tree_lines.append(f"{file_indent}{f}")
    
    return '\n'.join(tree_lines)

if __name__ == '__main__':
    try:
        root_path = pathlib.Path(__file__).parent
        output = generate_tree(str(root_path))
        
        # Generar versión TXT
        out_file_txt = root_path / 'PROJECT_STRUCTURE.txt'
        out_file_txt.write_text(output, encoding='utf-8')
        print(f'Generated {out_file_txt}')
        
        # Generar versión Markdown
        md_output = f"""# 📁 Estructura del Proyecto - VRI Digital Twin

**Generado**: {pathlib.Path(__file__).stat().st_mtime}  
**Excluye**: `node_modules`, `venv`, `.git`, `__pycache__`, `dist`, `build`, `.kiro`, `.vscode`, `.idea`

---

## Árbol de Directorios

```
{output}
```

---

## Descripción de Carpetas Principales

### 📂 `src/` - Frontend React + TypeScript
- `components/` - 11 componentes React principales (GIS, Chatbot, RL Console, etc.)
- `services/` - Lógica de negocio (RL engine, Digital Twin, API client)
- `data/` - Datos mock (50K+ puntos de sensores)
- `types/` - Definiciones TypeScript
- `contexts/` - Context providers (Theme, Language)

### 📂 `backend/` - Backend FastAPI + Python
- `app/main.py` - Aplicación principal FastAPI
- `app/core/` - Configuración y base de datos
- `app/api/v1/endpoints/` - 6 módulos de endpoints REST
- `data/knowledge_base/` - Base de conocimiento agronómico (8 archivos .md)
- `requirements.txt` - Dependencias Python

### 📂 `public/` - Assets estáticos
- Favicon, imágenes, archivos públicos

### 📄 Archivos de Configuración
- `package.json` - Dependencias Node.js
- `tsconfig.json` - Configuración TypeScript
- `vite.config.ts` - Configuración Vite
- `docker-compose.yml` - Orquestación Docker
- `.env.example` - Variables de entorno de ejemplo

### 📄 Documentación
- `README.md` - Guía principal del proyecto
- `SETUP_GUIDE.md` - Guía de configuración detallada
- `CONTEXTO_PROYECTO_CLAUDE.md` - Contexto técnico completo
- `ESTADO_REQUISITOS.md` - Estado de cumplimiento de requisitos
"""
        out_file_md = root_path / 'PROJECT_STRUCTURE.md'
        out_file_md.write_text(md_output, encoding='utf-8')
        print(f'Generated {out_file_md}')
        
        print(f'Estructura del proyecto generada exitosamente en 2 formatos')
        
    except Exception as e:
        print('❌ Error generating structure:', e, file=sys.stderr)
        sys.exit(1)
