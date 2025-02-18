import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/user/";
const REFRESH_URL = "http://127.0.0.1:8000/api/auth/refresh/";

/**
 * Custom request wrapper that retries a request after refreshing the token
 * if it receives a 401 error.
 *
 * @param {Function} requestFn - A function returning an Axios promise.
 * @returns {Promise} The resolved response from Axios.
 */
export const makeAuthenticatedRequest = async (requestFn) => {
  try {
    return await requestFn();
  } catch (error) {
    if (error.response?.status === 401) {
      console.warn("Access token expired, refreshing...");
      const newAccess = await refreshAccessToken();
      if (newAccess) {
        // Retry the request after refreshing the token.
        return await requestFn();
      }
    }
    throw error;
  }
};

// Fetch filtered users from the API.
export const fetchFilteredUsers = async (options = {}) => {
  const { fields = ["profile_picture", "username", "id"], limit = 50, offset = 0, username = "" } = options;

  const params = new URLSearchParams();
  params.append("fields", fields.join(","));
  params.append("limit", limit);
  params.append("offset", offset);
  if (username) {
    params.append("username", username);
  }

  const url = `http://127.0.0.1:8000/api/users/filter/?${params.toString()}`;

  try {
    const response = await makeAuthenticatedRequest(() => axios.get(url));
    return response.data;
  } catch (error) {
    console.error("Error fetching filtered users:", error);
    throw error;
  }
};

// Refresh access token using the HttpOnly cookie.
export const refreshAccessToken = async () => {
  try {
    const response = await axios.post(REFRESH_URL, {}, { withCredentials: true });
    console.log(response.data);
    localStorage.setItem("access_token", response.data.access);
    return response.data.access;
  } catch (error) {
    console.error("Failed to refresh token:", error);
    return null;
  }
};

// Get user info.
export const getUserInfo = async () => {
  const token = localStorage.getItem("access_token");
  try {
    const response = await makeAuthenticatedRequest(() =>
      axios.get(API_URL, {
        headers: { Authorization: `Bearer ${token}` },
      })
    );
    return response.data;
  } catch (error) {
    console.error("Not logged in:", error);
    return null;
  }
};

const API_URL_ISLOGGEDIN = "http://127.0.0.1:8000/api/user/?fields=is_online";
export const isLoggedIn = async () => {
  const token = localStorage.getItem("access_token");
  if (!token) return false;
  try {
    const response = await makeAuthenticatedRequest(() =>
      axios.get(API_URL_ISLOGGEDIN, {
        headers: { Authorization: `Bearer ${token}` },
      })
    );
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

const API_URL_LIST_LICENSE = "http://127.0.0.1:8000/api/beats/licenses/user/";
export const getLicenseList = async () => {
  const token = localStorage.getItem("access_token");
  if (!token) return [];
  try {
    const response = await makeAuthenticatedRequest(() =>
      axios.get(API_URL_LIST_LICENSE, {
        headers: { Authorization: `Bearer ${token}` },
      })
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching licenses:", error);
    return [];
  }
};

export default {
  makeAuthenticatedRequest,
  fetchFilteredUsers,
  refreshAccessToken,
  getUserInfo,
  isLoggedIn,
  getLicenseList,
};
