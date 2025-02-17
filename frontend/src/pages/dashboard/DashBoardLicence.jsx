import React, { useState } from "react";
import "./DashBoardLicence.css";
import ViewLicence from "../../components/dashBoard/pageComponents/viewLicence/ViewLicence";
import EditLicence from "../../components/dashBoard/pageComponents/editLicence/EditLicence";
import DefaultPopUp from "../../components/popups/DefaultPopUp";
import { createLicense, updateLicense, deleteLicense } from "../../api/licence";

export default function DashBoardLicence() {
  const [page, setPage] = useState("list");
  const [selectedLicense, setSelectedLicense] = useState(null);
  const [deletePopupVisible, setDeletePopupVisible] = useState(false);
  const [licenseToDelete, setLicenseToDelete] = useState(null);
  const [refreshLicenses, setRefreshLicenses] = useState(0);

  const handleSubmit = async (data) => {
    console.log("Submitted data:", data);
    try {
      let response;
      // If data includes an id, update the existing license; otherwise, create a new one.
      if (data.id) {
        response = await updateLicense(data.id, data);
      } else {
        response = await createLicense(data);
      }
      console.log("API Response:", response);
      // Refresh the list after creation/update.
      setRefreshLicenses((prev) => prev + 1);
      setPage("list");
    } catch (error) {
      console.error("Error submitting license:", error);
      // You could display an error message here.
    }
  };

  const handleEdit = (licenseData) => {
    setSelectedLicense(licenseData);
    setPage("edit");
  };

  const handleCreateNew = () => {
    setSelectedLicense(null); // Clear any previously selected license
    setPage("edit");
  };

  // Called when the user clicks the delete icon on a license card.
  const handleDeleteRequest = (licenseData) => {
    setLicenseToDelete(licenseData);
    setDeletePopupVisible(true);
  };

  // Called when the user confirms deletion in the popup.
  const confirmDelete = async () => {
    try {
      await deleteLicense(licenseToDelete.id);
      console.log("License deleted successfully");
      setDeletePopupVisible(false);
      setLicenseToDelete(null);
      // Trigger a refresh of the license list.
      setRefreshLicenses((prev) => prev + 1);
      setPage("list");
    } catch (error) {
      console.error("Error deleting license:", error);
    }
  };

  const cancelDelete = () => {
    setDeletePopupVisible(false);
    setLicenseToDelete(null);
  };

  return (
    <div className="dashboard-licence">
      <div className="button-group">
        <button onClick={() => setPage("list")}>View Licence</button>
        <button onClick={handleCreateNew}>Create Licence</button>
      </div>
      <div className="page-content">
        {page === "list" ? (
          <ViewLicence onEdit={handleEdit} onDelete={handleDeleteRequest} refreshLicenses={refreshLicenses} />
        ) : (
          <EditLicence handleSubmit={handleSubmit} defaultData={selectedLicense} />
        )}
      </div>

      {/* Delete Confirmation Popup */}
      <DefaultPopUp isDisplayed={deletePopupVisible} onClose={cancelDelete} className="delete-popup">
        <div className="delete-popup-content">
          <h2>Confirm Deletion</h2>
          <p>Are you sure you want to delete the license "{licenseToDelete?.title}"?</p>
          <div className="popup-buttons">
            <button onClick={confirmDelete}>Confirm</button>
            <button onClick={cancelDelete}>Cancel</button>
          </div>
        </div>
      </DefaultPopUp>
    </div>
  );
}
