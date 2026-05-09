/**
 * MAMA-LENS AI — API Client
 * Axios instance with auth interceptors and error handling
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../store/authStore";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor — attach auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const { refreshToken, setTokens, logout } = useAuthStore.getState();

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          setTokens(access_token, refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch {
          logout();
          window.location.href = "/login";
        }
      } else {
        logout();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// ─── API Functions ────────────────────────────────────────────────────────────

export const authAPI = {
  register: (data: object) => apiClient.post("/auth/register", data),
  login: (data: object) => apiClient.post("/auth/login", data),
  verifyOTP: (data: object) => apiClient.post("/auth/verify-otp", data),
  requestOTP: (identifier: string) => apiClient.post(`/auth/request-otp?identifier=${identifier}`),
  logout: () => apiClient.post("/auth/logout"),
};

export const userAPI = {
  getProfile: () => apiClient.get("/users/me"),
  updateProfile: (data: object) => apiClient.put("/users/me", data),
};

export const riskAPI = {
  assess: (data: object) => apiClient.post("/risk/assess", data),
  getHistory: (limit?: number) => apiClient.get(`/risk/history?limit=${limit || 10}`),
  getAssessment: (id: string) => apiClient.get(`/risk/${id}`),
  symptomCheck: (symptoms: string[], gestationalAge: number, language?: string) =>
    apiClient.post(`/risk/symptom-check?gestational_age_weeks=${gestationalAge}&language=${language || "en"}`, symptoms),
};

export const pregnancyAPI = {
  create: (data: object) => apiClient.post("/pregnancy/", data),
  getActive: () => apiClient.get("/pregnancy/active"),
};

export const telemedicineAPI = {
  start: (data: object) => apiClient.post("/telemedicine/start", data),
  join: (id: string) => apiClient.post(`/telemedicine/${id}/join`),
  end: (id: string) => apiClient.post(`/telemedicine/${id}/end`),
  updateNotes: (id: string, data: object) => apiClient.put(`/telemedicine/${id}/notes`, data),
  submitFeedback: (id: string, data: object) => apiClient.post(`/telemedicine/${id}/feedback`, data),
  getHistory: () => apiClient.get("/telemedicine/history"),
};

export const facilitiesAPI = {
  findNearby: (lat: number, lng: number, params?: object) =>
    apiClient.get(`/facilities/nearby?latitude=${lat}&longitude=${lng}`, { params }),
  findEmergency: (lat: number, lng: number) =>
    apiClient.get(`/facilities/emergency-nearest?latitude=${lat}&longitude=${lng}`),
  getById: (id: string) => apiClient.get(`/facilities/${id}`),
};

export const avatarAPI = {
  chat: (data: object) => apiClient.post("/avatar/chat", data),
  transcribe: (formData: FormData) =>
    apiClient.post("/avatar/transcribe", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  getRealtimeToken: () => apiClient.get("/avatar/realtime-token"),
};

export const educationAPI = {
  getWeekly: (week: number, language?: string) =>
    apiClient.get(`/education/weekly/${week}?language=${language || "en"}`),
  getRecommendations: (gestationalAge: number, riskLevel?: string, language?: string) =>
    apiClient.get(`/education/recommendations?gestational_age_weeks=${gestationalAge}&risk_level=${riskLevel || "low"}&language=${language || "en"}`),
  getDangerSigns: (language?: string) =>
    apiClient.get(`/education/danger-signs?language=${language || "en"}`),
};

export const notificationsAPI = {
  getAll: (unreadOnly?: boolean) =>
    apiClient.get(`/notifications/?unread_only=${unreadOnly || false}`),
  markRead: (id: string) => apiClient.post(`/notifications/${id}/read`),
};

export const healthRecordsAPI = {
  getAll: () => apiClient.get("/health-records/"),
  logVitals: (data: object) => apiClient.post("/health-records/vitals", data),
};
