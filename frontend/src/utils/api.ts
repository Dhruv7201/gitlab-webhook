import axios from "axios";

axios.defaults.baseURL = import.meta.env.VITE_API_URL as string;

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL as string,
  headers: {
    'Content-Type': 'application/json; charset=UTF-8',
}
});

export default api;
