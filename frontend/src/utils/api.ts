import axios from "axios";

axios.defaults.baseURL = import.meta.env.VITE_API_URL as string;

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL as string,
  headers: {
    "Content-Type": "application/json; charset=UTF-8",
  },
});

export default api;

export const validateToken = async (token: string) => {
  try {
    const response = await api.post("/verify_token", {
      token,
    });
    return response.data;
  } catch (err) {
    return false;
  }
};
