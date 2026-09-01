# VRI Digital Twin - Guía de Inicio Rápido

## ✅ Cambios Realizados

### 1. **Eliminación de Gemini API**
- ❌ Eliminada dependencia `@google/genai` de `package.json`
- ❌ Eliminada configuración de `GEMINI_API_KEY` del `.env.example`
- ✅ Actualizado README.md con instrucciones nuevas

### 2. **Backend FastAPI Implementado**
Se ha creado un backend completo en FastAPI con:

**Estructura:**
```
backend/
├── app/
│   ├── main.py              # Aplicación principal
│   ├── core/
│   │   ├── config.py        # Configuración
│   │   └── database.py      # Conexión DB
│   └── api/v1/endpoints/    # Endpoints
│       ├── health.py        # Health checks
│       ├── fields.py        # Campos agrícolas
│       ├── sensors.py       # Telemetría
│       ├── rl_engine.py     # Motor RL
│       ├── irrigation.py    # Control de riego
│       └── reports.py       # Reportes
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Imagen Docker
└── README.md               # Documentación

**API Endpoints:**
- `GET /health` - Health check
- `GET /api/v1/fields` - Listar campos
- `POST /api/v1/rl-engine/infer-vri-rates` - Inferencia RL
- `POST /api/v1/irrigation/execute-decision` - Ejecutar riego
- `GET /api/v1/sensors` - Sensores
- `POST /api/v1/reports/generate` - Generar reportes
- Y muchos más...

### 3. **Frontend Actualizado**
- ✅ Creado `apiClient.ts` - Cliente API tipado
- ✅ Configuración de `.env.local` para apuntar al backend
- ✅ Eliminadas dependencias de Gemini

### 4. **Docker Compose**
- ✅ Configuración completa con PostgreSQL, Redis, FastAPI y React
- ✅ Dockerfile para backend y frontend

---

## 🚀 Iniciar Desarrollo (Opción 1: Local)

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend disponible en: `http://localhost:8000`
📚 Docs: `http://localhost:8000/docs`

### Frontend

```bash
# En otra terminal, desde la raíz del proyecto

# Instalar dependencias
npm install

# Ejecutar app
npm run dev
```

✅ Frontend disponible en: `http://localhost:3000`

---

## 🐳 Iniciar con Docker Compose (Opción 2: Recomendado)

Desde la raíz del proyecto:

```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

**Servicios:**
- 🌐 Frontend React: `http://localhost:3000`
- ⚙️ Backend FastAPI: `http://localhost:8000`
- 📚 API Docs: `http://localhost:8000/docs`
- 🗄️ PostgreSQL: `localhost:5432`
- 💾 Redis: `localhost:6379`

---

## 🔧 Configuración

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
VITE_APP_ENV=development
VITE_DEBUG=true
```

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://vri_admin:vri_secure_pass_2026@localhost:5432/vri_digital_twin
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## 📋 Checklist de Verificación

- [ ] Backend FastAPI corriendo en puerto 8000
- [ ] Frontend React corriendo en puerto 3000
- [ ] API Docs accesible en http://localhost:8000/docs
- [ ] Base de datos PostgreSQL conectada
- [ ] Redis conectado
- [ ] CORS habilitado en backend
- [ ] Entorno .env.local configurado en frontend

---

## 🌐 Próximos Pasos

1. **Base de Datos:**
   - Ejecutar migraciones Alembic para crear tablas
   - Cargar datos iniciales

2. **Autenticación:**
   - Implementar JWT authentication
   - Crear endpoints de login

3. **Modelos ORM:**
   - Definir modelos SQLAlchemy en `backend/app/models/`
   - Crear relaciones entre tablas

4. **Lógica de Negocio:**
   - Implementar servicios en `backend/app/services/`
   - Conectar endpoints con base de datos

5. **Frontend:**
   - Actualizar componentes para usar `apiClient.ts`
   - Eliminar datos mock cuando sea posible

---

## 📚 Recursos

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/)

---

## 🆘 Troubleshooting

### Backend no inicia
```bash
# Verificar Puerto 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Detener proceso en puerto
kill -9 <PID>  # macOS/Linux
```

### Error de Base de Datos
```bash
# Verificar conexión PostgreSQL
psql -U vri_admin -h localhost -d vri_digital_twin

# Verificar variables de entorno
echo $DATABASE_URL
```

### Error CORS
- Verificar `CORS_ORIGINS` en `backend/app/core/config.py`
- Debe incluir `http://localhost:3000` en desarrollo

---

## ✨ Cambios Resumidos

| Componente | Antes | Después |
|-----------|-------|---------|
| API | Gemini SDK | FastAPI + REST |
| Database | Mock data | PostgreSQL + TimescaleDB |
| Auth | Ninguno | JWT ready |
| Cache | Ninguno | Redis |
| Deployment | Vite solo | Docker Compose |

¡Listo para desarrollo! 🎉
