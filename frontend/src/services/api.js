import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const healthCheck = () => api.get('/health');

export const predictFlareVolume = (data) => api.post('/predict/flare-volume', data);
export const predictEmissions = (data) => api.post('/predict/emissions', data);
export const predictRisk = (data) => api.post('/predict/risk', data);

export const getEmissionReport = (params) => api.get('/emission/report', { params });
export const getFacilityDetail = (id) => api.get(`/facility/${id}`);
export const getComplianceStatus = (facilityId) =>
  api.get('/compliance/status', { params: { facility_id: facilityId } });
export const getExplanation = (data) => api.post('/explain/emission', data);

export default api;
