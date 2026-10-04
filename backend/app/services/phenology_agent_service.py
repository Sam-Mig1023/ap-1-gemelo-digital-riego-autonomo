"""
LangChain Phenology Agent Service
Advanced crop phenological stage reasoning with RAG integration
Uses LangChain Agents, Tools, and Chains for intelligent recommendations
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import csv
import os
from pathlib import Path

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool, StructuredTool
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from pydantic import BaseModel, Field

from .rag_service import get_rag_service


# Data Models
class PhenologyCalculation(BaseModel):
    """Calculated phenology data"""
    zone_id: str
    crop_name: str
    current_stage: str
    stage_name: str
    days_since_planting: int
    days_to_flowering: int
    days_to_harvest: int
    kc: float
    gdd: float = 0.0  # Growing Degree Days
    progress_pct: float
    planting_date: str
    flowering_date: str
    harvest_date: str


class IrrigationRecommendation(BaseModel):
    """AI-generated irrigation recommendation"""
    zone_id: str
    recommended_mm: float
    reasoning: str
    confidence: float
    risk_factors: List[str]
    optimization_tips: List[str]


# Kc values by phenological stage (FAO-56)
KC_DATABASE = {
    "Tomate": {
        "initial": {"kc": 0.60, "duration_days": 20, "description": "Emergencia y establecimiento"},
        "vegetative": {"kc": 0.90, "duration_days": 25, "description": "Desarrollo vegetativo rápido"},
        "flowering": {"kc": 1.15, "duration_days": 30, "description": "Floración y cuajado"},
        "yield_formation": {"kc": 1.20, "duration_days": 25, "description": "Formación y crecimiento de frutos"},
        "ripening": {"kc": 0.80, "duration_days": 20, "description": "Maduración y cosecha"}
    },
    "Calabacin": {
        "initial": {"kc": 0.50, "duration_days": 15, "description": "Germinación"},
        "vegetative": {"kc": 0.80, "duration_days": 20, "description": "Crecimiento vegetativo"},
        "flowering": {"kc": 0.95, "duration_days": 25, "description": "Floración continua"},
        "yield_formation": {"kc": 0.90, "duration_days": 15, "description": "Producción de frutos"},
        "ripening": {"kc": 0.75, "duration_days": 10, "description": "Madurez comercial"}
    },
    "Arandano": {
        "initial": {"kc": 0.50, "duration_days": 30, "description": "Brotación"},
        "vegetative": {"kc": 0.65, "duration_days": 60, "description": "Desarrollo foliar"},
        "flowering": {"kc": 0.95, "duration_days": 45, "description": "Floración y polinización"},
        "yield_formation": {"kc": 1.05, "duration_days": 60, "description": "Formación de bayas"},
        "ripening": {"kc": 0.85, "duration_days": 30, "description": "Maduración de frutos"}
    }
}


class PhenologyAgentService:
    """
    Advanced LangChain-based service for phenological reasoning
    Combines traditional calculations with AI-powered recommendations
    """
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        groq_model: str = "llama-3.3-70b-versatile"
    ):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model
        self.csv_path = Path("backend/data/crop_calendar.csv")
        
        # Initialize LLM
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name=self.groq_model,
            temperature=0.2,
            max_tokens=2048
        )
        
        # Initialize RAG service for knowledge retrieval
        self.rag_service = get_rag_service()
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        print("[✓] PhenologyAgentService initialized with LangChain")
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools for the agent"""
        
        def calculate_phenology_tool(zone_id: str) -> str:
            """Calculate current phenological stage for a zone"""
            try:
                result = self._calculate_phenology_raw(zone_id)
                return f"""
                Zone: {result.zone_id}
                Crop: {result.crop_name}
                Stage: {result.stage_name} ({result.current_stage})
                Kc: {result.kc}
                Days since planting: {result.days_since_planting}
                Days to flowering: {result.days_to_flowering}
                Days to harvest: {result.days_to_harvest}
                Progress: {result.progress_pct}%
                """
            except Exception as e:
                return f"Error calculating phenology: {str(e)}"
        
        def calculate_gdd_tool(zone_id: str, base_temp: float = 10.0) -> str:
            """Calculate Growing Degree Days (GDD) for thermal time"""
            try:
                result = self._calculate_phenology_raw(zone_id)
                # Mock GDD calculation (en producción vendría de datos reales)
                avg_temp = 22.0  # Temperatura promedio simulada
                gdd_per_day = max(0, avg_temp - base_temp)
                accumulated_gdd = gdd_per_day * result.days_since_planting
                return f"Accumulated GDD: {accumulated_gdd:.1f} °C-days (Base: {base_temp}°C)"
            except Exception as e:
                return f"Error calculating GDD: {str(e)}"
        
        def query_crop_knowledge_tool(question: str) -> str:
            """Query agronomic knowledge base using RAG"""
            try:
                if not self.rag_service._initialized:
                    self.rag_service.initialize()
                result = self.rag_service.query(question)
                return result["answer"]
            except Exception as e:
                return f"Error querying knowledge base: {str(e)}"
        
        def get_kc_recommendation_tool(crop_name: str, stage: str) -> str:
            """Get detailed Kc information for crop and stage"""
            crop_data = KC_DATABASE.get(crop_name, KC_DATABASE["Tomate"])
            stage_data = crop_data.get(stage, crop_data["initial"])
            return f"""
            Crop: {crop_name}
            Stage: {stage}
            Kc: {stage_data['kc']}
            Typical Duration: {stage_data['duration_days']} days
            Description: {stage_data['description']}
            """
        
        def calculate_water_requirement_tool(
            zone_id: str,
            et0: float = 5.5,
            rain_forecast: float = 0.0
        ) -> str:
            """Calculate water requirement based on Kc and ET0"""
            try:
                result = self._calculate_phenology_raw(zone_id)
                etc = result.kc * et0
                net_requirement = max(0, etc - rain_forecast)
                return f"""
                Zone: {zone_id}
                Kc: {result.kc}
                ET0: {et0} mm/day
                ETc: {etc:.2f} mm/day
                Rain forecast: {rain_forecast} mm
                Net water requirement: {net_requirement:.2f} mm/day
                """
            except Exception as e:
                return f"Error calculating water requirement: {str(e)}"
        
        return [
            Tool(
                name="CalculatePhenology",
                func=calculate_phenology_tool,
                description="Calculate current phenological stage, Kc, and progress for a management zone. Input: zone_id (e.g., 'zone-1-nw')"
            ),
            Tool(
                name="CalculateGDD",
                func=calculate_gdd_tool,
                description="Calculate accumulated Growing Degree Days for thermal time tracking. Input: zone_id"
            ),
            Tool(
                name="QueryCropKnowledge",
                func=query_crop_knowledge_tool,
                description="Query agronomic knowledge base for crop-specific information using RAG. Input: question in natural language"
            ),
            Tool(
                name="GetKcRecommendation",
                func=get_kc_recommendation_tool,
                description="Get detailed Kc coefficient information for a crop and phenological stage. Input format: 'crop_name,stage' (e.g., 'Tomate,flowering')"
            ),
            Tool(
                name="CalculateWaterRequirement",
                func=calculate_water_requirement_tool,
                description="Calculate daily water requirement based on phenology. Input: zone_id"
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create ReAct agent with tools"""
        
        prompt = PromptTemplate.from_template("""Eres un agrónomo experto especializado en fenología de cultivos y riego de precisión.

Tienes acceso a las siguientes herramientas:
{tools}

Nombres de herramientas: {tool_names}

Usa el siguiente formato:

Question: la pregunta o tarea que debes responder
Thought: razona sobre qué hacer
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: el input para la acción
Observation: el resultado de la acción
... (este patrón Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: Ya tengo la respuesta final
Final Answer: la respuesta final al usuario

Pregunta: {input}

{agent_scratchpad}""")
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def _calculate_phenology_raw(self, zone_id: str) -> PhenologyCalculation:
        """Raw calculation of phenological stage"""
        # Load CSV data
        entries = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            entries = list(reader)
        
        # Find zone
        zone_data = next((e for e in entries if e['zona'] == zone_id), None)
        if not zone_data:
            raise ValueError(f"Zone {zone_id} not found in crop calendar")
        
        today = datetime.now()
        planting = datetime.fromisoformat(zone_data['fecha_siembra'])
        flowering = datetime.fromisoformat(zone_data['fecha_floracion_esperada'])
        harvest = datetime.fromisoformat(zone_data['fecha_cosecha'])
        
        days_since = (today - planting).days
        days_to_flowering = max(0, (flowering - today).days)
        days_to_harvest = max(0, (harvest - today).days)
        
        total_days = (harvest - planting).days
        progress_pct = min(100, max(0, (days_since / total_days) * 100))
        
        # Determine stage
        if progress_pct < 20:
            stage, stage_name = "initial", "Inicial"
        elif progress_pct < 40:
            stage, stage_name = "vegetative", "Vegetativo"
        elif progress_pct < 65:
            stage, stage_name = "flowering", "Floración"
        elif progress_pct < 85:
            stage, stage_name = "yield_formation", "Formación"
        else:
            stage, stage_name = "ripening", "Maduración"
        
        # Get Kc
        crop = zone_data['cultivo']
        kc_data = KC_DATABASE.get(crop, KC_DATABASE["Tomate"])
        kc = kc_data.get(stage, {"kc": 1.0})["kc"]
        
        return PhenologyCalculation(
            zone_id=zone_id,
            crop_name=crop,
            current_stage=stage,
            stage_name=stage_name,
            days_since_planting=days_since,
            days_to_flowering=days_to_flowering,
            days_to_harvest=days_to_harvest,
            kc=kc,
            progress_pct=round(progress_pct, 1),
            planting_date=zone_data['fecha_siembra'],
            flowering_date=zone_data['fecha_floracion_esperada'],
            harvest_date=zone_data['fecha_cosecha']
        )
    
    def get_phenology_with_reasoning(self, zone_id: str) -> Dict[str, Any]:
        """
        Get phenology with AI reasoning and recommendations
        """
        # Get raw calculation
        phenology = self._calculate_phenology_raw(zone_id)
        
        # Use agent for intelligent reasoning
        question = f"""
        Analiza la etapa fenológica de la zona {zone_id} y proporciona:
        1. Estado actual del cultivo y Kc
        2. Recomendaciones de riego específicas para esta etapa
        3. Factores críticos a monitorear
        4. Riesgos potenciales
        
        Usa todas las herramientas disponibles para dar una respuesta completa.
        """
        
        try:
            result = self.agent.invoke({"input": question})
            ai_reasoning = result.get("output", "No reasoning available")
        except Exception as e:
            ai_reasoning = f"Agent error: {str(e)}"
        
        return {
            "phenology": phenology.dict(),
            "ai_reasoning": ai_reasoning,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_irrigation_recommendation(
        self,
        zone_id: str,
        current_moisture: float,
        et0: float,
        rain_forecast: float = 0.0
    ) -> IrrigationRecommendation:
        """
        Generate AI-powered irrigation recommendation
        """
        phenology = self._calculate_phenology_raw(zone_id)
        
        # Create recommendation chain
        prompt = PromptTemplate(
            input_variables=["zone", "crop", "stage", "kc", "moisture", "et0", "rain"],
            template="""Como agrónomo experto, genera una recomendación de riego precisa.

Datos de entrada:
- Zona: {zone}
- Cultivo: {crop}
- Etapa fenológica: {stage}
- Coeficiente Kc: {kc}
- Humedad actual del suelo: {moisture}%
- ET0: {et0} mm/día
- Pronóstico de lluvia: {rain} mm

Calcula:
1. Lámina de riego recomendada (mm)
2. Razonamiento técnico
3. Nivel de confianza (0-1)
4. Factores de riesgo
5. Tips de optimización

Formato de respuesta (JSON):
{{
    "recommended_mm": <valor>,
    "reasoning": "<explicación>",
    "confidence": <0-1>,
    "risk_factors": ["factor1", "factor2"],
    "optimization_tips": ["tip1", "tip2"]
}}
"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        result = chain.run(
            zone=zone_id,
            crop=phenology.crop_name,
            stage=phenology.stage_name,
            kc=phenology.kc,
            moisture=current_moisture,
            et0=et0,
            rain=rain_forecast
        )
        
        # Parse result (simplified - en producción usar JSON parsing robusto)
        try:
            import json
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return IrrigationRecommendation(
                    zone_id=zone_id,
                    recommended_mm=data.get("recommended_mm", 0.0),
                    reasoning=data.get("reasoning", ""),
                    confidence=data.get("confidence", 0.0),
                    risk_factors=data.get("risk_factors", []),
                    optimization_tips=data.get("optimization_tips", [])
                )
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        # Fallback calculation
        etc = phenology.kc * et0
        net_requirement = max(0, etc - rain_forecast)
        
        return IrrigationRecommendation(
            zone_id=zone_id,
            recommended_mm=round(net_requirement, 2),
            reasoning=f"Cálculo basado en FAO-56: ETc = Kc ({phenology.kc}) × ET0 ({et0}) - Lluvia ({rain_forecast})",
            confidence=0.85,
            risk_factors=["Pronóstico de lluvia incierto"] if rain_forecast > 0 else [],
            optimization_tips=[
                f"Etapa {phenology.stage_name} requiere monitoreo frecuente",
                "Considerar aplicación fraccionada en suelos arenosos"
            ]
        )


# Singleton instance
_phenology_agent_instance: Optional[PhenologyAgentService] = None


def get_phenology_agent() -> PhenologyAgentService:
    """Get or create singleton instance"""
    global _phenology_agent_instance
    if _phenology_agent_instance is None:
        _phenology_agent_instance = PhenologyAgentService()
    return _phenology_agent_instance
