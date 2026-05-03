import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000",
});

let isRefreshing = false;
let queue = [];
const processQueue = (token) => { queue.forEach((cb) => cb(token)); queue = []; };

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use((res) => res, async (error) => {
  const original = error.config;
  if (error.response?.status === 401 && !original?._retry) {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      localStorage.clear();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        queue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          resolve(api(original));
        });
      });
    }

    original._retry = true;
    isRefreshing = true;
    try {
      const res = await axios.post(`${api.defaults.baseURL}/refresh`, {}, { headers: { Authorization: `Bearer ${refreshToken}` } });
      const newToken = res.data.access_token;
      localStorage.setItem("access_token", newToken);
      processQueue(newToken);
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch (e) {
      localStorage.clear();
      window.location.href = "/login";
      return Promise.reject(e);
    } finally {
      isRefreshing = false;
    }
  }
  return Promise.reject(error);
});

export default api;
