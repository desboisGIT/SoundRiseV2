// src/api/beats.js
import axios from "axios";
import { getAuthHeaders } from "./requestHelpers";
import { makeAuthenticatedRequest } from "./requestHelpers";

//############################################################
//                          drafts                          //
//############################################################
// Docs
// Urls:
//
//    Create Draft:
//    POST http://127.0.0.1:8000/api/beats/drafts/
//
//    Edit Draft:
//    PATCH http://127.0.0.1:8000/api/beats/drafts/:ID/
//
//    Delete Draft:
//    DELETE http://127.0.0.1:8000/api/beats/drafts/:ID/
//
//    Edit Draft:
//    PATCH http://127.0.0.1:8000/api/beats/drafts/:ID/
//
//    Draft --> Beat (Publish)
//    POST http://127.0.0.1:8000/api/beats/finalize-draft/:ID/
//
//    Get All Drafts From The Current User:
//    GET http://127.0.0.1:8000/api/beats/drafts/user

const API_URL = "http://127.0.0.1:8000/api/beats/";

// Create Draft: POST /drafts/
export const createDraft = async () => {
  const response = await makeAuthenticatedRequest(() =>
    axios.post(`${API_URL}drafts/`, {}, { headers: getAuthHeaders() })
  );
  return response.data;
};

// Edit Draft: PATCH /drafts/:ID/
export const editDraft = async (id, updatedData) => {
  const response = await makeAuthenticatedRequest(() =>
    axios.patch(`${API_URL}drafts/${id}/`, updatedData, { headers: getAuthHeaders() })
  );
  return response.data;
};

// Delete Draft: DELETE /drafts/:ID/
export const deleteDraft = async (id) => {
  const response = await makeAuthenticatedRequest(() =>
    axios.delete(`${API_URL}drafts/${id}/`, { headers: getAuthHeaders() })
  );
  return response.data;
};

// Publish Draft (Draft --> Beat): POST /finalize-draft/:ID/
export const finalizeDraft = async (id) => {
  const response = await makeAuthenticatedRequest(() =>
    axios.post(`${API_URL}finalize-draft/${id}/`, {}, { headers: getAuthHeaders() })
  );
  return response.data;
};

// Get All Drafts From The Current User: GET /drafts/user
export const getUserDrafts = async () => {
  const response = await makeAuthenticatedRequest(() =>
    axios.get(`${API_URL}drafts/user`, { headers: getAuthHeaders() })
  );
  return response.data;
};
