import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/user/";
const REFRESH_URL = "http://127.0.0.1:8000/api/auth/token/refresh/";

/**
 * Fetch filtered users from the API.
 *
 * @param {Object} options - The options for filtering.
 * @param {string[]} [options.fields=["profile_picture", "username", "id"]] - The fields to include in the response.
 * @param {number} [options.limit=50] - The maximum number of users to return.
 * @param {number} [options.offset=0] - The offset for pagination.
 * @param {string} [options.username=""] - A username filter (optional).
 * @returns {Promise<Object>} The response data from the API.
 */
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
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error("Error fetching filtered users:", error);
    throw error;
  }
};

// Updated refreshAccessToken: relies on the HttpOnly cookie being sent automatically.
export const refreshAccessToken = async () => {
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
        return getUserInfo();
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
