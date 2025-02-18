// src/api/requestHelpers.js
import axios from "axios";
import { refreshAccessToken } from "../user";

export const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token");
  return {
    Authorization: `Bearer ${token}`,
  };
};

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
