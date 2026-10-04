/**
 * Phenology Service - Frontend API Client
 * Connects to LangChain-powered phenology endpoints
 */

import { apiClient } from './apiClient';

export interface PhenologicalStage {
  zone_id: string;
  crop_name: string;
  current_stage: string;
  stage_name: string;
  days_since_planting: number;
  days_to_flowering: number;
  days_to_harvest: number;
  kc: number;
  gdd?: number;
  progress_pct: number;
  planting_date: string;
  flowering_date: string;
  harvest_date: string;
}

export interface AIPhenologyAnalysis {
  phenology: PhenologicalStage;
  ai_reasoning: string;
  timestamp: string;
}

export interface IrrigationRecommendation {
  zone_id: string;
  recommended_mm: number;
  reasoning: string;
  confidence: number;
  risk_factors: string[];
  optimization_tips: string[];
}

export interface AgentTool {
  name: string;
  description: string;
}

class PhenologyService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = '/api/v1/crop-calendar';
  }

  /**
   * Get basic phenology for all zones or specific zone
   */
  async getCalendar(zoneId?: string): Promise<PhenologicalStage[]> {
    const url = zoneId 
      ? `${this.baseUrl}/calendar?zone_id=${zoneId}`
      : `${this.baseUrl}/calendar`;
    
    const response = await fetch(apiClient.getFullUrl(url));
    if (!response.ok) {
      throw new Error(`Failed to fetch calendar: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get phenology for specific zone
   */
  async getZonePhenology(zoneId: string): Promise<PhenologicalStage> {
    const response = await fetch(
      apiClient.getFullUrl(`${this.baseUrl}/calendar/${zoneId}`)
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch phenology for ${zoneId}: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get Kc value for zone
   */
  async getZoneKc(zoneId: string): Promise<{
    zone_id: string;
    kc: number;
    stage: string;
    stage_name: string;
    crop: string;
  }> {
    const response = await fetch(
      apiClient.getFullUrl(`${this.baseUrl}/kc/${zoneId}`)
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch Kc for ${zoneId}: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * 🤖 AI-Powered Phenology Analysis with LangChain Agent
   * Uses ReAct agent with multiple tools for comprehensive analysis
   */
  async getAIPhenologyAnalysis(zoneId: string): Promise<{
    success: boolean;
    data: AIPhenologyAnalysis;
    agent_type: string;
    model: string;
  }> {
    const response = await fetch(
      apiClient.getFullUrl(`${this.baseUrl}/ai/phenology/${zoneId}`)
    );
    if (!response.ok) {
      throw new Error(`AI analysis failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * 🚀 AI-Generated Irrigation Recommendation
   * Uses LangChain LLM Chain for precise recommendations
   */
  async getAIIrrigationRecommendation(
    zoneId: string,
    currentMoisture: number,
    et0: number = 5.5,
    rainForecast: number = 0
  ): Promise<{
    success: boolean;
    recommendation: IrrigationRecommendation;
    method: string;
  }> {
    const params = new URLSearchParams({
      current_moisture: currentMoisture.toString(),
      et0: et0.toString(),
      rain_forecast: rainForecast.toString()
    });

    const response = await fetch(
      apiClient.getFullUrl(`${this.baseUrl}/ai/irrigation-recommendation/${zoneId}?${params}`)
    );
    if (!response.ok) {
      throw new Error(`AI recommendation failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * List available LangChain agent tools
   */
  async listAgentTools(): Promise<{
    total_tools: number;
    tools: AgentTool[];
  }> {
    const response = await fetch(
      apiClient.getFullUrl(`${this.baseUrl}/ai/tools`)
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch tools: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Calculate dynamic Kc based on current phenological stage
   * This replaces hardcoded Kc values in digitalTwinEngine
   */
  async getDynamicKcForZone(zoneId: string): Promise<number> {
    try {
      const data = await this.getZoneKc(zoneId);
      return data.kc;
    } catch (error) {
      console.warn(`Failed to fetch dynamic Kc for ${zoneId}, using fallback`, error);
      return 1.15; // Fallback value
    }
  }

  /**
   * Get enhanced phenology data for map visualization
   */
  async getMapVisualizationData(): Promise<Map<string, PhenologicalStage>> {
    const allStages = await this.getCalendar();
    const map = new Map<string, PhenologicalStage>();
    
    allStages.forEach(stage => {
      map.set(stage.zone_id, stage);
    });
    
    return map;
  }
}

// Singleton instance
export const phenologyService = new PhenologyService();

// Export convenience functions
export const getPhenologyForZone = (zoneId: string) => 
  phenologyService.getZonePhenology(zoneId);

export const getAIPhenologyAnalysis = (zoneId: string) => 
  phenologyService.getAIPhenologyAnalysis(zoneId);

export const getAIIrrigationRecommendation = (
  zoneId: string,
  moisture: number,
  et0?: number,
  rain?: number
) => phenologyService.getAIIrrigationRecommendation(zoneId, moisture, et0, rain);

export const getDynamicKc = (zoneId: string) => 
  phenologyService.getDynamicKcForZone(zoneId);
