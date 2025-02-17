import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/user/";
const REFRESH_URL = "http://127.0.0.1:8000/api/auth/token/refresh/";

// Updated refreshAccessToken: relies on the HttpOnly cookie being sent automatically.
const refreshAccessToken = async () => {
  try {
    // We don't need to pass the refresh token manually – the cookie is sent automatically.
    const response = await axios.post(REFRESH_URL, {}, { withCredentials: true });
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
        return getUserInfo(); // Retry with new access token
      }
    }
    console.error("Not logged in:", error);
    return null;
  }
};

const API_URL_ISLOGGEDIN = "http://127.0.0.1:8000/api/user/?fields=is_online";
export const isLoggedIn = async () => {
  const accessToken = localStorage.getItem("access_token");
  if (!accessToken) return false;

  try {
    const response = await axios.get(API_URL_ISLOGGEDIN, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

const API_URL_LIST_LICENSE = "http://127.0.0.1:8000/api/beats/licenses/user/";
export const getLicenseList = async () => {
  const accessToken = localStorage.getItem("access_token");
  if (!accessToken) return [];

  try {
    const response = await axios.get(API_URL_LIST_LICENSE, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching licenses:", error);
    return [];
  }
};
