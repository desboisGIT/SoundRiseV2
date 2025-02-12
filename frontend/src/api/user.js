import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/user/";
const REFRESH_URL = "http://127.0.0.1:8000/api/auth/token/refresh/";

const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      console.error("No refresh token available.");
      return null;
    }

    const response = await axios.post(REFRESH_URL, {
      refresh: refreshToken,
    });

    localStorage.setItem("access_token", response.data.access);
    return response.data.access;
  } catch (error) {
    console.error("Failed to refresh token:", error);
    return null;
  }
};

export const getUserInfo = async () => {
  let accessToken = localStorage.getItem("access_token");

  try {
    const response = await axios.get(API_URL, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      console.warn("Access token expired, trying to refresh...");
      accessToken = await refreshAccessToken();
      if (accessToken) {
        return getUserInfo(); // Retry the request with the new token
      }
    }
    console.error("Not logged in:", error);
    return null;
  }
};
