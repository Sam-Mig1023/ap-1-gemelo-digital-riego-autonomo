# Requirements Document

## Introduction

This requirements specification defines the comprehensive integration of LangChain, LangFlow, and intelligent notification systems into the VRI (Variable-Rate Irrigation) Digital Twin project. The system is a React 19 + TypeScript frontend with FastAPI + Python 3.11 backend irrigation management platform that currently operates with mock data and demo mode. This integration focuses on four prioritized phases:

1. **Phase 1**: LangChain RAG (Retrieval-Augmented Generation) implementation for knowledge-grounded chatbot responses
2. **Phase 2**: LangFlow visual workflow design for RAG chatbot, intelligent alerts, and RL analysis with explainability
3. **Phase 3**: Intelligent notification system with LLM-based urgency classification and multi-channel dispatch
4. **Phase 4**: Three enhancement features including automatic crop calendar, retrospective what-if analysis, and sensor quality scoring

The system will be reviewed by Engineer Ticona who specifically expects: (1) public dataset documentation, (2) functional LangChain implementation, and (3) LangFlow workflow demonstrations. One team member is already working on the public dataset separately.

## Glossary

- **VRI_System**: The Variable-Rate Irrigation digital twin platform combining frontend and backend components
- **Backend_Service**: FastAPI Python 3.11 service providing REST API endpoints
- **Frontend_Application**: React 19 + TypeScript client application with existing mockData.ts
- **Knowledge_Base**: Collection of 8-10 markdown files containing agronomic domain knowledge
- **RAG_Service**: Retrieval-Augmented Generation service using LangChain for knowledge-grounded responses
- **LangFlow_Engine**: Visual workflow design tool for creating AI pipelines
- **FAISS_Vectorstore**: Facebook AI Similarity Search vector database for document embeddings
- **Groq_LLM**: Language model API service using LLaMA 3.3 for text generation
- **Notification_Dispatcher**: Multi-channel alert delivery system with urgency-based routing
- **Agronomic_Chatbot**: Conversational interface component in AgronomicChatbot.tsx
- **Digital_Twin_Engine**: Simulation engine in digitalTwinEngine.ts implementing Green-Ampt hydraulic model
- **RL_Agent**: Reinforcement Learning agent providing irrigation recommendations
- **Telemetry_System**: Sensor data collection and anomaly detection system
- **SHAP_Explainer**: SHapley Additive exPlanations tool for model interpretability
- **Crop_Calendar**: Database of phenological stages with Kc coefficient mapping
- **Quality_Score**: Sensor reliability metric ranging 0-100 based on validity, noise, and calibration

## Requirements

### Requirement 1: Knowledge Base Creation

**User Story:** As a system administrator, I want to establish a structured agronomic knowledge base, so that the chatbot can provide accurate, domain-specific responses.

#### Acceptance Criteria

1. THE Backend_Service SHALL create directory backend/data/knowledge_base/ with subdirectories for crops, soils, irrigation, and regulations
2. THE Backend_Service SHALL store 8-10 markdown files covering topics including crop water requirements, soil properties, irrigation methods, and local water regulations
3. WHEN a markdown file is requested, THE Backend_Service SHALL return the file content in UTF-8 encoding
4. THE Knowledge_Base SHALL include at least one document defining crop coefficients (Kc) for major crops
5. THE Knowledge_Base SHALL include at least one document defining soil hydraulic conductivity (Ksat) values by soil texture

### Requirement 2: LangChain Dependency Installation

**User Story:** As a backend developer, I want all required LangChain dependencies installed, so that I can implement RAG functionality.

#### Acceptance Criteria

1. THE Backend_Service SHALL include langchain in requirements.txt
2. THE Backend_Service SHALL include langchain-groq in requirements.txt
3. THE Backend_Service SHALL include langchain-community in requirements.txt
4. THE Backend_Service SHALL include chromadb in requirements.txt
5. THE Backend_Service SHALL include faiss-cpu in requirements.txt
6. THE Backend_Service SHALL include sentence-transformers in requirements.txt
7. WHEN Backend_Service starts, THE Backend_Service SHALL verify all dependencies are importable without errors

### Requirement 3: RAG Service Implementation

**User Story:** As a backend developer, I want a RAG service that loads knowledge base documents and provides retrieval-augmented responses, so that chatbot answers are grounded in verified sources.

#### Acceptance Criteria

1. THE RAG_Service SHALL load all markdown files from backend/data/knowledge_base/ recursively
2. THE RAG_Service SHALL split loaded documents into chunks of maximum 500 tokens with 50 token overlap
3. THE RAG_Service SHALL generate embeddings using paraphrase-multilingual-MiniLM-L12-v2 model for multilingual support
4. THE RAG_Service SHALL store embeddings in FAISS_Vectorstore for efficient similarity search
5. THE RAG_Service SHALL implement RetrievalQA chain combining FAISS_Vectorstore with Groq_LLM
6. WHEN a question is submitted, THE RAG_Service SHALL retrieve top 3 most relevant document chunks
7. WHEN a question is submitted, THE RAG_Service SHALL return both generated answer and source document references
8. THE RAG_Service SHALL cache the vectorstore to avoid regenerating embeddings on every request
9. WHEN Backend_Service restarts, THE RAG_Service SHALL reload vectorstore from cache if knowledge base is unchanged

### Requirement 4: Chat Endpoint with RAG

**User Story:** As a frontend developer, I want a REST endpoint that accepts questions and returns RAG-enhanced answers with sources, so that the chatbot can cite verified information.

#### Acceptance Criteria

1. THE Backend_Service SHALL expose endpoint POST /api/v1/chat accepting JSON with question field
2. WHEN POST /api/v1/chat receives a request, THE Backend_Service SHALL pass the question to RAG_Service
3. WHEN RAG_Service completes processing, THE Backend_Service SHALL return JSON containing answer and sources fields
4. THE sources field SHALL contain an array of objects with document_name and excerpt properties
5. WHEN request includes x-groq-api-key header, THE Backend_Service SHALL use that API key for Groq_LLM calls
6. WHEN request lacks x-groq-api-key header, THE Backend_Service SHALL return HTTP 401 with error message "Groq API key required"
7. WHEN RAG_Service encounters an error, THE Backend_Service SHALL return HTTP 500 with descriptive error message
8. THE Backend_Service SHALL document the /api/v1/chat endpoint in OpenAPI/Swagger documentation

### Requirement 5: Chatbot Frontend RAG Integration

**User Story:** As an agronomist, I want the chatbot to cite sources for its answers, so that I can verify the information and trace it back to authoritative documents.

#### Acceptance Criteria

1. THE Agronomic_Chatbot SHALL send user questions to POST /api/v1/chat instead of directly calling Groq API
2. WHEN Backend_Service returns a response, THE Agronomic_Chatbot SHALL display the answer text in the message thread
3. WHEN Backend_Service returns sources, THE Agronomic_Chatbot SHALL display each source below the answer with document name and excerpt
4. WHEN Backend_Service is unreachable, THE Agronomic_Chatbot SHALL fall back to direct Groq_LLM API call without RAG
5. WHEN using fallback mode, THE Agronomic_Chatbot SHALL display a warning message "Backend unavailable, responses may not be grounded in knowledge base"
6. THE Agronomic_Chatbot SHALL render source document names as clickable elements that expand to show full excerpt
7. THE Agronomic_Chatbot SHALL include visual distinction between RAG-enhanced responses and fallback responses

### Requirement 6: RAG Verification Testing

**User Story:** As a QA engineer, I want to verify that RAG returns correct sources for test questions, so that I can confirm the system is working as intended.

#### Acceptance Criteria

1. THE RAG_Service SHALL correctly answer question "What is the Kc for potato in mid-season?" by returning a numeric value and citing the source document
2. THE RAG_Service SHALL correctly answer question "What is the hydraulic conductivity of sandy loam soil?" by returning a value and citing the soil properties document
3. THE RAG_Service SHALL correctly answer question "What irrigation methods are suitable for variable-rate irrigation?" by citing the irrigation methods document
4. THE RAG_Service SHALL correctly answer question "What are the water use regulations in the region?" by citing the regulations document
5. THE RAG_Service SHALL correctly answer a multilingual question in Spanish and return Spanish answer with appropriate sources
6. WHEN Backend_Service /docs endpoint is accessed, THE Backend_Service SHALL show /api/v1/chat as executable with example request/response
7. FOR ALL five test questions, THE RAG_Service SHALL return response time under 5 seconds

### Requirement 7: LangFlow Installation and Execution

**User Story:** As a system administrator, I want to install and run LangFlow, so that I can design visual AI workflows without writing code.

#### Acceptance Criteria

1. THE Backend_Service SHALL include langflow in requirements.txt
2. WHEN administrator executes "langflow run --host 0.0.0.0 --port 7860", THE LangFlow_Engine SHALL start successfully
3. WHEN administrator navigates to http://localhost:7860, THE LangFlow_Engine SHALL display the visual workflow designer interface
4. THE LangFlow_Engine SHALL remain accessible while Backend_Service is running on port 8000
5. THE LangFlow_Engine SHALL support saving and loading flow configurations

### Requirement 8: RAG Chatbot Flow Design

**User Story:** As an AI engineer, I want to design a visual RAG chatbot flow in LangFlow, so that the architecture is clearly documented and maintainable by non-programmers.

#### Acceptance Criteria

1. THE LangFlow_Engine SHALL support creating a flow with Question input node, FAISS Retriever node, Groq LLM node, and Answer output node
2. THE RAG chatbot flow SHALL connect Question → FAISS_Retriever → Groq_LLM → Answer with Sources
3. THE FAISS_Retriever node SHALL configure vectorstore path pointing to backend/data/knowledge_base/
4. THE Groq_LLM node SHALL configure model selection for llama-3.3-70b-versatile
5. WHEN the flow is executed with test question, THE LangFlow_Engine SHALL return answer matching RAG_Service behavior
6. THE LangFlow_Engine SHALL export the flow as Python code to backend/app/services/langflow_pipelines/rag_chatbot.py
7. THE LangFlow_Engine SHALL export the flow as JSON to backend/app/services/langflow_pipelines/rag_chatbot.json
8. THE AI engineer SHALL capture a screenshot of the complete flow for documentation purposes

### Requirement 9: Intelligent Alerts Flow Design

**User Story:** As an AI engineer, I want to design a visual intelligent notification flow, so that the alert generation and dispatch logic is transparent and modifiable without code changes.

#### Acceptance Criteria

1. THE LangFlow_Engine SHALL support creating a flow with nodes: Sensor Data Input, Anomaly Detector, Urgency Classifier LLM, Message Generator, and Multi-channel Dispatcher
2. THE intelligent alerts flow SHALL implement path: [Sensor Data] → [Anomaly Detector] → [Urgency Classifier] → [Message Generator] → [Dispatcher]
3. THE Urgency Classifier node SHALL use Groq_LLM to classify events as CRITICAL, MODERATE, or INFO
4. THE Message Generator node SHALL use Groq_LLM to create role-specific messages for agronomist and producer roles
5. THE Multi-channel Dispatcher node SHALL route CRITICAL to email and SMS, MODERATE to push notification, INFO to dashboard only
6. WHEN the flow is executed with a critical sensor event, THE LangFlow_Engine SHALL generate appropriate messages and routing decisions
7. THE LangFlow_Engine SHALL export the flow as Python code to backend/app/services/langflow_pipelines/alert_system.py
8. THE LangFlow_Engine SHALL export the flow as JSON to backend/app/services/langflow_pipelines/alert_system.json
9. THE AI engineer SHALL capture a screenshot of the complete flow for documentation purposes

### Requirement 10: RL Analysis with Explainability Flow Design

**User Story:** As an AI engineer, I want to design a visual RL analysis flow with explainability, so that the decision validation process is transparent and auditable.

#### Acceptance Criteria

1. THE LangFlow_Engine SHALL support creating a flow with nodes: Zone State Input, RL Agent, SHAP Explainer, LLM Validator, and Human Approval Interface
2. THE RL analysis flow SHALL implement path: [Zone State] → [RL_Agent] → [SHAP_Explainer] → [LLM Validator] → [Human Approval]
3. THE RL_Agent node SHALL generate irrigation dose recommendations in mm
4. THE SHAP_Explainer node SHALL compute feature importance scores for each sensor input
5. THE LLM Validator node SHALL use Groq_LLM to verify that the RL decision is agronomically reasonable given SHAP explanations
6. WHEN the flow is executed with test zone state, THE LangFlow_Engine SHALL output recommendation with explainability report
7. THE LangFlow_Engine SHALL export the flow as Python code to backend/app/services/langflow_pipelines/rl_analysis.py
8. THE LangFlow_Engine SHALL export the flow as JSON to backend/app/services/langflow_pipelines/rl_analysis.json
9. THE AI engineer SHALL capture a screenshot of the complete flow for documentation purposes

### Requirement 11: LangFlow Documentation

**User Story:** As a project reviewer, I want to see documentation of LangFlow workflows, so that I can understand the visual design without running the system.

#### Acceptance Criteria

1. THE VRI_System SHALL include file backend/docs/langflow_flows.md documenting all three flows
2. THE documentation SHALL embed or reference screenshots of each LangFlow visual workflow
3. THE documentation SHALL describe inputs, outputs, and purpose of each flow
4. THE documentation SHALL provide instructions for importing the JSON flow files into LangFlow
5. THE documentation SHALL explain how to execute each flow from Python code

### Requirement 12: Notification Service Urgency Classification

**User Story:** As a backend developer, I want a service that classifies event urgency using LLM, so that alerts are prioritized correctly.

#### Acceptance Criteria

1. THE Backend_Service SHALL implement notification_service.py in backend/app/services/
2. THE Notification_Dispatcher SHALL define function classify_urgency accepting event dictionary with moisture, threshold, crop, and growth_stage fields
3. WHEN classify_urgency is called, THE Notification_Dispatcher SHALL construct a prompt asking Groq_LLM to classify urgency as CRITICAL, MODERATE, or INFO
4. THE Notification_Dispatcher SHALL parse LLM response and return urgency level as string literal "critical", "moderate", or "info"
5. WHEN moisture is 15% or more below threshold, THE Notification_Dispatcher SHALL classify as "critical"
6. WHEN moisture is 5-15% below threshold, THE Notification_Dispatcher SHALL classify as "moderate"
7. WHEN moisture is within 5% of threshold, THE Notification_Dispatcher SHALL classify as "info"
8. THE Notification_Dispatcher SHALL handle LLM API errors by falling back to rule-based classification

### Requirement 13: Notification Service Message Generation

**User Story:** As a backend developer, I want a service that generates personalized alert messages for different user roles, so that users receive information appropriate to their expertise level.

#### Acceptance Criteria

1. THE Notification_Dispatcher SHALL define function generate_message accepting event dictionary and role string
2. WHEN generate_message is called with role "agronomist", THE Notification_Dispatcher SHALL return a technical message including sensor values, thresholds, and agronomic reasoning
3. WHEN generate_message is called with role "producer", THE Notification_Dispatcher SHALL return a simple message with actionable recommendation in non-technical language
4. THE Notification_Dispatcher SHALL ensure generated messages are maximum 3 lines
5. THE Notification_Dispatcher SHALL use Groq_LLM to generate natural language messages
6. THE Notification_Dispatcher SHALL include event severity, affected zone, and recommended action in all messages
7. WHEN generate_message encounters LLM API error, THE Notification_Dispatcher SHALL return a fallback template-based message

### Requirement 14: Multi-Channel Alert Dispatch

**User Story:** As an operations engineer, I want alerts routed to appropriate channels based on urgency, so that critical issues receive immediate attention.

#### Acceptance Criteria

1. THE Notification_Dispatcher SHALL define function dispatch_notification accepting message, urgency, and recipient parameters
2. WHEN urgency is "critical", THE Notification_Dispatcher SHALL send message via email channel and SMS channel
3. WHEN urgency is "moderate", THE Notification_Dispatcher SHALL send message via push notification channel only
4. WHEN urgency is "info", THE Notification_Dispatcher SHALL log message to dashboard only without external dispatch
5. THE Notification_Dispatcher SHALL log all dispatches to audit log with timestamp, urgency, channel, and recipient
6. THE Notification_Dispatcher SHALL implement stub functions for email, SMS, and push notification that log the action without requiring external service integration
7. THE Notification_Dispatcher SHALL return dispatch result including channels_used array and delivery_status

### Requirement 15: Alert Processing Endpoint

**User Story:** As a frontend developer, I want an endpoint that processes sensor events and returns urgency classification with role-specific messages, so that I can display contextual alerts to users.

#### Acceptance Criteria

1. THE Backend_Service SHALL expose endpoint POST /api/v1/process-alert accepting JSON with event object containing moisture, threshold, crop, growth_stage, and zone_id fields
2. WHEN POST /api/v1/process-alert receives a request, THE Backend_Service SHALL call classify_urgency to determine urgency level
3. WHEN urgency is determined, THE Backend_Service SHALL call generate_message for both "agronomist" and "producer" roles
4. WHEN messages are generated, THE Backend_Service SHALL call dispatch_notification with appropriate routing
5. THE Backend_Service SHALL return JSON response containing urgency, agronomist_message, producer_message, and channels_used fields
6. WHEN request includes critical event (moisture 15%+ below threshold), THE Backend_Service SHALL return urgency "critical" with both email and sms in channels_used
7. WHEN request includes moderate event, THE Backend_Service SHALL return urgency "moderate" with only push in channels_used
8. THE Backend_Service SHALL return HTTP 400 when required event fields are missing
9. THE Backend_Service SHALL document the /api/v1/process-alert endpoint in OpenAPI/Swagger documentation

### Requirement 16: Alert System Integration Testing

**User Story:** As a QA engineer, I want to verify the alert system works end-to-end with different event scenarios, so that I can confirm correct urgency classification and message generation.

#### Acceptance Criteria

1. WHEN POST /api/v1/process-alert is called with critical event (moisture 20%, threshold 40%, crop "potato"), THE Backend_Service SHALL return urgency "critical" and agronomist_message containing technical details
2. WHEN POST /api/v1/process-alert is called with moderate event (moisture 30%, threshold 40%, crop "potato"), THE Backend_Service SHALL return urgency "moderate" and producer_message in simple language
3. WHEN POST /api/v1/process-alert is called with info event (moisture 38%, threshold 40%, crop "potato"), THE Backend_Service SHALL return urgency "info" and channels_used containing only "dashboard"
4. FOR ALL three test scenarios, THE Backend_Service SHALL return response time under 3 seconds
5. FOR ALL three test scenarios, THE agronomist_message and producer_message fields SHALL be different demonstrating role-based personalization

### Requirement 17: Crop Calendar Data Structure

**User Story:** As a backend developer, I want a CSV data structure defining crop phenological stages, so that the system can automatically determine current growth stage.

#### Acceptance Criteria

1. THE Backend_Service SHALL create file backend/data/crop_calendar.csv with columns: zone_id, crop, planting_date, expected_flowering_date, expected_harvest_date
2. THE crop_calendar.csv SHALL contain at least one row per zone in the VRI_System
3. THE crop_calendar.csv SHALL use ISO 8601 date format (YYYY-MM-DD) for all date fields
4. WHEN Backend_Service starts, THE Backend_Service SHALL validate that crop_calendar.csv exists and is readable
5. THE Backend_Service SHALL include pandas in requirements.txt for CSV parsing

### Requirement 18: Phenological Stage Calculation

**User Story:** As a backend developer, I want a function that calculates the current phenological stage based on crop calendar and current date, so that Kc coefficients can be dynamically adjusted.

#### Acceptance Criteria

1. THE Backend_Service SHALL implement function calculate_phenological_stage accepting zone_id and current_date parameters
2. WHEN calculate_phenological_stage is called, THE Backend_Service SHALL load crop_calendar.csv and locate row matching zone_id
3. THE Backend_Service SHALL calculate days_since_planting by subtracting planting_date from current_date
4. WHEN days_since_planting is less than 25% of total crop cycle, THE Backend_Service SHALL return stage "initial" with Kc 0.35
5. WHEN days_since_planting is 25-50% of total crop cycle, THE Backend_Service SHALL return stage "development" with Kc 0.75
6. WHEN days_since_planting is 50-85% of total crop cycle, THE Backend_Service SHALL return stage "mid-season" with Kc 1.15
7. WHEN days_since_planting is 85-100% of total crop cycle, THE Backend_Service SHALL return stage "late-season" with Kc 0.85
8. THE Backend_Service SHALL return stage object containing stage_name, kc_coefficient, and days_to_next_stage fields
9. WHEN zone_id is not found in crop_calendar.csv, THE Backend_Service SHALL return error with message "Zone not found in crop calendar"

### Requirement 19: Dynamic Kc Integration with Digital Twin

**User Story:** As a frontend developer, I want the digital twin to use dynamic Kc values from phenological stage calculation, so that evapotranspiration predictions are accurate throughout the growing season.

#### Acceptance Criteria

1. THE Digital_Twin_Engine SHALL call calculate_phenological_stage for each zone before computing evapotranspiration
2. THE Digital_Twin_Engine SHALL use the returned kc_coefficient instead of the currently hardcoded Kc value
3. WHEN Digital_Twin_Engine performs water balance simulation, THE Digital_Twin_Engine SHALL apply dynamically calculated Kc to ETo
4. THE Digital_Twin_Engine SHALL cache phenological stage for each zone and update only when date changes to avoid repeated calculations
5. WHEN Digital_Twin_Engine encounters error from calculate_phenological_stage, THE Digital_Twin_Engine SHALL fall back to default Kc value of 1.0 and log warning

### Requirement 20: Phenological Stage Display on Map

**User Story:** As an agronomist, I want to see the current phenological stage displayed on the GIS map for each zone, so that I can quickly assess crop development status.

#### Acceptance Criteria

1. THE Frontend_Application SHALL fetch phenological stage for each zone from Backend_Service endpoint GET /api/v1/fields/{field_id}/zones/{zone_id}/phenology
2. WHEN phenological stage data is received, THE Frontend_Application SHALL display stage name as text overlay on each zone in the GIS map
3. THE Frontend_Application SHALL display Kc coefficient value alongside stage name
4. THE Frontend_Application SHALL color-code stage display: blue for "initial", green for "development", yellow for "mid-season", orange for "late-season"
5. WHEN zone panel is opened, THE Frontend_Application SHALL show detailed phenological information including planting_date, current_stage, days_in_stage, and days_to_next_stage
6. THE Frontend_Application SHALL update phenological stage display automatically when date changes

### Requirement 21: Retrospective Simulation Mode

**User Story:** As an agronomist, I want to run retrospective simulations comparing predicted vs actual outcomes for historical dates, so that I can evaluate the digital twin accuracy and learn from past decisions.

#### Acceptance Criteria

1. THE Digital_Twin_Engine SHALL implement function retrospective_simulation accepting historical_date, zone_id, and altered_parameter parameters
2. THE altered_parameter SHALL support modifying irrigation_mm, temperature_c, or humidity_pct for the historical date
3. WHEN retrospective_simulation is called, THE Digital_Twin_Engine SHALL retrieve actual sensor data from that historical_date from mockData.ts
4. THE Digital_Twin_Engine SHALL recompute soil moisture starting from historical_date using the altered_parameter
5. THE Digital_Twin_Engine SHALL compare simulated_moisture against actual_measured_moisture from sensors
6. THE Digital_Twin_Engine SHALL return result object containing simulated_moisture, actual_moisture, difference_pct, and explanation fields
7. THE Digital_Twin_Engine SHALL calculate accuracy_score as (1 - |difference_pct| / 100) capped at 0-1 range

### Requirement 22: Retrospective UI Component

**User Story:** As an agronomist, I want a UI extension to the What-If Simulator that allows retrospective mode selection, so that I can easily compare what would have happened with different decisions.

#### Acceptance Criteria

1. THE Frontend_Application SHALL extend WhatIfSimulator.tsx with mode selector toggling between "prospective" and "retrospective"
2. WHEN "retrospective" mode is selected, THE Frontend_Application SHALL display date picker for selecting historical date within last 30 days
3. WHEN "retrospective" mode is selected, THE Frontend_Application SHALL display parameter selector for choosing which variable to alter (irrigation, temperature, humidity)
4. WHEN user clicks "Run Retrospective Simulation", THE Frontend_Application SHALL call retrospective_simulation and display results in comparison table
5. THE comparison table SHALL show columns: Parameter, Actual Decision, Alternative Decision, Predicted Outcome, Actual Outcome, Difference
6. THE Frontend_Application SHALL visualize difference using color gradient (green for <5% difference, yellow for 5-10%, red for >10%)
7. WHEN simulation completes, THE Frontend_Application SHALL display explanation text describing why the difference occurred

### Requirement 23: Sensor Quality Score Calculation

**User Story:** As a maintenance engineer, I want a quality score for each sensor based on reliability metrics, so that I can prioritize sensor maintenance and calibration.

#### Acceptance Criteria

1. THE Telemetry_System SHALL extend anomalyDetectionEngine.ts to track sensor quality metrics
2. THE Telemetry_System SHALL calculate valid_reading_pct as percentage of non-anomalous readings in last 7 days
3. THE Telemetry_System SHALL calculate noise_level as standard deviation of readings in last 7 days normalized to 0-100 scale
4. THE Telemetry_System SHALL track days_since_calibration for each sensor (simulated based on last known calibration date)
5. THE Quality_Score SHALL be calculated as: (0.50 × valid_reading_pct) + (0.30 × (100 - noise_level)) + (0.20 × calibration_freshness_score)
6. THE calibration_freshness_score SHALL be 100 if days_since_calibration < 30, linearly decreasing to 0 at 180 days
7. THE Telemetry_System SHALL update Quality_Score for each sensor every 4 hours
8. THE Telemetry_System SHALL store Quality_Score with timestamp in sensor metadata object

### Requirement 24: Sensor Quality Display

**User Story:** As a maintenance engineer, I want to see sensor quality scores in the telemetry dashboard, so that I can identify problematic sensors at a glance.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create new section in TelemetryAnalytics.tsx titled "Sensor Health Dashboard"
2. THE Sensor Health Dashboard SHALL display all sensors grouped by zone with Quality_Score for each
3. WHEN Quality_Score is 80-100, THE Frontend_Application SHALL display score with green background
4. WHEN Quality_Score is 60-79, THE Frontend_Application SHALL display score with yellow background
5. WHEN Quality_Score is below 60, THE Frontend_Application SHALL display score with red background and warning icon
6. WHEN user clicks on a sensor, THE Frontend_Application SHALL display detailed breakdown showing valid_reading_pct, noise_level, and days_since_calibration
7. THE Frontend_Application SHALL sort sensors by Quality_Score with lowest scores at top for visibility
8. THE Frontend_Application SHALL display timestamp of last Quality_Score update

### Requirement 25: Sensor Quality Alerting

**User Story:** As a maintenance engineer, I want to receive alerts when sensor quality drops below acceptable thresholds, so that I can address issues before they impact decision quality.

#### Acceptance Criteria

1. WHEN Quality_Score drops below 60 for any sensor, THE Telemetry_System SHALL trigger alert event
2. THE Telemetry_System SHALL call Notification_Dispatcher with urgency "moderate" for quality scores 40-59
3. THE Telemetry_System SHALL call Notification_Dispatcher with urgency "critical" for quality scores below 40
4. THE generated message SHALL include sensor_id, zone_id, Quality_Score, and primary_issue (validity, noise, or calibration)
5. THE generated message SHALL recommend specific action (recalibrate, inspect wiring, replace sensor)
6. THE Notification_Dispatcher SHALL route sensor quality alerts to email for "critical" and dashboard only for "moderate"

### Requirement 26: Phase Priority Documentation

**User Story:** As a project manager, I want clear documentation of phase priorities and time estimates, so that I can allocate resources effectively and meet Engineer Ticona's review requirements.

#### Acceptance Criteria

1. THE VRI_System SHALL include file docs/IMPLEMENTATION_PHASES.md documenting all 4 phases
2. THE documentation SHALL clearly label Phases 1-3 as "non-negotiable" for Engineer Ticona review
3. THE documentation SHALL label Phase 4 features as "optional differentiators" that can be reduced if time-limited
4. THE documentation SHALL provide time estimates: Phase 1 (1-2 days), Phase 2 (1 day), Phase 3 (1 day), Phase 4a (3-4 hours), Phase 4b (4-6 hours), Phase 4c (3-4 hours)
5. THE documentation SHALL state recommended priority order for Phase 4 features: 4a (crop calendar) first, then 4c (sensor quality), then 4b (retrospective mode)
6. THE documentation SHALL note that public dataset is being handled by separate team member
7. THE documentation SHALL include ready criteria for each phase defining what "complete" means

### Requirement 27: System Integration and Testing

**User Story:** As a QA engineer, I want comprehensive integration tests covering all four phases, so that I can verify the system works end-to-end before Engineer Ticona's review.

#### Acceptance Criteria

1. THE VRI_System SHALL include test suite verifying Phase 1: RAG returns correct answers with sources for 5 test questions
2. THE VRI_System SHALL include test suite verifying Phase 2: All 3 LangFlow flows are exported and screenshots are captured
3. THE VRI_System SHALL include test suite verifying Phase 3: Alert processing returns correct urgency and messages for 3 test scenarios
4. THE VRI_System SHALL include test suite verifying Phase 4a: Phenological stage calculation returns correct Kc for different date ranges
5. THE VRI_System SHALL include test suite verifying Phase 4b: Retrospective simulation calculates difference between predicted and actual outcomes
6. THE VRI_System SHALL include test suite verifying Phase 4c: Quality_Score is calculated correctly and color-coded in UI
7. WHEN all test suites pass, THE VRI_System SHALL be considered ready for demonstration to Engineer Ticona

### Requirement 28: Public Dataset Coordination

**User Story:** As a team coordinator, I want to ensure the public dataset work is tracked separately, so that there is no duplication of effort with the team member already assigned.

#### Acceptance Criteria

1. THE VRI_System requirements SHALL explicitly note that public dataset creation is handled by separate team member
2. THE Backend_Service SHALL reserve endpoint GET /api/v1/dataset/metadata for future dataset integration
3. THE Backend_Service SHALL reserve endpoint GET /api/v1/dataset/export for future dataset download capability
4. THE documentation SHALL include placeholder section for dataset documentation to be filled by assigned team member
5. THE integration testing SHALL include verification that dataset endpoints return appropriate "not yet implemented" responses

### Requirement 29: LangChain and LangFlow Documentation

**User Story:** As Engineer Ticona, I want comprehensive documentation of LangChain and LangFlow implementations, so that I can evaluate the technical approach and verify requirements are met.

#### Acceptance Criteria

1. THE VRI_System SHALL include file docs/LANGCHAIN_IMPLEMENTATION.md documenting RAG architecture, vectorstore configuration, and endpoint specifications
2. THE VRI_System SHALL include file docs/LANGFLOW_WORKFLOWS.md with embedded screenshots and descriptions of all three visual flows
3. THE documentation SHALL explain how knowledge base is structured and how to add new documents
4. THE documentation SHALL provide example curl commands for testing /api/v1/chat endpoint with sample questions
5. THE documentation SHALL explain fallback behavior when Backend_Service is unavailable
6. THE documentation SHALL include architecture diagrams showing data flow from user question through RAG_Service to response with sources

### Requirement 30: Performance and Scalability Considerations

**User Story:** As a system architect, I want the RAG and notification systems to perform efficiently under realistic load, so that the system remains responsive during operation.

#### Acceptance Criteria

1. WHEN Backend_Service receives 10 concurrent /api/v1/chat requests, THE RAG_Service SHALL respond to all within 10 seconds total
2. THE RAG_Service SHALL cache vectorstore in memory to avoid disk I/O on every request
3. THE Notification_Dispatcher SHALL process alerts asynchronously to avoid blocking the API request thread
4. WHEN Knowledge_Base contains 50+ markdown documents, THE RAG_Service SHALL still return results within 5 seconds
5. THE Backend_Service SHALL implement request timeout of 30 seconds for LLM API calls to prevent hanging
6. THE Backend_Service SHALL log performance metrics for RAG queries including retrieval_time_ms and generation_time_ms
