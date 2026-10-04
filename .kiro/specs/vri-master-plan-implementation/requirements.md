# Requirements: VRI Digital Twin - Master Plan Implementation

## Overview

Implementation of critical features for the VRI (Variable-Rate Irrigation) Digital Twin system, focusing on LangChain RAG integration, LangFlow visual workflows, intelligent notifications, and advanced analytics features. This implementation is divided into 4 phases with Phases 1-3 being critical for review by engineer Ticona.

**Context:**
- Frontend: React 19 + TypeScript (currently functional with mockData.ts)
- Backend: FastAPI + Python 3.11 (currently in demo mode with streamlit_backend.py for testing)
- Bilingual system: Fully functional with LanguageContext (Spanish/English)
- Critical review criteria: (1) Public dataset, (2) LangChain implementation
- Additional suggestion: LangFlow applied to chatbot and/or notifications
- Team split: One teammate is working on the public dataset separately

**Recent Repository Updates Integrated:**
- ✅ Streamlit Technical Console operational with 6 complete modules (667 lines)
- ✅ Enhanced RL decision samples in mockData (dec-20260831-04)
- ✅ Improved translation system with architectural descriptions
- ✅ LanguageContext fully functional (es/en switching)
- ✅ Knowledge base created (8 .md files in `backend/data/knowledge_base/`)
- ✅ Public dataset identified: Soil Moisture, Irrigation & Weather data (Italy, 2025)
  - Location: `c:\Users\ather\Downloads\gemelitos\Soil Moisture, Irrigation Actuator and Weather Dat\`
  - 5 sectors with different crops (tomato, zucchini, blueberry)
  - 789 validated irrigation events
  - ML-ready preprocessed CSVs (dataset_zone_1-5_preprocessed.csv)
  - Weather data from ERA5 reanalysis
  - Ready for Phase 1 integration into RAG system

## Goals

1. **Implement LangChain RAG system** for agronomic knowledge base with multilingual support
2. **Design and export LangFlow visual workflows** for chatbot, alerts, and RL analysis
3. **Build intelligent notification system** with LLM-based urgency classification
4. **Add advanced features**: crop calendar automation, retrospective analysis, and sensor quality scoring

## User Stories

### Phase 1 - LangChain RAG (Critical - Directly reviewed by Ticona)

**Priority: P0 (Critical)**

#### US-1.1: Knowledge Base Enhancement and Dataset Integration
**As a** system administrator  
**I want** to enhance the existing knowledge base and integrate the public dataset  
**So that** the RAG system can provide accurate, context-aware responses with real-world data

**Acceptance Criteria:**
- ✅ Existing 8 markdown files verified and functional in `backend/data/knowledge_base/`
- Public dataset files copied to `backend/data/datasets/` directory
- Dataset summary document created: `backend/data/knowledge_base/09_real_world_dataset.md`
- Summary includes: sector information, crop types, temporal coverage, key statistics
- RAG system can reference both knowledge base docs and dataset statistics
- Dataset metadata is properly cited (CC BY 4.0, Italy 2025 trial)

#### US-1.2: LangChain Dependencies Installation
**As a** developer  
**I want** all required LangChain dependencies installed  
**So that** the RAG service can function properly

**Acceptance Criteria:**
- `requirements.txt` updated with: langchain, langchain-groq, langchain-community, chromadb, faiss-cpu, sentence-transformers
- Dependencies are pinned to stable versions
- No dependency conflicts with existing packages
- All packages install successfully in Python 3.11

#### US-1.3: RAG Service Implementation
**As a** backend developer  
**I want** a complete RAG service  
**So that** the chatbot can answer questions with cited sources

**Acceptance Criteria:**
- `backend/app/services/rag_service.py` implemented with:
  - Document loader for markdown files
  - Text chunking with appropriate overlap
  - Multilingual embeddings (supports Spanish and English)
  - FAISS vector store for efficient retrieval
  - RetrievalQA chain using Groq LLM
- Service can be initialized and queried
- Responses include source citations
- Error handling for missing API keys or failed queries

#### US-1.4: Chat Endpoint
**As a** frontend developer  
**I want** a POST endpoint for chat interactions  
**So that** the frontend can communicate with the RAG system

**Acceptance Criteria:**
- Endpoint: `POST /api/v1/chat`
- Request body accepts: `{question: string, language?: string}`
- Response returns: `{answer: string, sources: Array<{content: string, metadata: object}>}`
- FastAPI automatic docs (`/docs`) show the endpoint correctly
- Endpoint handles errors gracefully (API key missing, service unavailable)

#### US-1.5: Frontend Integration
**As a** user  
**I want** the chatbot to use the RAG backend  
**So that** I get more accurate responses with sources

**Acceptance Criteria:**
- `AgronomicChatbot.tsx` updated to call `/api/v1/chat` endpoint
- Sources are displayed below the answer with proper formatting
- Fallback to direct Groq call if backend is unavailable
- Loading states and error messages are user-friendly
- Language preference is sent with the request

#### US-1.6: RAG Testing
**As a** QA engineer  
**I want** verified test scenarios  
**So that** we can confirm RAG accuracy before demo

**Acceptance Criteria:**
- 5 test questions prepared covering different topics:
  1. Crop water requirements
  2. Soil types and irrigation
  3. VRI regulations
  4. Optimal irrigation timing
  5. Disease prevention through irrigation management
- Each question returns relevant answer with correct source citation
- Test results documented in `/docs` or test file
- All tests pass before Phase 1 completion

**Definition of Done:**
- 5 test questions return accurate answers with correct sources
- Verification possible via `/docs` endpoint
- No critical bugs in RAG pipeline

---

### Phase 2 - LangFlow Visual Workflows (Critical - Explicitly requested by Ticona)

**Priority: P0 (Critical)**

#### US-2.1: LangFlow Installation and Setup
**As a** developer  
**I want** LangFlow installed and running  
**So that** I can design visual LLM workflows

**Acceptance Criteria:**
- LangFlow installed via `pip install langflow`
- Can launch with `langflow run --host 0.0.0.0 --port 7860`
- Web interface accessible at `http://localhost:7860`
- No conflicts with existing FastAPI server (port 8000)

#### US-2.2: Flow 1 - RAG Chatbot Workflow
**As a** workflow designer  
**I want** a visual representation of the RAG chatbot pipeline  
**So that** stakeholders can understand the architecture

**Acceptance Criteria:**
- Flow designed in LangFlow with components:
  1. Input: User question
  2. FAISS Retriever (using knowledge base)
  3. Groq LLM
  4. Output: Answer + Sources
- Flow mirrors the implementation from Phase 1
- Flow is tested and produces correct outputs
- Exported as Python code to `backend/app/services/langflow_pipelines/chatbot_rag.py`
- Screenshot captured for demo presentation

#### US-2.3: Flow 2 - Intelligent Alerts Workflow
**As a** workflow designer  
**I want** a visual workflow for smart alert processing  
**So that** alerts are automatically classified and routed

**Acceptance Criteria:**
- Flow designed in LangFlow with components:
  1. Input: Sensor data event
  2. Anomaly detector
  3. LLM urgency classifier (CRITICAL/MODERATE/INFO)
  4. Personalized message generator
  5. Multi-channel dispatcher
- Flow is tested with sample sensor events
- Exported as Python code to `backend/app/services/langflow_pipelines/intelligent_alerts.py`
- Screenshot captured for demo presentation

#### US-2.4: Flow 3 - RL Analysis with Explainability
**As a** workflow designer  
**I want** a visual workflow for RL decision validation  
**So that** RL recommendations are explainable and require human approval

**Acceptance Criteria:**
- Flow designed in LangFlow with components:
  1. Input: Zone state data
  2. RL Agent (decision maker)
  3. SHAP explainer
  4. LLM validator (generates human-readable explanation)
  5. Human approval gate
- Flow demonstrates the explainability pipeline
- Exported as Python code to `backend/app/services/langflow_pipelines/rl_explainability.py`
- Screenshot captured for demo presentation

#### US-2.5: LangFlow Documentation
**As a** team member  
**I want** documentation of all LangFlow workflows  
**So that** I can understand and maintain them

**Acceptance Criteria:**
- All 3 flows designed and functional
- All 3 flows exported as Python code
- Screenshots saved in `backend/docs/langflow_screenshots/`
- Brief README in `backend/app/services/langflow_pipelines/` explaining each flow
- Flows are ready for demo presentation

**Definition of Done:**
- 3 flows designed, tested, and exported
- Screenshots captured and organized
- Code exported to `langflow_pipelines/` directory

---

### Phase 3 - Intelligent Notification System

**Priority: P0 (Critical)**

#### US-3.1: Notification Service Structure
**As a** backend developer  
**I want** a notification service module  
**So that** alerts can be processed intelligently

**Acceptance Criteria:**
- File created: `backend/app/services/notification_service.py`
- Service imports necessary LLM and communication libraries
- Service is properly structured with clear function signatures
- Error handling for API failures

#### US-3.2: Urgency Classification
**As a** system operator  
**I want** automatic urgency classification of events  
**So that** critical issues are prioritized

**Acceptance Criteria:**
- Function: `classify_urgency(event: dict) -> str`
- Uses LLM (Groq) to classify events into: CRITICAL, MODERATE, INFO
- Classification considers:
  - Sensor value deviation from normal range
  - Rate of change
  - Time of day
  - Crop growth stage
- Returns urgency level with confidence score
- Processing time < 3 seconds per event

#### US-3.3: Personalized Message Generation
**As a** notification recipient  
**I want** messages tailored to my role  
**So that** I receive actionable information

**Acceptance Criteria:**
- Function: `generate_message(event: dict, role: str) -> str`
- Generates role-specific messages:
  - **Agronomist**: Technical details, sensor readings, recommended actions
  - **Producer**: Simple language, impact on crop, what to do
  - **Technician**: Equipment-focused, maintenance actions
- Message length: max 3 lines (except for critical alerts)
- Messages are in Spanish by default, English optional
- Uses LLM to generate contextually appropriate text

#### US-3.4: Multi-Channel Dispatcher
**As a** system administrator  
**I want** alerts routed to appropriate channels  
**So that** urgent issues get immediate attention

**Acceptance Criteria:**
- Dispatcher routes based on urgency:
  - **CRITICAL**: Email + SMS
  - **MODERATE**: Push notification
  - **INFO**: Dashboard only
- Supports multiple recipients per channel
- Implements rate limiting (max 5 CRITICAL per hour per user)
- Logs all dispatched notifications
- Graceful degradation if a channel fails

#### US-3.5: Process Alert Endpoint
**As a** frontend developer  
**I want** an endpoint to process alerts  
**So that** sensor events trigger intelligent notifications

**Acceptance Criteria:**
- Endpoint: `POST /api/v1/process-alert`
- Request body: `{event: {sensor_id, value, timestamp, zone_id}, test_mode?: boolean}`
- Response: `{urgency: string, messages: {agronomist: string, producer: string, technician: string}, channels: string[]}`
- Endpoint orchestrates: classification → message generation → dispatch
- Test mode skips actual sending (for demo/testing)
- Documented in FastAPI `/docs`

#### US-3.6: Notification Testing
**As a** QA engineer  
**I want** verified test cases for notifications  
**So that** the system handles various scenarios correctly

**Acceptance Criteria:**
- 3+ test events prepared:
  1. Critical low soil moisture during day
  2. Moderate temperature spike
  3. Info: normal sensor reading
- Each test event processed successfully
- Urgency classification matches expectations
- Messages are appropriate for each role
- Test results logged or documented

**Definition of Done:**
- `POST /process-alert` with critical sensor event returns JSON with `urgency: "critical"` and role-specific messages
- All 3 test cases pass
- No errors in processing pipeline

---

### Phase 4a - Automatic Crop Calendar / Phenological Stage

**Priority: P1 (Nice to have, differentiator)**

#### US-4a.1: Crop Calendar Data
**As a** agronomist  
**I want** a structured crop calendar  
**So that** the system knows the growth stage of each zone

**Acceptance Criteria:**
- CSV file: `backend/data/crop_calendar.csv`
- Columns: `zone_id, crop_type, planting_date, flowering_date_expected, harvest_date, kc_initial, kc_mid, kc_late`
- Data includes all zones from mockData.ts
- Dates are realistic for typical crop cycles
- File is properly formatted and parseable

#### US-4a.2: Phenological Stage Calculation
**As a** system  
**I want** to calculate current phenological stage  
**So that** irrigation recommendations are stage-appropriate

**Acceptance Criteria:**
- Function that calculates stage based on current date vs. planting/flowering/harvest dates
- Returns: `{stage: 'initial' | 'development' | 'mid-season' | 'late-season', days_since_planting: number, kc_current: number}`
- Logic accounts for typical crop development patterns
- Updates dynamically as dates change

#### US-4a.3: Dynamic Kc Integration
**As a** digital twin engine  
**I want** Kc values to update based on phenological stage  
**So that** water calculations are accurate

**Acceptance Criteria:**
- `digitalTwinEngine.ts` or similar updated to use stage-based Kc
- Replaces any hardcoded/manual Kc values
- Kc interpolated smoothly between stages
- Works for all zones simultaneously

#### US-4a.4: UI Display of Phenological Stage
**As a** user  
**I want** to see the current growth stage  
**So that** I understand the context of irrigation decisions

**Acceptance Criteria:**
- Growth stage displayed on GIS map or zone panel
- Shows: stage name, days since planting, current Kc
- Visual indicator (color/icon) for stage
- Updates when zone or date changes

**Definition of Done:**
- Kc calculation in `digitalTwinEngine.ts` is dynamic based on phenological stage
- Current stage visible in UI (map or zone panel)
- Accurate for all zones

**Estimated Time:** 3-4 hours

---

### Phase 4b - Retrospective "What-If" Mode

**Priority: P1 (Nice to have, most complex of Phase 4)**

#### US-4b.1: Retrospective Simulation Engine
**As a** data analyst  
**I want** to simulate past irrigation scenarios  
**So that** I can learn from historical decisions

**Acceptance Criteria:**
- Extends `digitalTwinEngine.ts` or `WhatIfSimulator.tsx`
- New function: `simulateRetrospective(historical_date, zone_id, altered_params)`
- Recalculates soil moisture from that historical date forward
- Uses actual weather data from mockData.ts for that period
- Returns simulated vs. actual comparison

#### US-4b.2: Historical Data Comparison
**As a** analyst  
**I want** to compare simulated outcomes with actual results  
**So that** I can validate the model

**Acceptance Criteria:**
- Function compares simulated soil moisture with actual recorded values
- Calculates metrics: MAE (Mean Absolute Error), RMSE, R²
- Identifies days where simulation diverges from reality
- Suggests possible reasons (unmodeled rain, sensor drift, etc.)

#### US-4b.3: UI Extension for Retrospective Mode
**As a** user  
**I want** a retrospective mode in the What-If Simulator  
**So that** I can explore historical scenarios

**Acceptance Criteria:**
- `WhatIfSimulator.tsx` extended with "Retrospective Mode" toggle
- Date picker for selecting historical date
- Parameter adjustment controls (e.g., +5mm irrigation)
- Chart showing: actual vs. simulated soil moisture over time
- Summary metrics displayed clearly

#### US-4b.4: Retrospective Insights Generation
**As a** user  
**I want** automatic insights from retrospective analysis  
**So that** I can quickly understand what I could have done differently

**Acceptance Criteria:**
- System generates 2-3 bullet point insights
- Examples: "5mm less irrigation on June 15 would have saved water without stress" or "Actual outcome matched simulation closely - good model accuracy"
- Insights are actionable and non-technical

**Definition of Done:**
- Retrospective mode functional in What-If Simulator
- Historical date + altered parameters produces simulation
- Comparison with actual data shown in chart
- Works with mockData.ts historical records

**Estimated Time:** 4-6 hours

---

### Phase 4c - Sensor Data Quality Scoring

**Priority: P1 (Nice to have, fastest to implement)**

#### US-4c.1: Data Quality Metrics Collection
**As a** system  
**I want** to track sensor data quality metrics  
**So that** I can identify unreliable sensors

**Acceptance Criteria:**
- Extension to `anomalyDetectionEngine.ts`
- Tracks per sensor (last 7 days):
  - Valid reading percentage (not null, not out-of-range)
  - Noise level (standard deviation of readings)
  - Time since last simulated calibration
- Metrics stored in memory or localStorage

#### US-4c.2: Quality Score Calculation
**As a** system  
**I want** a single quality score per sensor  
**So that** users can quickly assess sensor health

**Acceptance Criteria:**
- Function: `calculateSensorQualityScore(sensor_id) -> number (0-100)`
- Formula combines:
  - Valid reading % (40% weight)
  - Noise level / expected variance (30% weight)
  - Recency of calibration (30% weight)
- Score of 80+ = good, 60-79 = fair, <60 = poor
- Scores update daily or on demand

#### US-4c.3: Quality Score UI Display
**As a** user  
**I want** to see sensor quality scores  
**So that** I can trust or question sensor data

**Acceptance Criteria:**
- New section in `TelemetryAnalytics.tsx` showing sensor quality scores
- List or table format with sensor ID, score, color indicator
- Colors: green (80+), yellow (60-79), red (<60)
- Click on sensor shows detailed metrics breakdown
- Responsive design for mobile/desktop

#### US-4c.4: Quality Alerts
**As a** system operator  
**I want** alerts for poor quality sensors  
**So that** I can take corrective action

**Acceptance Criteria:**
- Automatic alert when sensor score drops below 60
- Alert shows which metric is problematic
- Suggested action: recalibrate, check connection, replace sensor
- Alert integrates with Phase 3 notification system (INFO level)

**Definition of Done:**
- Sensor quality scores visible in `TelemetryAnalytics.tsx`
- Scores calculated correctly (0-100)
- Color-coded display (green/yellow/red)
- Works for all sensors in mockData.ts

**Estimated Time:** 3-4 hours

---

## Non-Functional Requirements

### NFR-1: Performance
- RAG queries complete in < 5 seconds
- LangFlow workflows export without errors
- Notification processing < 3 seconds per event
- UI remains responsive during all operations

### NFR-2: Reliability
- Graceful degradation when backend unavailable (chatbot fallback)
- Error messages are user-friendly and actionable
- No data loss during notification dispatch failures

### NFR-3: Maintainability
- Code is well-documented with docstrings
- LangFlow exports are version-controlled
- Clear separation between Phase 1-3 (critical) and Phase 4 (optional)

### NFR-4: Usability
- All UI text is bilingual (Spanish/English)
- Loading states clearly indicate progress
- Error states suggest corrective actions

### NFR-5: Security
- API keys stored securely (environment variables)
- No sensitive data in logs or error messages
- Rate limiting on notification channels

---

## Success Criteria

### Phase 1 Success
- [ ] Knowledge base created (8-10 .md files)
- [ ] RAG service functional
- [ ] `/api/v1/chat` endpoint working
- [ ] Frontend displays answers with sources
- [ ] 5 test questions pass with correct sources

### Phase 2 Success
- [ ] LangFlow installed and running
- [ ] 3 flows designed and tested
- [ ] Python code exported for each flow
- [ ] Screenshots captured for demo
- [ ] Documentation completed

### Phase 3 Success
- [ ] Notification service implemented
- [ ] `/api/v1/process-alert` endpoint working
- [ ] Urgency classification accurate
- [ ] Role-specific messages generated
- [ ] 3 test events processed correctly

### Phase 4 Success (Optional)
- [ ] 4a: Crop calendar integrated, Kc is dynamic
- [ ] 4b: Retrospective mode functional
- [ ] 4c: Sensor quality scores displayed

### Overall Success
- [ ] README.md updated mentioning LangChain/LangFlow
- [ ] Backend and frontend run without errors
- [ ] Demo-ready state achieved
- [ ] All critical features (Phases 1-3) complete

---

## Priority Summary

**P0 (Critical - Must have for Ticona review):**
- Phase 1: LangChain RAG
- Phase 2: LangFlow workflows
- Phase 3: Intelligent notifications

**P1 (Nice to have - Differentiators):**
- Phase 4a: Crop calendar (fastest, 3-4h)
- Phase 4c: Sensor quality (fast, 3-4h)
- Phase 4b: Retrospective analysis (complex, 4-6h)

**Recommendation if time is limited:**
Complete P0 phases first, then add 4a (crop calendar) as it provides the most value for the least time investment and improves the core digital twin accuracy.

---

## Dependencies & Constraints

**External Dependencies:**
- Groq API key (for LLM calls)
- LangFlow library compatibility with Python 3.11
- FAISS library installation on target system

**Team Dependencies:**
- Teammate working on public dataset (coordinate separately)
- Requires coordination for demo timing

**Technical Constraints:**
- Backend must remain compatible with existing FastAPI structure
- Frontend must maintain fallback to direct Groq calls
- Cannot break existing functionality

**Time Constraints:**
- Phases 1-3 are non-negotiable (estimated 3-4 days total)
- Phase 4 can be partially implemented based on available time
- Demo deadline drives prioritization

---

## Out of Scope

- Public dataset integration (handled by teammate)
- Production deployment configuration
- Load testing and scalability optimization
- User authentication and authorization
- Real sensor hardware integration
- Email/SMS gateway integration (mock/simulate in Phase 3)

---

## Risks & Mitigations

**Risk 1:** LangChain dependencies conflict with existing packages  
**Mitigation:** Test in virtual environment first, pin compatible versions

**Risk 2:** LangFlow UI too complex for quick workflow design  
**Mitigation:** Follow examples from LangFlow documentation, allocate 1 full day

**Risk 3:** Groq API rate limits during testing  
**Mitigation:** Implement caching, use test mode flags, monitor quota

**Risk 4:** Time runs out before Phase 4 completion  
**Mitigation:** Prioritize 4a (crop calendar) first as it's quickest and highest impact

**Risk 5:** Integration issues between Phase 3 notification system and Phase 2 LangFlow  
**Mitigation:** Design Phase 3 to work standalone first, then optionally integrate LangFlow export

---

## Glossary

- **RAG**: Retrieval-Augmented Generation
- **LangChain**: Framework for building LLM applications
- **LangFlow**: Visual workflow designer for LangChain
- **Groq**: Fast LLM inference API
- **FAISS**: Facebook AI Similarity Search (vector database)
- **Kc**: Crop coefficient (irrigation calculation parameter)
- **VRI**: Variable-Rate Irrigation
- **RL**: Reinforcement Learning
- **SHAP**: SHapley Additive exPlanations (explainability framework)
- **STT**: Speech-to-Text
- **TTS**: Text-to-Speech
