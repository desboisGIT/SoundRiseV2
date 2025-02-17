import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/beats/licenses";

// Helper function to retrieve the auth headers (adjust token retrieval as needed)
const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token"); // or use your preferred token store
  return {
    Authorization: `Bearer ${token}`,
  };
};

// 1. Create a License
export const createLicense = async (licenseData) => {
  try {
    const response = await axios.post(`${API_URL}/`, licenseData, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Error creating license:", error);
    throw error;
  }
};

// 2. Get Licenses of Logged-in User
export const getLicenseList = async () => {
  try {
    const response = await axios.get(`${API_URL}/user/`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching licenses:", error);
    throw error;
  }
};

// 3. Update a License
export const updateLicense = async (id, updatedData) => {
  try {
    const response = await axios.patch(`${API_URL}/${id}/`, updatedData, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Error updating license:", error);
    throw error;
  }
};

// 4. Delete a License
export const deleteLicense = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/${id}/`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    console.error("Error deleting license:", error);
    throw error;
  }
};
