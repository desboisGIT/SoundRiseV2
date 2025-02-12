// src/api/auth.js
import axios from 'axios';

// For Vite, environment variables should be prefixed with VITE_
// e.g., in your .env file: VITE_API_URL=http://localhost:8000/api/auth
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/auth';

export const login = async (email, password) => {
  const response = await axios.post(`${API_URL}/login/`, { email, password });
  return response.data; // returns { refresh: "...", access: "..." }
};

export const register = async (username, email, password) => {
  const response = await axios.post(`${API_URL}/register/`, { username, email, password });
  return response.data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  delete axios.defaults.headers.common["Authorization"];
};


