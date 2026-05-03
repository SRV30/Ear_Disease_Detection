import axios from "axios";
import { handle401WithRefresh, isTokenExpired } from "./authSession";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token && !isTokenExpired(token)) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      return handle401WithRefresh(err, api);
    }
    return Promise.reject(err);
  }
);

export default api;
