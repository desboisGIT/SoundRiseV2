// src/api/beats.js
import axios from "axios";
import { getAuthHeaders, makeAuthenticatedRequest, convertToFormData } from "./utils/requestHelpers";

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
export const createDraft = async (draftData) => {
  return await makeAuthenticatedRequest(() => axios.post(`${API_URL}drafts/`, draftData, { headers: getAuthHeaders() })).then(
    (response) => response.data
  );
};

// Upload Files To Draft: PATCH /drafts/:ID/
export const uploadFilesToDraft = async (draftId, files) => {
  const formData = new FormData();

  // Append only files that are not null
  Object.entries(files).forEach(([key, file]) => {
    if (file) {
      formData.append(key, file);
    }
  });

  return await makeAuthenticatedRequest(() =>
    axios.patch(`${API_URL}drafts/${draftId}/`, formData, {
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "multipart/form-data",
      },
    })
  );
};

// Edit Draft: PATCH /drafts/:ID/
export const editDraft = async (draftId, draftData) => {
  return await makeAuthenticatedRequest(() => axios.patch(`${API_URL}drafts/${draftId}/`, draftData, { headers: getAuthHeaders() })).then(
    (response) => response.data
  );
};

// Delete Draft: DELETE /drafts/:ID/
export const deleteDraft = async (id) => {
  const response = await makeAuthenticatedRequest(() => axios.delete(`${API_URL}drafts/${id}/`, { headers: getAuthHeaders() }));
  return response.data;
};

// Publish Draft (Draft --> Beat): POST /finalize-draft/:ID/
export const finalizeDraft = async (id) => {
  const response = await makeAuthenticatedRequest(() => axios.post(`${API_URL}finalize-draft/${id}/`, {}, { headers: getAuthHeaders() }));
  return response.data;
};

// Get All Drafts From The Current User: GET /drafts/user
export const getUserDrafts = async () => {
  const response = await makeAuthenticatedRequest(() => axios.get(`${API_URL}drafts/user`, { headers: getAuthHeaders() }));
  return response.data;
};

//############################################################
//                          tracks                          //
//############################################################
// Docs
// Urls:
//
//    Create Track:
//    POST http://127.0.0.1:8000/api/beats/tracks/
//
//    Get All Tracks From The Current User:
//    GET http://127.0.0.1:8000/api/beats/tracks/user/
//
//    Get Track :id From The Current User:
//    DELETE http://127.0.0.1:8000/api/beats/tracks/:ID/

// Create Track: POST /tracks/
export const createTrack = async (trackData) => {
  const response = await makeAuthenticatedRequest(() => axios.post(`${API_URL}tracks/`, trackData, { headers: getAuthHeaders() }));
  return response.data;
};
