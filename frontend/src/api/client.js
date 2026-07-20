import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ---- Auth ----
export const login = (email, password) => client.post("/auth/login", { email, password });
export const register = (data) => client.post("/auth/register", data);
export const getMe = () => client.get("/auth/me");

// ---- Roads ----
export const getRoads = () => client.get("/roads/");
export const createRoad = (data) => client.post("/roads/", data);
export const updateRoad = (id, data) => client.put(`/roads/${id}`, data);
export const deleteRoad = (id) => client.delete(`/roads/${id}`);

// ---- Traffic Data ----
export const getTrafficData = (params) => client.get("/traffic/", { params });
export const createTrafficData = (data) => client.post("/traffic/", data);
export const updateTrafficData = (id, data) => client.put(`/traffic/${id}`, data);
export const deleteTrafficData = (id) => client.delete(`/traffic/${id}`);
export const uploadTrafficCsv = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return client.post("/traffic/upload-csv", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
export const downloadTrafficCsv = (roadId) =>
  client.get("/traffic/export/download-csv", { params: { road_id: roadId }, responseType: "blob" });

// ---- Predictions ----
export const getPrediction = (trafficId) => client.get("/prediction/", { params: { traffic_id: trafficId } });
export const trainModel = () => client.post("/prediction/train");

// ---- Incidents ----
export const getIncidents = (limit = 50) => client.get("/incidents/", { params: { limit } });
export const createIncident = (data) => client.post("/incidents/", data);

// ---- Alerts ----
export const getAlerts = (limit = 50) => client.get("/alerts/", { params: { limit } });
export const generateAlert = (incidentId) => client.post("/alerts/generate", { incident_id: incidentId });
export const getScenario = (scenarioType) => client.get("/alerts/scenario", { params: { scenario_type: scenarioType } });
export const getScenarioTypes = () => client.get("/alerts/scenario/types");

// ---- Agent ----
export const getAgentLogs = (limit = 50) => client.get("/agent/", { params: { limit } });
export const runAgent = (roadId, trafficId, incidentId) =>
  client.post("/agent/run", null, { params: { road_id: roadId, traffic_id: trafficId, incident_id: incidentId } });

// ---- Reports ----
export const downloadReport = (type) =>
  client.get("/reports/", { params: { report_type: type }, responseType: "blob" });
export const getLstmForecast = (roadId) =>         
  client.get("/prediction/lstm-forecast", { params: { road_id: roadId } });
export default client;
