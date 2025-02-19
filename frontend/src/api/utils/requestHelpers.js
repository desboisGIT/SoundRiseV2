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

// Convert text and file data into FormData
export const convertToFormData = (draft, files) => {
  const formData = new FormData();

  // Append text fields
  for (const key in draft) {
    if (Array.isArray(draft[key])) {
      draft[key].forEach((value, index) => {
        formData.append(`${key}[${index}]`, value);
      });
    } else if (draft[key] !== null && draft[key] !== undefined) {
      formData.append(key, draft[key]);
    }
  }

  // Append files
  for (const fileKey in files) {
    if (files[fileKey]) {
      formData.append(fileKey, files[fileKey]); // Add only non-null files
    }
  }

  return formData;
};
