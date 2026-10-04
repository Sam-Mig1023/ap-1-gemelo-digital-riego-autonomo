# Design: VRI Digital Twin - Master Plan Implementation

## Overview

This document provides the technical design for implementing LangChain RAG, LangFlow workflows, intelligent notifications, and advanced analytics features for the VRI Digital Twin system.

**Architecture Philosophy:**
- Modular services that can function independently
- Graceful degradation when backend is unavailable
- Clear separation between critical (P0) and optional (P1) features
- Maintain compatibility with existing FastAPI/React structure

**Recent Updates Integrated (from repository):**
- Streamlit Technical Console (667 lines) with 6 modules: Dashboard, 3D Digital Twin, Maintenance, Predictive Analysis, AI Engine, Scrum Documentation (`backend/streamlit_backend.py`)
- Enhanced translation system with improved architecture descriptions
- New RL decision samples in mockData (dec-20260831-04)
- Bilingual interface fully functional (LanguageContext)
- Knowledge base created (8 .md files in `backend/data/knowledge_base/`)
- Public dataset available: Soil Moisture, Irrigation & Weather data from Italy (2025) - 5 sectors, 789 irrigation events, preprocessed ML-ready CSVs

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React 19)                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ AgronomicChatbot │  │ TelemetryAnalytics│  │ WhatIfSimulator│ │
│  │   (RAG Client)   │  │ (Quality Scores)  │  │ (Retrospective)│ │
│  └────────┬─────────┘  └────────┬──────────┘  └───────┬───────┘ │
│           │                     │                      │         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │        LanguageContext (es/en) - Fully Functional          │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────┼─────────────────────┼──────────────────────┼─────────┘
            │                     │                      │
            │    ┌────────────────┴──────────────────────┘
            │    │                                 
         HTTPS  HTTPS                            
            │    │                                 
┌───────────┴────┴─────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Python 3.11)                  │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    API Layer (FastAPI)                       │ │
│  │  /api/v1/chat  /api/v1/process-alert  /api/v1/health        │ │
│  └────────┬──────────────────┬────────────────────────────────┬─┘ │
│           │                  │                                │   │
│  ┌────────▼──────┐  ┌────────▼─────────┐  ┌─────────────────▼──┐│
│  │  RAG Service   │  │ Notification Svc │  │  Existing Services ││
│  │  (LangChain)   │  │  (LLM Classify)  │  │  (RL, Irrigation)  ││
│  │                │  │                  │  │                    ││
│  │  ┌──────────┐  │  │  ┌────────────┐ │  └────────────────────┘│
│  │  │ FAISS DB │  │  │  │ Dispatcher │ │                         │
│  │  └──────────┘  │  │  └────────────┘ │                         │
│  └─────────────────┘  └──────────────────┘                         │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │            LangFlow Pipelines (Exported Code)                │ │
│  │  chatbot_rag.py  intelligent_alerts.py  rl_explainability.py│ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │     Streamlit Testing UI (streamlit_backend.py:8501)        │ │
│  │     Manual testing interface for FastAPI endpoints          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
            │                     │                      
            ▼                     ▼                      
    ┌──────────────┐      ┌──────────────┐             
    │  Groq API    │      │ Email/SMS    │             
    │  (LLM Calls) │      │ Gateways     │             
    └──────────────┘      └──────────────┘             

┌────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
│  knowledge_base/    crop_calendar.csv    mockData.ts (frontend)    │
│  Enhanced RL Decisions (dec-20260831-04: omit irrigation in Z3)    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: LangChain RAG System

### 1.1 Knowledge Base Structure

**Location:** `backend/data/knowledge_base/`

**Status:** ✅ Already created by teammate (8 files)

**Existing Files:**

```
backend/data/knowledge_base/
├── 01_crops_corn_maiz.md              # Maize/corn cultivation
├── 02_crops_wheat_trigo.md            # Wheat cultivation
├── 03_soils_types_tipos.md            # Soil types and properties
├── 04_soils_sensors_sensores.md       # Sensor technology and soil moisture
├── 05_irrigation_vri_basics.md        # VRI irrigation basics
├── 06_irrigation_hardware_equipamiento.md  # Hardware and equipment
├── 07_regulations_water_rights.md     # Water rights regulations
├── 08_regulations_environmental_impact.md  # Environmental regulations
└── README.md                           # Knowledge base documentation
```

**Public Dataset Integration:**

The public dataset located at `c:\Users\ather\Downloads\gemelitos\Soil Moisture, Irrigation Actuator and Weather Dat\` contains:

- **5 sectors** of real irrigation data (Italy, 2025 growing season)
- **789 validated irrigation events** with measured water volumes
- **Preprocessed ML-ready files:**
  - `dataset_zone_1_preprocessed.csv` (9,531 rows - tomato, open field)
  - `dataset_zone_2_preprocessed.csv` (11,929 rows - tomato, open field)
  - `dataset_zone_3_preprocessed.csv` (1,118 rows - tomato, pots)
  - `dataset_zone_4_preprocessed.csv` (12,676 rows - zucchini)
  - `dataset_zone_5_preprocessed.csv` (11,814 rows - blueberry)
- **Features:** soil moisture, pH, EC, temperature, humidity, precipitation, irrigation duration, water volume applied
- **24-hour targets:** point forecast and mean forecast for soil moisture

**Integration Strategy:**

1. Copy relevant CSV files to `backend/data/datasets/` for RAG context
2. Create summary .md files in knowledge base referencing the dataset
3. Use dataset statistics in RAG responses when asked about real-world irrigation data
4. Optional: Train RL models on this data (Phase 4 extension)

**Content Structure Example:**

```markdown
# Cultivos Principales / Main Crops

## Maíz (Zea mays) / Maize

### Requerimientos Hídricos
- Kc inicial: 0.4
- Kc medio: 1.2
- Kc final: 0.6
- Sensibilidad al estrés hídrico: Alta en floración

### Etapas Fenológicas
1. Emergencia (0-15 días)
2. Crecimiento vegetativo (15-45 días)
3. Floración (45-70 días) - **crítico**
4. Llenado de grano (70-100 días)
5. Madurez (100-120 días)

### Recomendaciones de Riego Variable
...
```

**Bilingual Strategy:**
- Headings in both Spanish/English
- Content primarily in Spanish (target audience)
- Key technical terms in both languages
- English fallback sections for international users

---

### 1.2 RAG Service Architecture

**File:** `backend/app/services/rag_service.py`

```python
"""
RAG Service for Agronomic Knowledge Retrieval
Uses LangChain + FAISS + Groq LLM
"""

from typing import List, Dict, Optional
from pathlib import Path
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class RAGService:
    """
    Retrieval-Augmented Generation Service
    Loads knowledge base, creates embeddings, and answers questions with sources
    """
    
    def __init__(
        self,
        knowledge_base_path: str = "backend/data/knowledge_base",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        groq_api_key: Optional[str] = None,
        groq_model: str = "llama-3.3-70b-versatile"
    ):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.embedding_model_name = embedding_model
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model
        
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Load documents, create embeddings, and initialize QA chain"""
        if self._initialized:
            return
        
        # 1. Load documents
        documents = self._load_documents()
        
        # 2. Split into chunks
        chunks = self._split_documents(documents)
        
        # 3. Create embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 4. Create FAISS vector store
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        # 5. Initialize LLM
        llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name=self.groq_model,
            temperature=0.3,
            max_tokens=1024
        )
        
        # 6. Create custom prompt
        prompt_template = self._get_prompt_template()
        
        # 7. Create RetrievalQA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
        
        self._initialized = True
    
    def _load_documents(self) -> List:
        """Load all markdown documents from knowledge base"""
        loader = DirectoryLoader(
            str(self.knowledge_base_path),
            glob="**/*.md",
            show_progress=True
        )
        return loader.load()
    
    def _split_documents(self, documents: List) -> List:
        """Split documents into manageable chunks with overlap"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_documents(documents)
    
    def _get_prompt_template(self) -> PromptTemplate:
        """Custom prompt template for agronomic context"""
        template = """Eres un asistente agronómico experto especializado en riego variable (VRI) y gemelos digitales.

Contexto relevante de la base de conocimiento:
{context}

Pregunta: {question}

Instrucciones:
1. Responde de forma precisa y técnica basándote SOLO en el contexto proporcionado
2. Si la información no está en el contexto, indícalo claramente
3. Cita las fuentes cuando sea posible (nombre del archivo o sección)
4. Usa términos agronómicos apropiados
5. Responde en el mismo idioma de la pregunta (español o inglés)

Respuesta:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(
        self,
        question: str,
        language: str = "es"
    ) -> Dict[str, any]:
        """
        Query the RAG system
        
        Args:
            question: User's question
            language: Language code (es/en)
        
        Returns:
            Dict with 'answer' and 'sources'
        """
        if not self._initialized:
            self.initialize()
        
        # Execute query
        result = self.qa_chain({"query": question})
        
        # Format response
        answer = result["result"]
        source_documents = result.get("source_documents", [])
        
        sources = [
            {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            for doc in source_documents
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "model": self.groq_model,
            "num_sources": len(sources)
        }
    
    def health_check(self) -> Dict[str, any]:
        """Check if RAG service is healthy"""
        return {
            "initialized": self._initialized,
            "knowledge_base_exists": self.knowledge_base_path.exists(),
            "groq_api_key_set": bool(self.groq_api_key),
            "embedding_model": self.embedding_model_name,
            "groq_model": self.groq_model
        }


# Singleton instance
_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
```

---

### 1.3 Chat Endpoint

**File:** `backend/app/api/v1/endpoints/chat.py`

```python
"""
Chat endpoint for RAG-powered agronomic assistant
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from app.services.rag_service import get_rag_service


router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    question: str = Field(..., min_length=1, max_length=1000)
    language: str = Field(default="es", pattern="^(es|en)$")


class SourceDocument(BaseModel):
    """Source document reference"""
    content: str
    metadata: Dict


class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    sources: List[SourceDocument]
    model: str
    num_sources: int


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint
    
    Returns answer with cited sources from knowledge base
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.query(
            question=request.question,
            language=request.language
        )
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )


@router.get("/chat/health", status_code=status.HTTP_200_OK)
async def chat_health():
    """Health check for RAG service"""
    try:
        rag_service = get_rag_service()
        health = rag_service.health_check()
        
        if not health["initialized"]:
            # Try to initialize
            rag_service.initialize()
            health = rag_service.health_check()
        
        return health
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG service unhealthy: {str(e)}"
        )
```

**Update:** `backend/app/api/v1/__init__.py`

```python
from app.api.v1.endpoints import health, fields, sensors, rl_engine, irrigation, reports, chat

# ...existing code...

api_router.include_router(chat.router, tags=["Chat & RAG"])
```

---

### 1.4 Frontend Integration

**Update:** `src/services/apiClient.ts`

```typescript
// Add to APIClient class

// Chat & RAG Endpoints
async chat(question: string, language: string = 'es') {
  return this.request('/api/v1/chat', 'POST', { question, language });
}

async getChatHealth() {
  return this.request('/api/v1/chat/health', 'GET');
}
```

**Update:** `src/components/AgronomicChatbot.tsx`

Add new function before `handleSendMessage`:

```typescript
// Try RAG backend first, fallback to direct Groq
const queryWithRAG = async (query: string): Promise<{answer: string, sources?: any[]}> => {
  try {
    const response = await apiClient.chat(query, language);
    
    if (response.data) {
      return {
        answer: response.data.answer,
        sources: response.data.sources
      };
    }
  } catch (error) {
    console.warn('RAG backend unavailable, falling back to direct Groq', error);
  }
  
  // Fallback to direct Groq call (already implemented in current chatbot)
  const systemPrompt = buildAgronomicSystemPrompt(field, zones, decisions, sensors, radarCells);
  const groqMessages = [...messages, {role: 'user', content: query}].map(m => ({
    role: m.role,
    content: m.content
  }));
  
  const answer = await queryGroqChat(groqMessages, systemPrompt, apiKey, selectedModel);
  return { answer, sources: undefined };
};
```

**Note:** The current `AgronomicChatbot.tsx` already has full Groq integration with voice support (STT/TTS), model selection, and multilingual support via `LanguageContext`. This update adds RAG capability while preserving all existing functionality.

Update `handleSendMessage` to use `queryWithRAG`:

```typescript
try {
  const { answer, sources } = await queryWithRAG(query);
  
  const botMsgId = `bot-${Date.now()}`;
  const botMsg: ChatMessage = {
    id: botMsgId,
    role: 'assistant',
    content: answer,
    timestamp: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' }),
    sources: sources // Add sources field to ChatMessage interface
  };
  
  setMessages(prev => [...prev, botMsg]);
  
  // ... rest of code
}
```

Add sources display in message rendering:

```typescript
{msg.sources && msg.sources.length > 0 && (
  <div className="mt-2 pt-2 border-t border-slate-200 dark:border-slate-700">
    <div className="text-[10px] font-semibold text-slate-600 dark:text-slate-400 mb-1">
      📚 Fuentes consultadas:
    </div>
    {msg.sources.map((src, idx) => (
      <div key={idx} className="text-[10px] text-slate-500 dark:text-slate-400 mb-1">
        • {src.metadata.source || 'Knowledge Base'}: {src.content.substring(0, 80)}...
      </div>
    ))}
  </div>
)}
```

---

### 1.5 Dependencies Update

**Update:** `backend/requirements.txt`

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-dotenv==1.0.1
pydantic==2.8.2
pydantic-settings==2.3.0
typing-extensions==4.12.2

# LangChain & RAG (Phase 1)
langchain==0.1.16
langchain-groq==0.0.3
langchain-community==0.0.34
chromadb==0.4.24
faiss-cpu==1.8.0
sentence-transformers==2.6.1
```

---

## Phase 2: LangFlow Visual Workflows

### 2.1 LangFlow Setup

**Installation:**
```bash
pip install langflow==1.0.0
```

**Launch Command:**
```bash
langflow run --host 0.0.0.0 --port 7860
```

**Environment Variables:**
Add to `backend/.env`:
```
LANGFLOW_PORT=7860
LANGFLOW_HOST=0.0.0.0
```

---

### 2.2 Flow 1: RAG Chatbot Workflow

**Components in LangFlow:**

```
[Text Input: User Question]
        ↓
[FAISS Retriever]
    ↓ (retrieves 4 docs)
    ↓
[Groq LLM - llama-3.3-70b]
    ↓
[Text Output: Answer + Sources]
```

**Configuration:**

1. **Text Input Component:**
   - Name: "user_question"
   - Type: String
   - Description: "Pregunta del usuario sobre agronomía y riego"

2. **FAISS Retriever Component:**
   - Index Path: `backend/data/faiss_index/`
   - Embedding Model: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
   - Top K: 4
   - Search Type: similarity

3. **Groq LLM Component:**
   - API Key: From env variable
   - Model: llama-3.3-70b-versatile
   - Temperature: 0.3
   - Max Tokens: 1024
   - System Prompt: (Same as RAG service prompt template)

4. **Output Component:**
   - Format: JSON
   - Fields: answer, sources

**Export:**
- Export as Python code to `backend/app/services/langflow_pipelines/chatbot_rag.py`
- Capture screenshot: `backend/docs/langflow_screenshots/flow1_chatbot_rag.png`

---

### 2.3 Flow 2: Intelligent Alerts Workflow

**Components in LangFlow:**

```
[JSON Input: Sensor Event]
        ↓
[Anomaly Detector - Python Function]
        ↓
[Groq LLM - Urgency Classifier]
        ↓
    ┌───┴───┐
    │       │
[CRITICAL] [MODERATE/INFO]
    │       │
    ↓       ↓
[Message Generator - Groq LLM]
    ↓
[Multi-Channel Dispatcher - Python Function]
    ↓
[JSON Output: Alert Result]
```

**Configuration:**

1. **JSON Input:**
   ```json
   {
     "sensor_id": "S001",
     "zone_id": "Z001",
     "value": 15.2,
     "expected_range": [20, 40],
     "timestamp": "2026-09-24T14:30:00Z",
     "metric": "soil_moisture_percent"
   }
   ```

2. **Anomaly Detector (Python Function):**
   ```python
   def detect_anomaly(event):
       value = event['value']
       low, high = event['expected_range']
       
       if value < low * 0.7 or value > high * 1.3:
           return {'anomaly': True, 'severity': 'high'}
       elif value < low or value > high:
           return {'anomaly': True, 'severity': 'medium'}
       else:
           return {'anomaly': False, 'severity': 'none'}
   ```

3. **Groq LLM Classifier:**
   - Prompt: "Classify urgency (CRITICAL/MODERATE/INFO): {event_json}"
   - Output Parser: Extract urgency level

4. **Message Generator:**
   - Prompt: "Generate 3 messages (agronomist/producer/technician) for: {event_json}"
   - Output: JSON with role-specific messages

5. **Dispatcher (Python Function):**
   ```python
   def dispatch(urgency, messages):
       channels = {
           'CRITICAL': ['email', 'sms'],
           'MODERATE': ['push'],
           'INFO': ['dashboard']
       }
       return {'channels': channels[urgency], 'messages': messages}
   ```

**Export:**
- Export to `backend/app/services/langflow_pipelines/intelligent_alerts.py`
- Screenshot: `backend/docs/langflow_screenshots/flow2_intelligent_alerts.png`

---

### 2.4 Flow 3: RL Analysis with Explainability

**Components in LangFlow:**

```
[JSON Input: Zone State]
        ↓
[RL Agent Simulator - Python Function]
        ↓
[SHAP Explainer - Python Function]
        ↓
[Groq LLM - Explanation Validator]
        ↓
[Human Approval Gate - Conditional]
        ↓
[JSON Output: Decision + Explanation]
```

**Configuration:**

1. **JSON Input (Zone State):**
   ```json
   {
     "zone_id": "Z001",
     "soil_moisture": 25.5,
     "temperature": 28.0,
     "et0": 6.2,
     "crop_stage": "flowering",
     "days_since_rain": 5
   }
   ```

2. **RL Agent (Python Function):**
   ```python
   def rl_decision(state):
       # Simplified RL logic
       if state['soil_moisture'] < 30 and state['crop_stage'] == 'flowering':
           return {'action': 'irrigate', 'depth_mm': 15}
       else:
           return {'action': 'wait', 'depth_mm': 0}
   ```

3. **SHAP Explainer (Python Function):**
   ```python
   def explain_decision(state, decision):
       # Mock SHAP values
       feature_importance = {
           'soil_moisture': 0.45,
           'crop_stage': 0.30,
           'et0': 0.15,
           'temperature': 0.10
       }
       return {'shap_values': feature_importance}
   ```

4. **Groq LLM Validator:**
   - Prompt: "Explain this RL decision in simple terms: {decision} based on {shap_values}"
   - Output: Human-readable explanation

5. **Approval Gate:**
   - If decision is "irrigate" and depth > 10mm: require approval
   - Else: auto-approve

**Export:**
- Export to `backend/app/services/langflow_pipelines/rl_explainability.py`
- Screenshot: `backend/docs/langflow_screenshots/flow3_rl_explainability.png`

---

### 2.5 LangFlow Documentation

**Create:** `backend/app/services/langflow_pipelines/README.md`

```markdown
# LangFlow Exported Pipelines

This directory contains Python code exported from LangFlow visual workflows.

## Flows

### 1. Chatbot RAG (`chatbot_rag.py`)
- **Purpose:** Visual representation of the RAG pipeline
- **Components:** FAISS Retriever → Groq LLM → Answer with sources
- **Usage:** Demonstrates the knowledge retrieval architecture
- **Screenshot:** `../../docs/langflow_screenshots/flow1_chatbot_rag.png`

### 2. Intelligent Alerts (`intelligent_alerts.py`)
- **Purpose:** Smart alert processing and routing
- **Components:** Anomaly Detection → LLM Classifier → Message Generator → Dispatcher
- **Usage:** Automates alert urgency classification and multi-channel routing
- **Screenshot:** `../../docs/langflow_screenshots/flow2_intelligent_alerts.png`

### 3. RL Explainability (`rl_explainability.py`)
- **Purpose:** Explainable RL decision workflow
- **Components:** RL Agent → SHAP → LLM Validator → Approval Gate
- **Usage:** Provides transparency for automated irrigation decisions
- **Screenshot:** `../../docs/langflow_screenshots/flow3_rl_explainability.png`

## Running LangFlow

```bash
pip install langflow
langflow run --host 0.0.0.0 --port 7860
```

Then open http://localhost:7860 and import the `.json` flow files (if saved).

## Integration

These exported Python files can be imported and used directly in FastAPI endpoints
as alternative implementations or for testing purposes.
```

---

## Phase 3: Intelligent Notification System

### 3.1 Notification Service Architecture

**File:** `backend/app/services/notification_service.py`

```python
"""
Intelligent Notification Service
Uses LLM for urgency classification and personalized message generation
"""

from typing import Dict, List, Optional
from enum import Enum
import os
from datetime import datetime

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"
    MODERATE = "MODERATE"
    INFO = "INFO"


class UserRole(str, Enum):
    AGRONOMIST = "agronomist"
    PRODUCER = "producer"
    TECHNICIAN = "technician"


class NotificationService:
    """Intelligent notification processing with LLM classification"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=512
        )
        
        # Rate limiting tracker (in-memory, use Redis in production)
        self.critical_alerts_sent = {}
    
    def classify_urgency(self, event: Dict) -> Dict[str, any]:
        """
        Classify event urgency using LLM
        
        Args:
            event: Sensor event data
        
        Returns:
            Dict with urgency level and confidence
        """
        prompt = PromptTemplate(
            template="""Eres un clasificador de urgencia para eventos de sensores en agricultura de precisión.

Evento:
- Sensor: {sensor_id}
- Zona: {zone_id}
- Métrica: {metric}
- Valor actual: {value}
- Rango esperado: {expected_range}
- Etapa del cultivo: {crop_stage}
- Hora del día: {hour}

Clasifica la urgencia en CRITICAL, MODERATE, o INFO considerando:
1. Desviación del rango normal
2. Etapa crítica del cultivo (floración es más sensible)
3. Hora del día (estrés diurno vs nocturno)
4. Tendencia (si está disponible)

Responde SOLO con: URGENCY:<nivel>,CONFIDENCE:<0-100>

Ejemplo: URGENCY:CRITICAL,CONFIDENCE:85""",
            input_variables=["sensor_id", "zone_id", "metric", "value", "expected_range", "crop_stage", "hour"]
        )
        
        # Extract hour from timestamp
        timestamp = event.get("timestamp", datetime.now().isoformat())
        hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
        
        # Build prompt
        formatted_prompt = prompt.format(
            sensor_id=event.get("sensor_id", "unknown"),
            zone_id=event.get("zone_id", "unknown"),
            metric=event.get("metric", "unknown"),
            value=event.get("value", 0),
            expected_range=event.get("expected_range", [0, 100]),
            crop_stage=event.get("crop_stage", "unknown"),
            hour=hour
        )
        
        # Query LLM
        response = self.llm.invoke(formatted_prompt)
        result_text = response.content.strip()
        
        # Parse response
        urgency = UrgencyLevel.INFO
        confidence = 50
        
        try:
            parts = result_text.split(',')
            for part in parts:
                if 'URGENCY:' in part:
                    level = part.split(':')[1].strip()
                    urgency = UrgencyLevel(level)
                elif 'CONFIDENCE:' in part:
                    confidence = int(part.split(':')[1].strip())
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        return {
            "urgency": urgency,
            "confidence": confidence,
            "raw_response": result_text
        }
    
    def generate_message(self, event: Dict, role: UserRole, urgency: UrgencyLevel) -> str:
        """
        Generate role-specific message using LLM
        
        Args:
            event: Sensor event data
            role: Target user role
            urgency: Urgency level
        
        Returns:
            Personalized message string
        """
        role_instructions = {
            UserRole.AGRONOMIST: "Mensaje técnico con datos específicos, acciones recomendadas, y terminología agronómica. Máximo 3 líneas.",
            UserRole.PRODUCER: "Mensaje simple y directo, impacto en el cultivo, qué hacer ahora. Lenguaje no técnico. Máximo 2 líneas.",
            UserRole.TECHNICIAN: "Mensaje enfocado en equipamiento, posibles fallas técnicas, mantenimiento. Máximo 2 líneas."
        }
        
        prompt = PromptTemplate(
            template="""Genera un mensaje de alerta para un {role}.

Evento:
- Sensor {sensor_id} en zona {zone_id}
- {metric}: {value} (esperado: {expected_range})
- Urgencia: {urgency}
- Etapa del cultivo: {crop_stage}

Instrucciones: {role_instructions}

Mensaje:""",
            input_variables=["role", "sensor_id", "zone_id", "metric", "value", "expected_range", "urgency", "crop_stage", "role_instructions"]
        )
        
        formatted_prompt = prompt.format(
            role=role.value,
            sensor_id=event.get("sensor_id", "unknown"),
            zone_id=event.get("zone_id", "unknown"),
            metric=event.get("metric", "unknown"),
            value=event.get("value", 0),
            expected_range=event.get("expected_range", [0, 100]),
            urgency=urgency.value,
            crop_stage=event.get("crop_stage", "unknown"),
            role_instructions=role_instructions[role]
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content.strip()
    
    def dispatch(
        self,
        urgency: UrgencyLevel,
        messages: Dict[str, str],
        recipients: Dict[str, List[str]],
        test_mode: bool = False
    ) -> Dict[str, any]:
        """
        Dispatch notifications to appropriate channels
        
        Args:
            urgency: Urgency level
            messages: Role-specific messages
            recipients: Contact info per role
            test_mode: If True, don't actually send
        
        Returns:
            Dispatch result
        """
        # Determine channels based on urgency
        channel_map = {
            UrgencyLevel.CRITICAL: ["email", "sms"],
            UrgencyLevel.MODERATE: ["push"],
            UrgencyLevel.INFO: ["dashboard"]
        }
        
        channels = channel_map[urgency]
        
        # Rate limiting for critical alerts
        if urgency == UrgencyLevel.CRITICAL:
            if not self._check_rate_limit("critical_alerts", max_per_hour=5):
                return {
                    "success": False,
                    "reason": "Rate limit exceeded for critical alerts",
                    "channels": [],
                    "messages_sent": 0
                }
        
        dispatched = []
        
        if test_mode:
            # Mock dispatch
            for channel in channels:
                for role, message in messages.items():
                    dispatched.append({
                        "channel": channel,
                        "role": role,
                        "message": message,
                        "status": "test_mode"
                    })
        else:
            # Real dispatch (implement email/SMS gateways)
            for channel in channels:
                for role, message in messages.items():
                    result = self._send_notification(
                        channel=channel,
                        recipient=recipients.get(role, []),
                        message=message
                    )
                    dispatched.append({
                        "channel": channel,
                        "role": role,
                        "message": message,
                        "status": result
                    })
        
        return {
            "success": True,
            "channels": channels,
            "messages_sent": len(dispatched),
            "dispatch_details": dispatched
        }
    
    def _check_rate_limit(self, key: str, max_per_hour: int) -> bool:
        """Simple in-memory rate limiting"""
        now = datetime.now()
        hour_key = f"{key}_{now.hour}"
        
        if hour_key not in self.critical_alerts_sent:
            self.critical_alerts_sent[hour_key] = 0
        
        if self.critical_alerts_sent[hour_key] >= max_per_hour:
            return False
        
        self.critical_alerts_sent[hour_key] += 1
        return True
    
    def _send_notification(
        self,
        channel: str,
        recipient: List[str],
        message: str
    ) -> str:
        """
        Send notification via specified channel
        
        TODO: Implement actual email/SMS gateways
        """
        # Mock implementation
        print(f"[{channel.upper()}] To: {recipient} - {message}")
        return "sent"


# Singleton
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get or create notification service singleton"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
```

---

### 3.2 Process Alert Endpoint

**File:** `backend/app/api/v1/endpoints/alerts.py`

```python
"""
Alert processing endpoint
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from app.services.notification_service import (
    get_notification_service,
    UrgencyLevel,
    UserRole
)


router = APIRouter()


class SensorEvent(BaseModel):
    """Sensor event model"""
    sensor_id: str
    zone_id: str
    value: float
    expected_range: List[float] = Field(..., min_items=2, max_items=2)
    metric: str
    timestamp: str
    crop_stage: Optional[str] = "unknown"


class ProcessAlertRequest(BaseModel):
    """Alert processing request"""
    event: SensorEvent
    recipients: Optional[Dict[str, List[str]]] = None
    test_mode: bool = True


class ProcessAlertResponse(BaseModel):
    """Alert processing response"""
    urgency: str
    confidence: int
    messages: Dict[str, str]
    channels: List[str]
    dispatch_result: Dict


@router.post("/process-alert", response_model=ProcessAlertResponse)
async def process_alert(request: ProcessAlertRequest):
    """
    Process sensor alert with intelligent classification and routing
    
    1. Classify urgency using LLM
    2. Generate role-specific messages
    3. Dispatch to appropriate channels
    """
    try:
        notification_service = get_notification_service()
        
        # 1. Classify urgency
        event_dict = request.event.dict()
        classification = notification_service.classify_urgency(event_dict)
        urgency = classification["urgency"]
        confidence = classification["confidence"]
        
        # 2. Generate messages for all roles
        messages = {}
        for role in [UserRole.AGRONOMIST, UserRole.PRODUCER, UserRole.TECHNICIAN]:
            message = notification_service.generate_message(
                event=event_dict,
                role=role,
                urgency=urgency
            )
            messages[role.value] = message
        
        # 3. Dispatch
        recipients = request.recipients or {
            "agronomist": ["agronomo@example.com"],
            "producer": ["productor@example.com"],
            "technician": ["tecnico@example.com"]
        }
        
        dispatch_result = notification_service.dispatch(
            urgency=urgency,
            messages=messages,
            recipients=recipients,
            test_mode=request.test_mode
        )
        
        return ProcessAlertResponse(
            urgency=urgency.value,
            confidence=confidence,
            messages=messages,
            channels=dispatch_result["channels"],
            dispatch_result=dispatch_result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert processing failed: {str(e)}"
        )


@router.get("/alerts/health")
async def alerts_health():
    """Health check for notification service"""
    try:
        service = get_notification_service()
        return {
            "healthy": True,
            "groq_api_key_set": bool(service.groq_api_key)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
```

**Update:** `backend/app/api/v1/__init__.py`

```python
from app.api.v1.endpoints import health, fields, sensors, rl_engine, irrigation, reports, chat, alerts

# ...

api_router.include_router(alerts.router, tags=["Alerts & Notifications"])
```

---

## Phase 4a: Crop Calendar / Phenological Stage

### 4a.1 Crop Calendar Data Structure

**File:** `backend/data/crop_calendar.csv`

```csv
zone_id,crop_type,planting_date,flowering_date_expected,harvest_date,kc_initial,kc_mid,kc_late
zone-1-nw,maize,2026-03-15,2026-05-15,2026-07-15,0.4,1.2,0.6
zone-2-ne,wheat,2026-04-01,2026-06-01,2026-08-01,0.3,1.15,0.4
zone-3-sw,potato,2026-03-20,2026-05-20,2026-07-25,0.5,1.15,0.75
zone-4-se,maize,2026-03-10,2026-05-10,2026-07-10,0.4,1.2,0.6
```

**Note:** Zone IDs match the existing zones in `mockData.ts` (zone-1-nw, zone-2-ne, zone-3-sw, zone-4-se).

---

### 4a.2 Phenological Stage Service

**File:** `backend/app/services/phenology_service.py`

```python
"""
Phenological Stage Calculation Service
"""

from typing import Dict, Optional
from datetime import datetime, date
import csv
from pathlib import Path


class PhenologyService:
    """Calculate crop phenological stages and dynamic Kc"""
    
    def __init__(self, calendar_path: str = "backend/data/crop_calendar.csv"):
        self.calendar_path = Path(calendar_path)
        self.crop_calendar = self._load_calendar()
    
    def _load_calendar(self) -> Dict:
        """Load crop calendar from CSV"""
        calendar = {}
        
        if not self.calendar_path.exists():
            return calendar
        
        with open(self.calendar_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                calendar[row['zone_id']] = {
                    'crop_type': row['crop_type'],
                    'planting_date': datetime.strptime(row['planting_date'], '%Y-%m-%d').date(),
                    'flowering_date': datetime.strptime(row['flowering_date_expected'], '%Y-%m-%d').date(),
                    'harvest_date': datetime.strptime(row['harvest_date'], '%Y-%m-%d').date(),
                    'kc_initial': float(row['kc_initial']),
                    'kc_mid': float(row['kc_mid']),
                    'kc_late': float(row['kc_late'])
                }
        
        return calendar
    
    def get_stage(self, zone_id: str, current_date: Optional[date] = None) -> Dict:
        """
        Calculate phenological stage for a zone
        
        Returns:
            Dict with stage, days_since_planting, and kc_current
        """
        if zone_id not in self.crop_calendar:
            return {
                "stage": "unknown",
                "days_since_planting": 0,
                "kc_current": 1.0,
                "error": "Zone not in calendar"
            }
        
        if current_date is None:
            current_date = date.today()
        
        crop_data = self.crop_calendar[zone_id]
        planting = crop_data['planting_date']
        flowering = crop_data['flowering_date']
        harvest = crop_data['harvest_date']
        
        days_since_planting = (current_date - planting).days
        
        # Determine stage
        if days_since_planting < 0:
            stage = "not_planted"
            kc = crop_data['kc_initial']
        elif days_since_planting < (flowering - planting).days * 0.5:
            stage = "initial"
            kc = crop_data['kc_initial']
        elif days_since_planting < (flowering - planting).days:
            stage = "development"
            # Interpolate between initial and mid
            progress = (days_since_planting - (flowering - planting).days * 0.5) / ((flowering - planting).days * 0.5)
            kc = crop_data['kc_initial'] + (crop_data['kc_mid'] - crop_data['kc_initial']) * progress
        elif days_since_planting < (harvest - planting).days * 0.8:
            stage = "mid_season"
            kc = crop_data['kc_mid']
        elif days_since_planting < (harvest - planting).days:
            stage = "late_season"
            # Interpolate between mid and late
            progress = (days_since_planting - (harvest - planting).days * 0.8) / ((harvest - planting).days * 0.2)
            kc = crop_data['kc_mid'] + (crop_data['kc_late'] - crop_data['kc_mid']) * progress
        else:
            stage = "harvest"
            kc = crop_data['kc_late']
        
        return {
            "stage": stage,
            "days_since_planting": days_since_planting,
            "kc_current": round(kc, 2),
            "crop_type": crop_data['crop_type'],
            "planting_date": planting.isoformat(),
            "flowering_date": flowering.isoformat(),
            "harvest_date": harvest.isoformat()
        }


# Singleton
_phenology_service: Optional[PhenologyService] = None


def get_phenology_service() -> PhenologyService:
    """Get or create phenology service"""
    global _phenology_service
    if _phenology_service is None:
        _phenology_service = PhenologyService()
    return _phenology_service
```

---

### 4a.3 Frontend Integration

**Update:** `src/services/digitalTwinEngine.ts`

```typescript
// Add phenology calculation
interface PhenologyData {
  stage: string;
  days_since_planting: number;
  kc_current: number;
  crop_type: string;
}

// Fetch phenology from backend or calculate locally
async function getPhenologyForZone(zoneId: string): Promise<PhenologyData> {
  try {
    const response = await apiClient.request(`/api/v1/phenology/${zoneId}`, 'GET');
    return response.data;
  } catch {
    // Fallback to static Kc
    return {
      stage: 'unknown',
      days_since_planting: 0,
      kc_current: 1.0,
      crop_type: 'unknown'
    };
  }
}

// Update water balance calculation to use dynamic Kc
export async function calculateWaterBalance(zone: ManagementZone) {
  const phenology = await getPhenologyForZone(zone.id);
  const kc = phenology.kc_current;
  
  // Use kc in ET calculation
  const etc = et0 * kc;
  
  // ... rest of calculation
}
```

**Update:** `src/components/FieldGISMap.tsx`

Add phenology display to zone popup:

```typescript
{selectedZone && (
  <div className="zone-info">
    <h3>{selectedZone.name}</h3>
    <p>Etapa: {selectedZone.phenology?.stage}</p>
    <p>Días desde siembra: {selectedZone.phenology?.days_since_planting}</p>
    <p>Kc actual: {selectedZone.phenology?.kc_current}</p>
  </div>
)}
```

---

## Phase 4b: Retrospective "What-If" Mode

### 4b.1 Retrospective Simulation Function

**Update:** `src/services/digitalTwinEngine.ts`

```typescript
interface RetrospectiveParams {
  zoneId: string;
  historicalDate: Date;
  alteredParams: {
    irrigation_mm?: number;
    temperature_delta?: number;
  };
}

interface RetrospectiveResult {
  simulated_moisture: number[];
  actual_moisture: number[];
  dates: string[];
  metrics: {
    mae: number;
    rmse: number;
    r_squared: number;
  };
  insights: string[];
}

export function simulateRetrospective(
  params: RetrospectiveParams,
  historicalData: SensorTelemetry[]
): RetrospectiveResult {
  const { zoneId, historicalDate, alteredParams } = params;
  
  // Filter data from historical date forward (next 7 days)
  const startDate = historicalDate.getTime();
  const endDate = startDate + 7 * 24 * 60 * 60 * 1000;
  
  const relevantData = historicalData.filter(d =>
    d.zone_id === zoneId &&
    new Date(d.timestamp).getTime() >= startDate &&
    new Date(d.timestamp).getTime() <= endDate
  );
  
  if (relevantData.length === 0) {
    throw new Error('No historical data for this period');
  }
  
  // Simulate soil moisture with altered parameters
  const simulated: number[] = [];
  const actual: number[] = [];
  const dates: string[] = [];
  
  let currentMoisture = relevantData[0].soil_moisture_percent;
  
  relevantData.forEach((data, idx) => {
    // Actual value
    actual.push(data.soil_moisture_percent);
    dates.push(data.timestamp);
    
    // Simulated value
    const et0 = data.et0_mm_day || 5.0;
    const rainfall = data.precipitation_mm || 0;
    const irrigation = idx === 0 ? (alteredParams.irrigation_mm || 0) : 0;
    
    // Simple water balance
    const etc = et0 * 1.1; // Assuming mid-season Kc
    const deltaW = rainfall + irrigation - etc;
    currentMoisture = Math.max(10, Math.min(50, currentMoisture + deltaW * 0.5));
    
    simulated.push(currentMoisture);
  });
  
  // Calculate metrics
  const mae = calculateMAE(simulated, actual);
  const rmse = calculateRMSE(simulated, actual);
  const r_squared = calculateR2(simulated, actual);
  
  // Generate insights
  const insights = generateInsights(simulated, actual, alteredParams);
  
  return {
    simulated_moisture: simulated,
    actual_moisture: actual,
    dates,
    metrics: { mae, rmse, r_squared },
    insights
  };
}

function calculateMAE(predicted: number[], actual: number[]): number {
  const sum = predicted.reduce((acc, val, idx) => acc + Math.abs(val - actual[idx]), 0);
  return sum / predicted.length;
}

function calculateRMSE(predicted: number[], actual: number[]): number {
  const sum = predicted.reduce((acc, val, idx) => acc + Math.pow(val - actual[idx], 2), 0);
  return Math.sqrt(sum / predicted.length);
}

function calculateR2(predicted: number[], actual: number[]): number {
  const meanActual = actual.reduce((a, b) => a + b, 0) / actual.length;
  const ssRes = predicted.reduce((acc, val, idx) => acc + Math.pow(actual[idx] - val, 2), 0);
  const ssTot = actual.reduce((acc, val) => acc + Math.pow(val - meanActual, 2), 0);
  return 1 - (ssRes / ssTot);
}

function generateInsights(
  simulated: number[],
  actual: number[],
  alteredParams: any
): string[] {
  const insights: string[] = [];
  
  const avgSimulated = simulated.reduce((a, b) => a + b, 0) / simulated.length;
  const avgActual = actual.reduce((a, b) => a + b, 0) / actual.length;
  
  if (alteredParams.irrigation_mm && avgSimulated < avgActual) {
    insights.push(`Reducir el riego en ${alteredParams.irrigation_mm}mm habría ahorrado agua sin causar estrés significativo`);
  } else if (alteredParams.irrigation_mm && avgSimulated > avgActual) {
    insights.push(`Aumentar el riego en ${alteredParams.irrigation_mm}mm habría mejorado la humedad del suelo`);
  }
  
  const mae = calculateMAE(simulated, actual);
  if (mae < 2.0) {
    insights.push('El modelo simula muy bien las condiciones reales (error < 2%)');
  } else if (mae > 5.0) {
    insights.push('El modelo tiene desviaciones significativas - posible lluvia no registrada o deriva del sensor');
  }
  
  return insights;
}
```

---

### 4b.2 UI Extension

**Update:** `src/components/WhatIfSimulator.tsx`

Add retrospective mode toggle:

```typescript
const [mode, setMode] = useState<'forward' | 'retrospective'>('forward');
const [historicalDate, setHistoricalDate] = useState<Date>(new Date());
const [retrospectiveResult, setRetrospectiveResult] = useState<RetrospectiveResult | null>(null);

// Add mode selector
<div className="mode-selector">
  <button onClick={() => setMode('forward')} className={mode === 'forward' ? 'active' : ''}>
    Simulación Futura
  </button>
  <button onClick={() => setMode('retrospective')} className={mode === 'retrospective' ? 'active' : ''}>
    Análisis Retrospectivo
  </button>
</div>

{mode === 'retrospective' && (
  <div className="retrospective-controls">
    <label>Fecha Histórica:</label>
    <input
      type="date"
      value={historicalDate.toISOString().split('T')[0]}
      onChange={(e) => setHistoricalDate(new Date(e.target.value))}
      max={new Date().toISOString().split('T')[0]}
    />
    
    <label>Ajuste de Riego (mm):</label>
    <input
      type="number"
      value={irrigationAdjustment}
      onChange={(e) => setIrrigationAdjustment(Number(e.target.value))}
    />
    
    <button onClick={runRetrospective}>Simular</button>
  </div>
)}

{retrospectiveResult && (
  <div className="retrospective-results">
    <h3>Resultados de Simulación Retrospectiva</h3>
    
    <div className="chart">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formatRetrospectiveData(retrospectiveResult)}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis label={{ value: 'Humedad del Suelo (%)', angle: -90 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="simulated" stroke="#8884d8" name="Simulado" />
          <Line type="monotone" dataKey="actual" stroke="#82ca9d" name="Real" />
        </LineChart>
      </ResponsiveContainer>
    </div>
    
    <div className="metrics">
      <h4>Métricas de Precisión</h4>
      <p>MAE: {retrospectiveResult.metrics.mae.toFixed(2)}%</p>
      <p>RMSE: {retrospectiveResult.metrics.rmse.toFixed(2)}%</p>
      <p>R²: {retrospectiveResult.metrics.r_squared.toFixed(3)}</p>
    </div>
    
    <div className="insights">
      <h4>Análisis</h4>
      {retrospectiveResult.insights.map((insight, idx) => (
        <p key={idx}>• {insight}</p>
      ))}
    </div>
  </div>
)}
```

---

## Phase 4c: Sensor Data Quality Scoring

### 4c.1 Quality Metrics Extension

**Update:** `src/services/anomalyDetectionEngine.ts`

```typescript
interface SensorQualityMetrics {
  sensor_id: string;
  valid_reading_percent: number;
  noise_level: number;
  days_since_calibration: number;
  quality_score: number;
  grade: 'excellent' | 'good' | 'fair' | 'poor';
}

export class QualityScoreEngine {
  private readonly CALIBRATION_INTERVAL_DAYS = 30;
  
  calculateQualityScore(
    sensorId: string,
    recentReadings: SensorTelemetry[]
  ): SensorQualityMetrics {
    // Filter last 7 days
    const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    const relevantReadings = recentReadings.filter(
      r => r.sensor_id === sensorId && new Date(r.timestamp).getTime() >= sevenDaysAgo
    );
    
    if (relevantReadings.length === 0) {
      return {
        sensor_id: sensorId,
        valid_reading_percent: 0,
        noise_level: 100,
        days_since_calibration: 999,
        quality_score: 0,
        grade: 'poor'
      };
    }
    
    // 1. Valid reading percentage
    const validReadings = relevantReadings.filter(r =>
      r.soil_moisture_percent >= 0 &&
      r.soil_moisture_percent <= 100 &&
      r.soil_moisture_percent !== null
    );
    const validPercent = (validReadings.length / relevantReadings.length) * 100;
    
    // 2. Noise level (standard deviation)
    const values = validReadings.map(r => r.soil_moisture_percent);
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    
    // Expected variance is ~2-3% for stable soil
    const noiseLevel = Math.min(100, (stdDev / 3.0) * 100);
    
    // 3. Days since calibration (simulated)
    const lastCalibration = this.getLastCalibrationDate(sensorId);
    const daysSinceCalibration = Math.floor(
      (Date.now() - lastCalibration.getTime()) / (24 * 60 * 60 * 1000)
    );
    
    // Calculate weighted score
    const validScore = validPercent * 0.4;
    const noiseScore = (100 - noiseLevel) * 0.3;
    const calibrationScore = Math.max(0, 100 - (daysSinceCalibration / this.CALIBRATION_INTERVAL_DAYS) * 100) * 0.3;
    
    const qualityScore = Math.round(validScore + noiseScore + calibrationScore);
    
    // Determine grade
    let grade: 'excellent' | 'good' | 'fair' | 'poor';
    if (qualityScore >= 90) grade = 'excellent';
    else if (qualityScore >= 80) grade = 'good';
    else if (qualityScore >= 60) grade = 'fair';
    else grade = 'poor';
    
    return {
      sensor_id: sensorId,
      valid_reading_percent: Math.round(validPercent),
      noise_level: Math.round(noiseLevel),
      days_since_calibration: daysSinceCalibration,
      quality_score: qualityScore,
      grade
    };
  }
  
  private getLastCalibrationDate(sensorId: string): Date {
    // Mock implementation - in production, fetch from database
    const stored = localStorage.getItem(`calibration_${sensorId}`);
    if (stored) {
      return new Date(stored);
    }
    // Default: 15 days ago
    return new Date(Date.now() - 15 * 24 * 60 * 60 * 1000);
  }
  
  getAllSensorScores(allReadings: SensorTelemetry[]): SensorQualityMetrics[] {
    const uniqueSensors = [...new Set(allReadings.map(r => r.sensor_id))];
    return uniqueSensors.map(sensorId => 
      this.calculateQualityScore(sensorId, allReadings)
    );
  }
}

export const qualityScoreEngine = new QualityScoreEngine();
```

---

### 4c.2 UI Display

**Update:** `src/components/TelemetryAnalytics.tsx`

```typescript
import { qualityScoreEngine } from '../services/anomalyDetectionEngine';

// Inside component
const [qualityScores, setQualityScores] = useState<SensorQualityMetrics[]>([]);

useEffect(() => {
  const scores = qualityScoreEngine.getAllSensorScores(sensors);
  setQualityScores(scores);
}, [sensors]);

// Add new section
<div className="sensor-quality-section">
  <h3>Calidad de Datos de Sensores</h3>
  
  <div className="quality-grid">
    {qualityScores.map(score => (
      <div key={score.sensor_id} className={`quality-card grade-${score.grade}`}>
        <div className="sensor-id">{score.sensor_id}</div>
        
        <div className="score-circle">
          <div className="score-value">{score.quality_score}</div>
          <div className="score-label">Puntaje</div>
        </div>
        
        <div className="metrics-detail">
          <div className="metric">
            <span className="label">Lecturas válidas:</span>
            <span className="value">{score.valid_reading_percent}%</span>
          </div>
          <div className="metric">
            <span className="label">Nivel de ruido:</span>
            <span className="value">{score.noise_level}%</span>
          </div>
          <div className="metric">
            <span className="label">Días desde calibración:</span>
            <span className="value">{score.days_since_calibration}</span>
          </div>
        </div>
        
        {score.quality_score < 60 && (
          <div className="alert">
            ⚠️ Considere recalibrar o revisar conexión
          </div>
        )}
      </div>
    ))}
  </div>
</div>
```

**Add CSS:**

```css
.quality-card {
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin: 8px;
}

.quality-card.grade-excellent {
  border-color: #10b981;
  background: #f0fdf4;
}

.quality-card.grade-good {
  border-color: #3b82f6;
  background: #eff6ff;
}

.quality-card.grade-fair {
  border-color: #f59e0b;
  background: #fffbeb;
}

.quality-card.grade-poor {
  border-color: #ef4444;
  background: #fef2f2;
}

.score-circle {
  text-align: center;
  margin: 16px 0;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
}

.metrics-detail {
  font-size: 14px;
  margin-top: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
```

---

## Data Flow Diagrams

### RAG Query Flow (Phase 1)

```
User Question (Frontend)
        ↓
    [POST /api/v1/chat]
        ↓
    RAG Service
        ↓
    1. Embed question (multilingual)
        ↓
    2. Query FAISS (top 4 docs)
        ↓
    3. Build prompt with context
        ↓
    4. Call Groq LLM
        ↓
    5. Return answer + sources
        ↓
    Frontend displays with citations
```

### Alert Processing Flow (Phase 3)

```
Sensor Event
        ↓
    [POST /api/v1/process-alert]
        ↓
    Notification Service
        ↓
    1. Classify urgency (LLM)
        ↓
    2. Generate role-specific messages (LLM)
        ↓
    3. Determine channels based on urgency
        ↓
    4. Rate limit check
        ↓
    5. Dispatch to channels
        ↓
    Return result
```

---

## API Endpoint Summary

### New Endpoints

| Endpoint | Method | Purpose | Phase |
|----------|--------|---------|-------|
| `/api/v1/chat` | POST | RAG-powered chat | 1 |
| `/api/v1/chat/health` | GET | RAG health check | 1 |
| `/api/v1/process-alert` | POST | Process sensor alert | 3 |
| `/api/v1/alerts/health` | GET | Notification service health | 3 |
| `/api/v1/phenology/{zone_id}` | GET | Get phenological stage | 4a |

---

## Deployment Considerations

### Environment Variables

**Add to `backend/.env`:**

```env
# Groq API
GROQ_API_KEY=gsk_...

# Knowledge Base
KNOWLEDGE_BASE_PATH=backend/data/knowledge_base

# Embeddings
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# LangFlow
LANGFLOW_PORT=7860

# Notifications (mock in dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@vri.com
SMTP_PASS=...

SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

### Docker Compose Update

**Update:** `docker-compose.yml`

```yaml
services:
  backend:
    # ... existing config
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - KNOWLEDGE_BASE_PATH=/app/data/knowledge_base
    volumes:
      - ./backend/data:/app/data
  
  streamlit:
    build:
      context: ./backend
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_HOST=backend
      - API_PORT=8000
    depends_on:
      - backend
    command: streamlit run streamlit_backend.py --server.port=8501
  
  langflow:
    image: langflowai/langflow:latest
    ports:
      - "7860:7860"
    environment:
      - LANGFLOW_DATABASE_URL=sqlite:///langflow.db
    volumes:
      - ./backend/data/langflow:/app/langflow
```

**Note:** The existing `streamlit_backend.py` provides a manual testing UI for FastAPI endpoints (port 8501). This is separate from the main React frontend.

---

## Testing Strategy

### Phase 1 Testing

**Create:** `backend/tests/test_rag_service.py`

```python
import pytest
from app.services.rag_service import RAGService

def test_rag_initialization():
    service = RAGService()
    service.initialize()
    assert service._initialized == True

def test_rag_query():
    service = RAGService()
    service.initialize()
    
    result = service.query("¿Cuál es el Kc del maíz en floración?", language="es")
    
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) > 0

# 5 test questions
TEST_QUESTIONS = [
    "¿Cuánta agua necesita el maíz durante la floración?",
    "¿Qué tipos de suelo son mejores para riego por aspersión?",
    "¿Cuáles son las normativas de riego en Perú?",
    "¿Cuál es el mejor momento del día para regar?",
    "¿Cómo prevenir enfermedades con manejo de riego?"
]

@pytest.mark.parametrize("question", TEST_QUESTIONS)
def test_rag_questions(question):
    service = RAGService()
    service.initialize()
    
    result = service.query(question, language="es")
    
    assert len(result["answer"]) > 50
    assert result["num_sources"] >= 1
```

### Phase 3 Testing

**Create:** `backend/tests/test_notification_service.py`

```python
import pytest
from app.services.notification_service import NotificationService, UrgencyLevel

def test_urgency_classification():
    service = NotificationService()
    
    critical_event = {
        "sensor_id": "S001",
        "zone_id": "Z001",
        "value": 10.0,
        "expected_range": [25, 40],
        "metric": "soil_moisture_percent",
        "crop_stage": "flowering",
        "timestamp": "2026-09-24T14:00:00Z"
    }
    
    result = service.classify_urgency(critical_event)
    
    assert result["urgency"] == UrgencyLevel.CRITICAL
    assert result["confidence"] > 70

def test_message_generation():
    service = NotificationService()
    
    event = {...}
    message = service.generate_message(event, UserRole.PRODUCER, UrgencyLevel.CRITICAL)
    
    assert len(message) > 10
    assert len(message) < 300  # Max 3 lines ~100 chars each
```

---

## Performance Requirements

| Component | Requirement | Target |
|-----------|-------------|--------|
| RAG Query | Response time | < 5s |
| RAG Init | Startup time | < 30s |
| Alert Classification | Processing time | < 3s |
| Message Generation | Time per role | < 2s |
| Quality Score Calc | Update frequency | Every 1 hour |
| Phenology Calc | Update frequency | Daily |
| Retrospective Sim | Computation time | < 10s for 7 days |

---

## Security Considerations

1. **API Key Storage:**
   - Never commit API keys to git
   - Use environment variables
   - Frontend stores in localStorage (encrypted if possible)

2. **Rate Limiting:**
   - Critical alerts: max 5 per hour per user
   - Chat endpoint: max 20 requests per minute per IP
   - Use Redis for distributed rate limiting in production

3. **Input Validation:**
   - Sanitize all user inputs
   - Validate date ranges for retrospective analysis
   - Limit message lengths

4. **Error Handling:**
   - Don't expose API keys in error messages
   - Log errors internally, return generic messages to users
   - Graceful degradation when LLM APIs are unavailable

---

## Success Metrics

### Phase 1 Success Metrics
- RAG service initializes without errors
- 5/5 test questions return relevant answers
- Average source citation count: 2-4 per answer
- Response time: < 5 seconds

### Phase 2 Success Metrics
- All 3 LangFlow workflows designed and exported
- Screenshots captured for demo
- Code exports are syntactically valid Python

### Phase 3 Success Metrics
- Urgency classification accuracy: > 80% (manual validation)
- Message generation time: < 3s total for 3 roles
- 3/3 test events processed successfully

### Phase 4 Success Metrics
- 4a: Kc values update dynamically for all zones
- 4b: Retrospective simulation completes in < 10s
- 4c: Quality scores calculated for all sensors

---

## Implementation Priority

**Week 1 (Critical Path):**
- Day 1-2: Phase 1 (LangChain RAG)
- Day 3: Phase 2 (LangFlow workflows)
- Day 4: Phase 3 (Intelligent notifications)

**Week 2 (If time allows):**
- Day 5: Phase 4a (Crop calendar - quick win)
- Day 6: Phase 4c (Quality scores - medium complexity)
- Day 7: Phase 4b (Retrospective - most complex)

**Final Day:**
- Integration testing
- Documentation updates
- Demo preparation

---

## Conclusion

This design provides a complete technical blueprint for implementing the VRI Master Plan. Each phase is modular and can function independently, with clear interfaces between components. The design prioritizes P0 features (Phases 1-3) while providing detailed guidance for optional P1 features (Phase 4).

The architecture maintains compatibility with existing systems while adding powerful new capabilities through LangChain, LangFlow, and intelligent LLM-based processing.
