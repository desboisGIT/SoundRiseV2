// src/api/auth.js
import axios from "axios";
import { useAuth } from "../components/context/AuthContext";
// For Vite, environment variables should be prefixed with VITE_
// e.g., in your .env file: VITE_API_URL=http://127.0.0.1:8000/api/auth
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/auth";

export const login = async (email, password) => {
  const response = await axios.post(`${API_URL}/login/`, { email, password }, { withCredentials: true });
  return response.data;
};

export const register = async (username, email, password) => {
  const response = await axios.post(`${API_URL}/register/`, { username, email, password });
  return response.data;
};

const LOGOUT_URL = "http://127.0.0.1:8000/api/auth/logout/";

/**
 * Logs out the user by calling the backend logout endpoint.
 * This function sends the request with credentials so that the refresh token cookie is included.
 * It then clears local storage and axios defaults.
 *
 * @returns {Promise<Object>} The response data from the API.
 */
export const logout = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.post(
      LOGOUT_URL,
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      }
    );
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete axios.defaults.headers.common["Authorization"];
    return response.data;
  } catch (error) {
    console.error("Logout error:", error);
    throw error;
  }
};

export default logout;
