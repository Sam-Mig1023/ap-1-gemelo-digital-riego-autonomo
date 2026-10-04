# Tasks: VRI Digital Twin - Master Plan Implementation

## Overview

This task list implements the complete master plan for the VRI Digital Twin system in prioritized order. Tasks are organized by phase with clear dependencies.

**Current Repository State:**
- ✅ Frontend: React 19 + TypeScript with LanguageContext (bilingual)
- ✅ Backend: FastAPI + Streamlit Technical Console (667 lines, 6 modules)
- ✅ Knowledge base: 8 .md files created
- ✅ Public dataset: Available in parent folder (Italy 2025, 5 sectors, 789 events)

---

## PHASE 1: LangChain RAG (Critical - P0)

### Task 1.1: Enhance Knowledge Base with Public Dataset
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** None

Integrate the public soil moisture dataset into the knowledge base structure.

**Subtasks:**
1. Create `backend/data/datasets/` directory
2. Copy relevant CSV files from public dataset location:
   - `dataset_zone_1_preprocessed.csv` (tomato, open field)
   - `dataset_zone_2_preprocessed.csv` (tomato, open field)  
   - `dataset_zone_4_preprocessed.csv` (zucchini)
   - `dataset_zone_5_preprocessed.csv` (blueberry)
3. Create `backend/data/knowledge_base/09_real_world_dataset.md` with:
   - Dataset overview and citation (CC BY 4.0)
   - Per-sector statistics (crop type, rows, date range)
   - Key findings (irrigation patterns, soil moisture ranges)
   - References to CSV files for RAG retrieval
4. Verify all 8 existing .md files are properly formatted for RAG ingestion

**Acceptance Criteria:**
- [ ] Dataset files copied to `backend/data/datasets/`
- [ ] Summary document created with proper metadata
- [ ] Knowledge base has 9 total .md files
- [ ] Files use consistent bilingual format (Spanish/English)

---

### Task 1.2: Install LangChain Dependencies
**Priority:** P0  
**Estimated Time:** 30 minutes  
**Dependencies:** Task 1.1

Install all required dependencies for RAG system.

**Subtasks:**
1. Update `backend/requirements.txt` with:
   ```
   langchain==0.1.16
   langchain-groq==0.0.3
   langchain-community==0.0.34
   chromadb==0.4.24
   faiss-cpu==1.8.0
   sentence-transformers==2.6.1
   ```
2. Create virtual environment if needed
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Verify imports work in Python REPL

**Acceptance Criteria:**
- [ ] All packages install without errors
- [ ] No dependency conflicts with existing packages
- [ ] Can import: `from langchain_groq import ChatGroq`
- [ ] Can import: `from langchain_community.vectorstores import FAISS`

---

### Task 1.3: Implement RAG Service
**Priority:** P0  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.2

Create the core RAG service with LangChain + FAISS + Groq.

**Subtasks:**
1. Create `backend/app/services/rag_service.py` with:
   - `RAGService` class with initialization method
   - Document loader for knowledge base .md files
   - Text chunking (1000 chars, 200 overlap)
   - Multilingual embeddings (`paraphrase-multilingual-mpnet-base-v2`)
   - FAISS vector store creation
   - Groq LLM integration (`llama-3.3-70b-versatile`)
   - Custom agronomic prompt template
   - Query method returning answer + sources
   - Health check method
   - Singleton pattern with `get_rag_service()`

2. Handle environment variables:
   - `GROQ_API_KEY` from `.env`
   - `KNOWLEDGE_BASE_PATH` with default

3. Error handling for:
   - Missing API key
   - Empty knowledge base
   - Failed LLM queries

**Acceptance Criteria:**
- [ ] RAG service initializes without errors
- [ ] Loads all 9 .md files from knowledge base
- [ ] Creates FAISS index successfully
- [ ] Can query with Spanish and English questions
- [ ] Returns structured response with answer + sources
- [ ] Handles missing GROQ_API_KEY gracefully

---

### Task 1.4: Create Chat API Endpoint
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1.3

Implement FastAPI endpoint for RAG-powered chat.

**Subtasks:**
1. Create `backend/app/api/v1/endpoints/chat.py` with:
   - `POST /chat` endpoint
   - Request model: `ChatRequest(question: str, language: str)`
   - Response model: `ChatResponse(answer: str, sources: List, model: str, num_sources: int)`
   - Integration with `get_rag_service()`
   - Error handling (500 for service failures)
   - `GET /chat/health` for health checks

2. Update `backend/app/api/v1/__init__.py`:
   - Import chat router
   - Include with tag "Chat & RAG"

3. Add to `backend/.env.example`:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   KNOWLEDGE_BASE_PATH=backend/data/knowledge_base
   ```

**Acceptance Criteria:**
- [ ] Endpoint documented in FastAPI `/docs`
- [ ] POST /api/v1/chat accepts JSON and returns structured response
- [ ] GET /api/v1/chat/health returns service status
- [ ] Proper HTTP status codes (200, 500, 503)
- [ ] Sources are included in response

---

### Task 1.5: Integrate RAG in Frontend Chatbot
**Priority:** P0  
**Estimated Time:** 3 hours  
**Dependencies:** Task 1.4

Update the existing AgronomicChatbot to use RAG backend with fallback.

**Subtasks:**
1. Update `src/services/apiClient.ts`:
   - Add `chat(question: string, language: string)` method
   - Add `getChatHealth()` method

2. Update `src/types/index.ts` (or create interface):
   - Add `sources?: Array<{content: string, metadata: object}>` to ChatMessage type

3. Update `src/components/AgronomicChatbot.tsx`:
   - Create `queryWithRAG()` function that tries RAG backend first
   - Fallback to existing direct Groq call if RAG unavailable
   - Update `handleSendMessage` to use `queryWithRAG`
   - Display sources below answer when available
   - Style sources section with citations
   - Keep all existing functionality (voice, model selection, language switching)

**Acceptance Criteria:**
- [ ] Chatbot tries RAG backend first
- [ ] Falls back to direct Groq if backend unavailable
- [ ] Sources displayed with proper formatting
- [ ] No breaking changes to existing chatbot features
- [ ] Works in both Spanish and English
- [ ] Loading states updated appropriately

---

### Task 1.6: RAG System Testing
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1.5

Verify RAG system with comprehensive test scenarios.

**Subtasks:**
1. Create `backend/tests/test_rag_service.py`:
   - Test RAG initialization
   - Test query functionality
   - Parametrized test with 5 test questions

2. Define 5 test questions (Spanish):
   - "¿Cuánta agua necesita el maíz durante la floración?"
   - "¿Qué tipos de suelo son mejores para riego por aspersión?"
   - "¿Cuáles son las normativas de riego en zonas áridas?"
   - "¿Cuál es el mejor momento del día para regar cultivos?"
   - "Según el dataset público, ¿cuántos eventos de riego hubo en la zona 1?"

3. Manual testing via `/docs`:
   - Test each question
   - Verify sources are correct
   - Check response quality
   - Test in both languages

4. Document test results in `backend/docs/rag_test_results.md`

**Acceptance Criteria:**
- [ ] All 5 test questions return relevant answers
- [ ] Each answer includes at least 1 source citation
- [ ] Sources reference correct knowledge base files
- [ ] Response time < 5 seconds per query
- [ ] Works in both Spanish and English
- [ ] Test results documented

---

## PHASE 2: LangFlow Visual Workflows (Critical - P0)

### Task 2.1: Install and Configure LangFlow
**Priority:** P0  
**Estimated Time:** 1 hour  
**Dependencies:** Task 1.6

Set up LangFlow for visual workflow design.

**Subtasks:**
1. Add to `backend/requirements.txt`: `langflow==1.0.0`
2. Install: `pip install langflow`
3. Test launch: `langflow run --host 0.0.0.0 --port 7860`
4. Verify web interface accessible at http://localhost:7860
5. Create `backend/docs/langflow_screenshots/` directory
6. Update `backend/.env.example`:
   ```
   LANGFLOW_PORT=7860
   LANGFLOW_HOST=0.0.0.0
   ```

**Acceptance Criteria:**
- [ ] LangFlow installs without conflicts
- [ ] Web interface loads successfully
- [ ] Port 7860 does not conflict with FastAPI (8000) or Streamlit (8501)
- [ ] Can create and save flows

---

### Task 2.2: Design LangFlow Flow 1 - RAG Chatbot
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task 2.1

Create visual representation of the RAG pipeline.

**Subtasks:**
1. In LangFlow UI, create new flow named "VRI_RAG_Chatbot"
2. Add components:
   - Text Input: "user_question"
   - FAISS Retriever (path: `backend/data/faiss_index/`, embedding: multilingual, top_k: 4)
   - Groq LLM (model: llama-3.3-70b-versatile, temp: 0.3, max_tokens: 1024)
   - System Prompt component (agronomic context)
   - Text Output: answer + sources

3. Connect components in flow
4. Test with sample question
5. Export as Python code to `backend/app/services/langflow_pipelines/chatbot_rag.py`
6. Capture screenshot and save as `backend/docs/langflow_screenshots/flow1_chatbot_rag.png`

**Acceptance Criteria:**
- [ ] Flow designed and tested in LangFlow
- [ ] Produces correct output for sample question
- [ ] Python code exported successfully
- [ ] Screenshot captured with clear component labels
- [ ] Flow mirrors implementation from Phase 1

---

### Task 2.3: Design LangFlow Flow 2 - Intelligent Alerts
**Priority:** P0  
**Estimated Time:** 3 hours  
**Dependencies:** Task 2.1

Create visual workflow for smart alert processing.

**Subtasks:**
1. Create new flow named "VRI_Intelligent_Alerts"
2. Add components:
   - JSON Input: sensor event data
   - Python Function: `detect_anomaly()` (checks value vs expected range)
   - Groq LLM: urgency classifier (prompt: classify as CRITICAL/MODERATE/INFO)
   - Groq LLM: message generator (3 roles: agronomist/producer/technician)
   - Python Function: `dispatch()` (routes to channels based on urgency)
   - JSON Output: result with urgency + messages + channels

3. Configure logic:
   - Critical: value < range_low * 0.7
   - Moderate: value outside range
   - Info: within range

4. Test with sample critical event
5. Export to `backend/app/services/langflow_pipelines/intelligent_alerts.py`
6. Screenshot: `backend/docs/langflow_screenshots/flow2_intelligent_alerts.png`

**Acceptance Criteria:**
- [ ] Flow processes sensor events correctly
- [ ] Urgency classification works as expected
- [ ] Generates role-specific messages
- [ ] Python code exported
- [ ] Screenshot captured

---

### Task 2.4: Design LangFlow Flow 3 - RL Explainability
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task 2.1

Create visual workflow for explainable RL decisions.

**Subtasks:**
1. Create new flow named "VRI_RL_Explainability"
2. Add components:
   - JSON Input: zone state (soil_moisture, temperature, et0, crop_stage, etc.)
   - Python Function: `rl_decision()` (simplified RL logic)
   - Python Function: `explain_decision()` (mock SHAP values)
   - Groq LLM: explanation validator (converts SHAP to human-readable)
   - Conditional: approval gate (auto-approve if depth < 10mm, else require human)
   - JSON Output: decision + explanation + approval_required

3. Test with sample zone state
4. Export to `backend/app/services/langflow_pipelines/rl_explainability.py`
5. Screenshot: `backend/docs/langflow_screenshots/flow3_rl_explainability.png`

**Acceptance Criteria:**
- [ ] Flow demonstrates explainability pipeline
- [ ] SHAP values generated (mock)
- [ ] LLM provides human-readable explanation
- [ ] Approval gate logic works
- [ ] Python code exported
- [ ] Screenshot captured

---

### Task 2.5: Document LangFlow Workflows
**Priority:** P0  
**Estimated Time:** 1 hour  
**Dependencies:** Tasks 2.2, 2.3, 2.4

Create comprehensive documentation for all LangFlow workflows.

**Subtasks:**
1. Create `backend/app/services/langflow_pipelines/README.md` with:
   - Overview of each flow
   - Purpose and use case
   - Components and configuration
   - Screenshot references
   - Running instructions
   - Integration notes

2. Verify all files present:
   - [ ] chatbot_rag.py
   - [ ] intelligent_alerts.py
   - [ ] rl_explainability.py
   - [ ] README.md
   - [ ] 3 screenshot PNG files

**Acceptance Criteria:**
- [ ] README explains all 3 flows clearly
- [ ] Screenshots linked in documentation
- [ ] Running instructions for LangFlow provided
- [ ] Integration guidance for using exported Python code

---

## PHASE 3: Intelligent Notification System (Critical - P0)

### Task 3.1: Implement Notification Service
**Priority:** P0  
**Estimated Time:** 4 hours  
**Dependencies:** Task 1.2 (LangChain deps)

Create notification service with LLM-based classification.

**Subtasks:**
1. Create `backend/app/services/notification_service.py` with:
   - `NotificationService` class
   - `UrgencyLevel` enum (CRITICAL, MODERATE, INFO)
   - `UserRole` enum (agronomist, producer, technician)
   - `classify_urgency(event: dict) -> dict` method:
     * Uses Groq LLM to classify urgency
     * Considers: deviation, crop stage, time of day
     * Returns: urgency level + confidence score
   - `generate_message(event: dict, role: UserRole, urgency: UrgencyLevel) -> str`:
     * Role-specific message generation
     * Max 3 lines (agronomist), 2 lines (producer/technician)
     * Uses LLM for personalization
   - `dispatch(urgency, messages, recipients, test_mode) -> dict`:
     * Routes to channels based on urgency
     * CRITICAL → email + SMS
     * MODERATE → push notification
     * INFO → dashboard only
     * Rate limiting (max 5 critical/hour)
   - `get_notification_service()` singleton

2. Mock implementations:
   - `_send_notification()` prints to console
   - In-memory rate limiting tracker

**Acceptance Criteria:**
- [ ] Service classifies events correctly (tested manually)
- [ ] Messages generated for all 3 roles
- [ ] Message lengths within limits
- [ ] Rate limiting works
- [ ] Test mode skips actual sending
- [ ] Works in Spanish by default

---

### Task 3.2: Create Process Alert Endpoint
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task 3.1

Implement FastAPI endpoint for alert processing.

**Subtasks:**
1. Create `backend/app/api/v1/endpoints/alerts.py` with:
   - `POST /process-alert` endpoint
   - Request model: `ProcessAlertRequest(event: SensorEvent, recipients: dict, test_mode: bool)`
   - Response model: `ProcessAlertResponse(urgency: str, confidence: int, messages: dict, channels: list, dispatch_result: dict)`
   - Orchestrates: classification → message generation → dispatch
   - Error handling

2. Add health check: `GET /alerts/health`

3. Update `backend/app/api/v1/__init__.py`:
   - Import alerts router
   - Include with tag "Alerts & Notifications"

**Acceptance Criteria:**
- [ ] Endpoint documented in `/docs`
- [ ] Accepts sensor event JSON
- [ ] Returns urgency + role-specific messages
- [ ] Channels determined by urgency
- [ ] Test mode works (no actual sending)
- [ ] Proper error handling

---

### Task 3.3: Test Notification System
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task 3.2

Verify notification system with test scenarios.

**Subtasks:**
1. Create `backend/tests/test_notification_service.py`:
   - Test urgency classification
   - Test message generation (all roles)
   - Test dispatcher channel selection
   - Test rate limiting

2. Define 3 test events:
   - **Event 1 (CRITICAL):** Low soil moisture (10%) during flowering, expected 25-40%
   - **Event 2 (MODERATE):** Temperature spike (35°C), normal range 20-30°C
   - **Event 3 (INFO):** Normal reading within range

3. Manual testing via `/docs`:
   - Send all 3 events
   - Verify urgency classification matches expectations
   - Check message quality and length
   - Verify channels assigned correctly

4. Document results in `backend/docs/notification_test_results.md`

**Acceptance Criteria:**
- [ ] Event 1 classified as CRITICAL with confidence > 70%
- [ ] Event 2 classified as MODERATE
- [ ] Event 3 classified as INFO
- [ ] Messages appropriate for each role
- [ ] Channels: critical → [email, sms], moderate → [push], info → [dashboard]
- [ ] Test results documented

---

## PHASE 4a: Crop Calendar & Phenological Stage (Optional - P1)

### Task 4a.1: Create Crop Calendar Data
**Priority:** P1  
**Estimated Time:** 1 hour  
**Dependencies:** None

Create structured crop calendar for all zones.

**Subtasks:**
1. Create `backend/data/crop_calendar.csv` with columns:
   - zone_id, crop_type, planting_date, flowering_date_expected, harvest_date
   - kc_initial, kc_mid, kc_late

2. Populate with data for zones from mockData.ts:
   - zone-1-nw: maize, 2026-03-15 planting
   - zone-2-ne: wheat, 2026-04-01 planting
   - zone-3-sw: potato, 2026-03-20 planting
   - zone-4-se: maize, 2026-03-10 planting

3. Use realistic Kc values per crop from FAO-56

**Acceptance Criteria:**
- [ ] CSV file created with 4+ zone entries
- [ ] All required columns present
- [ ] Dates are realistic for crop cycles
- [ ] Kc values match FAO-56 standards
- [ ] File is parseable by pandas

---

### Task 4a.2: Implement Phenology Service
**Priority:** P1  
**Estimated Time:** 2 hours  
**Dependencies:** Task 4a.1

Create service to calculate phenological stages.

**Subtasks:**
1. Create `backend/app/services/phenology_service.py` with:
   - `PhenologyService` class
   - `_load_calendar()` reads CSV
   - `get_stage(zone_id: str, current_date: date) -> dict`:
     * Calculates stage based on days since planting
     * Stages: not_planted, initial, development, mid_season, late_season, harvest
     * Interpolates Kc between stages
     * Returns: stage, days_since_planting, kc_current, crop_type, dates
   - `get_phenology_service()` singleton

2. Stage logic:
   - Initial: 0-50% of time to flowering
   - Development: 50-100% of time to flowering
   - Mid-season: flowering to 80% of time to harvest
   - Late-season: last 20% before harvest

**Acceptance Criteria:**
- [ ] Service loads calendar correctly
- [ ] Calculates stage for all zones
- [ ] Kc interpolates smoothly between stages
- [ ] Returns structured response with all fields
- [ ] Handles missing zones gracefully

---

### Task 4a.3: Add Phenology API Endpoint
**Priority:** P1  
**Estimated Time:** 1 hour  
**Dependencies:** Task 4a.2

Expose phenology data via API.

**Subtasks:**
1. Create `backend/app/api/v1/endpoints/phenology.py`:
   - `GET /phenology/{zone_id}` endpoint
   - Optional query param: `date` (defaults to today)
   - Returns phenology data from service

2. Update API router

**Acceptance Criteria:**
- [ ] Endpoint in `/docs`
- [ ] Returns phenology for valid zone_id
- [ ] 404 for invalid zone_id
- [ ] Date parameter works

---

### Task 4a.4: Integrate Dynamic Kc in Frontend
**Priority:** P1  
**Estimated Time:** 2 hours  
**Dependencies:** Task 4a.3

Update digital twin engine to use dynamic Kc values.

**Subtasks:**
1. Update `src/services/digitalTwinEngine.ts`:
   - Add `getPhenologyForZone(zoneId)` function (calls API)
   - Update `calculateWaterBalance()` to use dynamic Kc
   - Replace any hardcoded Kc values

2. Update `src/components/FieldGISMap.tsx`:
   - Display phenological stage in zone popup
   - Show: stage name, days since planting, current Kc

**Acceptance Criteria:**
- [ ] Water balance uses dynamic Kc from phenology service
- [ ] Falls back to static Kc if API unavailable
- [ ] UI displays phenological stage
- [ ] Works for all zones

---

## PHASE 4b: Retrospective "What-If" Mode (Optional - P1)

### Task 4b.1: Implement Retrospective Simulation Engine
**Priority:** P1  
**Estimated Time:** 3 hours  
**Dependencies:** None

Create simulation function for historical scenarios.

**Subtasks:**
1. Update `src/services/digitalTwinEngine.ts`:
   - Add `simulateRetrospective(params, historicalData)` function
   - Params: zoneId, historicalDate, alteredParams (irrigation_mm, temp_delta)
   - Recalculates soil moisture from historical date forward (7 days)
   - Uses actual weather from mockData
   - Returns: simulated_moisture[], actual_moisture[], dates[], metrics, insights

2. Implement metrics:
   - `calculateMAE()` - Mean Absolute Error
   - `calculateRMSE()` - Root Mean Squared Error
   - `calculateR2()` - R-squared

3. Generate insights:
   - Compare simulated vs actual average
   - Suggest water savings if applicable
   - Comment on model accuracy

**Acceptance Criteria:**
- [ ] Function simulates 7 days forward from historical date
- [ ] Uses real weather data from mockData
- [ ] Calculates all 3 metrics correctly
- [ ] Generates 2-3 actionable insights
- [ ] Handles missing data gracefully

---

### Task 4b.2: Extend What-If Simulator UI
**Priority:** P1  
**Estimated Time:** 3 hours  
**Dependencies:** Task 4b.1

Add retrospective mode to existing simulator.

**Subtasks:**
1. Update `src/components/WhatIfSimulator.tsx`:
   - Add mode selector: "forward" vs "retrospective"
   - Retrospective controls:
     * Date picker (historical dates only)
     * Irrigation adjustment slider (+/- mm)
     * Temperature adjustment slider (+/- °C)
   - Run simulation button
   - Results display:
     * Line chart (simulated vs actual soil moisture)
     * Metrics table (MAE, RMSE, R²)
     * Insights list

2. Chart using Recharts:
   - X-axis: dates
   - Y-axis: soil moisture %
   - Two lines: simulated (blue) and actual (green)

**Acceptance Criteria:**
- [ ] Mode toggle works
- [ ] Historical date picker limited to past dates
- [ ] Simulation runs on button click
- [ ] Chart displays both series clearly
- [ ] Metrics displayed with 2 decimal places
- [ ] Insights shown as bullet points
- [ ] Responsive design

---

## PHASE 4c: Sensor Data Quality Scoring (Optional - P1)

### Task 4c.1: Extend Anomaly Detection for Quality Metrics
**Priority:** P1  
**Estimated Time:** 2 hours  
**Dependencies:** None

Add quality metric tracking to anomaly detection engine.

**Subtasks:**
1. Update `src/services/anomalyDetectionEngine.ts`:
   - Add `QualityScoreEngine` class
   - `calculateQualityScore(sensorId, recentReadings)` method:
     * Filters last 7 days of readings
     * Calculates valid_reading_percent (non-null, in range)
     * Calculates noise_level (standard deviation / expected)
     * Gets days_since_calibration (from localStorage mock)
     * Computes weighted score (0-100):
       - Valid readings: 40%
       - Noise level: 30%
       - Calibration recency: 30%
     * Assigns grade: excellent (90+), good (80-89), fair (60-79), poor (<60)
   - `getAllSensorScores(allReadings)` for all sensors
   - Mock calibration dates in localStorage

**Acceptance Criteria:**
- [ ] Quality score calculated for each sensor
- [ ] Score formula weighted correctly
- [ ] Grades assigned properly
- [ ] Works with mockData sensors
- [ ] Handles missing data

---

### Task 4c.2: Add Quality Scores UI to Telemetry
**Priority:** P1  
**Estimated Time:** 2 hours  
**Dependencies:** Task 4c.1

Display sensor quality scores in TelemetryAnalytics component.

**Subtasks:**
1. Update `src/components/TelemetryAnalytics.tsx`:
   - Import `qualityScoreEngine`
   - Calculate scores on mount and sensor update
   - Add "Sensor Quality" section:
     * Grid of quality cards (one per sensor)
     * Each card shows:
       - Sensor ID
       - Quality score (large number)
       - Grade (excellent/good/fair/poor)
       - Metrics breakdown (valid %, noise %, days since calib)
       - Alert for poor scores (<60)
     * Color-coded by grade:
       - Excellent: green
       - Good: blue
       - Fair: yellow/orange
       - Poor: red

2. Add CSS styling for quality cards

**Acceptance Criteria:**
- [ ] Quality scores visible for all sensors
- [ ] Cards color-coded correctly
- [ ] Metrics breakdown displayed
- [ ] Alert shown for poor sensors
- [ ] Responsive grid layout
- [ ] Updates when sensor data changes

---

## FINAL TASKS

### Task F.1: Update Documentation
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** All previous tasks

Update project documentation with new features.

**Subtasks:**
1. Update `README.md`:
   - Add LangChain RAG section
   - Mention LangFlow workflows
   - Add intelligent notifications
   - List Phase 4 features (if implemented)
   - Update setup instructions

2. Update `backend/README.md`:
   - Document new endpoints
   - Add environment variables
   - Explain RAG initialization
   - LangFlow setup instructions

3. Create `CHANGELOG.md` documenting all changes

**Acceptance Criteria:**
- [ ] README mentions all new features
- [ ] Setup instructions updated
- [ ] Environment variables documented
- [ ] API endpoints listed
- [ ] CHANGELOG created

---

### Task F.2: Integration Testing
**Priority:** P0  
**Estimated Time:** 3 hours  
**Dependencies:** Task F.1

End-to-end testing of all systems.

**Subtasks:**
1. Backend testing:
   - Start FastAPI server: `uvicorn app.main:app --reload`
   - Verify `/docs` shows all new endpoints
   - Test RAG chat endpoint (5 questions)
   - Test alert processing (3 events)
   - Check health endpoints

2. Frontend testing:
   - Start dev server: `npm run dev`
   - Test chatbot with RAG backend
   - Verify sources displayed
   - Test fallback when backend down
   - Check language switching
   - Test Phase 4 features (if implemented)

3. Streamlit testing:
   - Start Streamlit: `streamlit run backend/streamlit_backend.py`
   - Verify all 6 modules load
   - Test API connectivity

4. Document any issues found

**Acceptance Criteria:**
- [ ] Backend starts without errors
- [ ] All endpoints return 200 (with valid auth)
- [ ] Frontend connects to backend
- [ ] Chatbot works end-to-end
- [ ] Streamlit console operational
- [ ] No console errors
- [ ] Performance acceptable (<5s RAG queries)

---

### Task F.3: Demo Preparation
**Priority:** P0  
**Estimated Time:** 2 hours  
**Dependencies:** Task F.2

Prepare system for Ticona demo.

**Subtasks:**
1. Prepare demo script:
   - LangChain RAG demonstration (5 test questions)
   - LangFlow workflows showcase (3 flows + screenshots)
   - Intelligent notifications demo (3 test events)
   - Phase 4 features (if completed)

2. Create demo data:
   - Sample sensor events ready to process
   - Test questions prepared
   - Screenshots organized

3. Verify checklist:
   - [ ] Backend and frontend running
   - [ ] .env files configured
   - [ ] Knowledge base loaded
   - [ ] Public dataset integrated
   - [ ] LangFlow accessible
   - [ ] Streamlit console operational
   - [ ] All features functional

4. Create backup plan:
   - Screenshots of all features
   - Recorded demo video (optional)
   - Offline fallback mode

**Acceptance Criteria:**
- [ ] Demo script written
- [ ] All systems operational
- [ ] Test data ready
- [ ] Screenshots captured
- [ ] Backup plan ready
- [ ] Can complete demo in 15-20 minutes

---

## Task Execution Order (Recommended)

**Day 1-2: Phase 1 (Critical)**
1. Task 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6

**Day 3: Phase 2 (Critical)**
2. Task 2.1 → (2.2, 2.3, 2.4 in parallel) → 2.5

**Day 4: Phase 3 (Critical)**
3. Task 3.1 → 3.2 → 3.3

**Day 5 (Optional): Phase 4a (Quickest)**
4. Task 4a.1 → 4a.2 → 4a.3 → 4a.4

**Day 6 (Optional): Phase 4c (Medium)**
5. Task 4c.1 → 4c.2

**Day 7 (Optional): Phase 4b (Most Complex)**
6. Task 4b.1 → 4b.2

**Final Day: Documentation & Demo**
7. Task F.1 → F.2 → F.3

---

## Notes

- **Parallelization:** Tasks 2.2, 2.3, 2.4 can be done in parallel
- **Optional Features:** Phase 4 tasks can be skipped if time is limited
- **Priority Recommendation:** If time limited, do Phases 1-3 + 4a only
- **Testing:** Run integration tests after each phase
- **Git:** Commit after completing each task
- **Documentation:** Update docs as you go, not at the end
