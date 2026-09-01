/**
 * API Client Service for FastAPI Backend
 * Provides typed HTTP client methods for all VRI Digital Twin API endpoints
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    body?: any
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);

      if (!response.ok) {
        const error = await response.text();
        return {
          error: `HTTP ${response.status}: ${error}`,
          status: response.status,
        };
      }

      const data = await response.json();
      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 0,
      };
    }
  }

  // Health & Status
  async getHealth() {
    return this.request('/health', 'GET');
  }

  async getReadiness() {
    return this.request('/ready', 'GET');
  }

  // Fields Endpoints
  async getFields() {
    return this.request('/api/v1/fields', 'GET');
  }

  async getField(fieldId: string) {
    return this.request(`/api/v1/fields/${fieldId}`, 'GET');
  }

  async getFieldZones(fieldId: string) {
    return this.request(`/api/v1/fields/${fieldId}/zones`, 'GET');
  }

  async getZone(fieldId: string, zoneId: string) {
    return this.request(`/api/v1/fields/${fieldId}/zones/${zoneId}`, 'GET');
  }

  // Sensors Endpoints
  async getSensors() {
    return this.request('/api/v1/sensors', 'GET');
  }

  async getSensor(sensorId: string) {
    return this.request(`/api/v1/sensors/${sensorId}`, 'GET');
  }

  async getZoneSensors(zoneId: string) {
    return this.request(`/api/v1/sensors/zone/${zoneId}`, 'GET');
  }

  async ingestTelemetry(data: any) {
    return this.request('/api/v1/sensors/telemetry/ingest', 'POST', data);
  }

  // RL Engine Endpoints
  async inferVRIRates(observation: any) {
    return this.request('/api/v1/rl-engine/infer-vri-rates', 'POST', observation);
  }

  async getDecisions(fieldId?: string, status?: string) {
    let endpoint = '/api/v1/rl-engine/decisions';
    const params = new URLSearchParams();
    if (fieldId) params.append('field_id', fieldId);
    if (status) params.append('status_filter', status);
    if (params.toString()) endpoint += `?${params.toString()}`;
    return this.request(endpoint, 'GET');
  }

  async approveDecision(decisionId: string, approvedBy: string) {
    return this.request(
      `/api/v1/rl-engine/decisions/${decisionId}/approve`,
      'POST',
      { approvedBy }
    );
  }

  async overrideDecision(decisionId: string, overrideData: any) {
    return this.request(
      `/api/v1/rl-engine/decisions/${decisionId}/override`,
      'POST',
      overrideData
    );
  }

  async retrainPolicy(trainingData: any) {
    return this.request('/api/v1/rl-engine/retrain-policy', 'POST', trainingData);
  }

  // Irrigation Control Endpoints
  async executeDecision(decision: any) {
    return this.request('/api/v1/irrigation/execute-decision', 'POST', decision);
  }

  async manualTrigger(triggerData: any) {
    return this.request('/api/v1/irrigation/manual-trigger', 'POST', triggerData);
  }

  async getIrrigationStatus(fieldId?: string) {
    let endpoint = '/api/v1/irrigation/status';
    if (fieldId) endpoint += `?field_id=${fieldId}`;
    return this.request(endpoint, 'GET');
  }

  async emergencyStop(fieldId: string) {
    return this.request('/api/v1/irrigation/emergency-stop', 'POST', { fieldId });
  }

  async getIrrigationSchedule(fieldId?: string) {
    let endpoint = '/api/v1/irrigation/schedule';
    if (fieldId) endpoint += `?field_id=${fieldId}`;
    return this.request(endpoint, 'GET');
  }

  // Reports Endpoints
  async generateReport(reportConfig: any) {
    return this.request('/api/v1/reports/generate', 'POST', reportConfig);
  }

  async getReportStatus(reportId: string) {
    return this.request(`/api/v1/reports/${reportId}/status`, 'GET');
  }

  async downloadReport(reportId: string) {
    return this.request(`/api/v1/reports/${reportId}/download`, 'GET');
  }

  async getReportHistory(fieldId?: string, limit: number = 20) {
    let endpoint = '/api/v1/reports/history';
    const params = new URLSearchParams();
    if (fieldId) params.append('field_id', fieldId);
    params.append('limit', limit.toString());
    if (params.toString()) endpoint += `?${params.toString()}`;
    return this.request(endpoint, 'GET');
  }

  async scheduleReport(scheduleConfig: any) {
    return this.request('/api/v1/reports/schedule', 'POST', scheduleConfig);
  }

  async exportWhatIfScenario(scenarioData: any) {
    return this.request('/api/v1/reports/what-if-export', 'POST', scenarioData);
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export class for testing
export { APIClient };
