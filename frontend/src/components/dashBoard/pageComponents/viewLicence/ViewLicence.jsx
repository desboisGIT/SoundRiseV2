import React, { useState, useEffect } from "react";
import "./ViewLicence.css";
import LicenseCard from "../../../beats/licenses/LicenseCard";
import { getLicenseList } from "../../../../api/licence";

export default function ViewLicence({ onEdit, onDelete, refreshLicenses }) {
  const [licenses, setLicenses] = useState([]);

  useEffect(() => {
    const fetchLicenses = async () => {
      try {
        const result = await getLicenseList();
        console.log("Raw API Response:", result);
        if (Array.isArray(result)) {
          setLicenses(result);
        }
      } catch (error) {
        console.error("Error fetching licenses:", error);
      }
    };

    fetchLicenses();
  }, [refreshLicenses]); // re-fetch licenses whenever refreshLicenses changes

  return (
    <div className="dashboard-licence">
      <h1>Mes Licences:</h1>
      {licenses.length > 0 ? (
        licenses.map((license) => (
          <LicenseCard
            key={license.id}
            license={license}
            title={license.title || "No Title"}
            description={license.description || "No description available"}
            price={license.price || "0.00"}
            files={license.license_file_types || []} // Always an array
            conditions={license.conditions || []} // Always an array
            onEdit={() => onEdit(license)}
            onDelete={() => onDelete(license)}
          />
        ))
      ) : (
        <p>Aucune licence trouvée.</p>
      )}
    </div>
  );
}
