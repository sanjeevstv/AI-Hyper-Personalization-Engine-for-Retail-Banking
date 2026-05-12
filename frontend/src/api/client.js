import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const seedData = () => api.post("/ingest/seed");

export const searchCustomers = (query = "", page = 1) =>
  api.get("/customers/", { params: { q: query, page, per_page: 20 } });

export const getCustomer = (id) => api.get(`/customers/${id}`);

export const getProfile = (id) => api.get(`/customers/${id}/profile`);

export const getLifeEvents = (id, mode = "") =>
  api.get(`/customers/${id}/life-events`, { params: mode ? { mode } : {} });

export const getSegment = (id) => api.get(`/customers/${id}/segment`);

export const getRecommendations = (id, mode = "") =>
  api.get(`/customers/${id}/recommendations`, { params: mode ? { mode } : {} });

export const generateMessage = (id, messageType = "email") =>
  api.post(`/customers/${id}/generate-message`, {
    message_type: messageType,
  });

export const computeProfiles = () => api.post("/customers/compute-profiles");

export const detectLifeEvents = () =>
  api.post("/customers/detect-life-events");

export const runSegmentation = () => api.post("/customers/run-segmentation");

export const getSegmentsOverview = () =>
  api.get("/customers/segments/overview");

export const getFilterOptions = () =>
  api.get("/customers/filter-options");

export const getFilteredCustomers = (filters = {}) =>
  api.get("/customers/filter", { params: filters });

export const exportCustomersCSV = (filters = {}) => {
  const params = new URLSearchParams(filters).toString();
  window.open(`/api/customers/export?${params}`, "_blank");
};

export default api;
