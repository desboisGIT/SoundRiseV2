import React, { useState, useEffect } from "react";
import { useAuth } from "../../../components/context/AuthContext";
import CollaborationDropDown from "../../../components/dashBoard/pageComponents/collaborationDropDown/CollaborationDropDown";
import { getLicenseList } from "../../../api/licence";
import { createDraft, uploadFilesToDraft, editDraft, finalizeDraft } from "../../../api/beats";
import LicenseCard from "../../../components/beats/licenses/LicenseCard";
import { useNavigate } from "react-router-dom";

export default function DashBoardCreateBeats() {
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [licenses, setLicenses] = useState([]);
  const [selectedLicenseFiles, setSelectedLicenseFiles] = useState([]);
  const [currentDraftId, setCurrentDraftId] = useState(null);
  const navigate = useNavigate();

  const [draft, setDraft] = useState({
    title: "",
    bpm: "",
    key: "",
    genre: "",
    licenses: [],
    co_artists: [],
    user: user ? user.id : null,
  });

  const [files, setFiles] = useState({
    cover_image: null,
    mp3: null,
    wav: null,
    flac: null,
    ogg: null,
    aac: null,
    alac: null,
    zip: null,
  });

  useEffect(() => {
    const fetchLicenses = async () => {
      try {
        const result = await getLicenseList();
        if (Array.isArray(result)) {
          setLicenses(result);
        }
      } catch (error) {
        console.error("Error fetching licenses:", error);
      }
    };

    fetchLicenses();
  }, []);

  const handleDraftChange = (e) => {
    const { name, value } = e.target;
    setDraft((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFiles({ ...files, [e.target.name]: e.target.files[0] });
  };

  const handleLicenseSelect = (selectedLicense) => {
    setDraft((prev) => {
      const isSelected = prev.licenses.includes(selectedLicense.id);
      const newLicenses = isSelected
        ? prev.licenses.filter((id) => id !== selectedLicense.id) // Remove
        : [...prev.licenses, selectedLicense.id]; // Add

      const newFiles = licenses.filter((lic) => newLicenses.includes(lic.id)).flatMap((lic) => lic.license_file_types || []);

      setSelectedLicenseFiles([...new Set(newFiles)]);

      return { ...prev, licenses: newLicenses };
    });
  };

  const handleSaveDraft = async () => {
    try {
      const draftData = {
        user: draft.user,
        title: draft.title,
        bpm: draft.bpm,
        key: draft.key,
        genre: draft.genre,
        co_artists: draft.co_artists,
        licenses: draft.licenses,
      };

      let draftId = currentDraftId; // Store the draft ID in a local variable

      if (draftId) {
        // If draft exists, update it
        console.log(`Modifying existing draft ID: ${draftId}`);
        await editDraft(draftId, draftData);
        console.log("Draft updated successfully!");
      } else {
        // Otherwise, create a new draft
        console.log("No existing draft found. Creating a new one...");
        const createdDraft = await createDraft(draftData);
        console.log("Draft created:", createdDraft);
        draftId = createdDraft.id; // Assign the new draft ID
        setCurrentDraftId(draftId);
      }

      // Step 2: Upload the files (PATCH request)
      if (draftId) {
        await uploadFilesToDraft(draftId, files);
        console.log("Files uploaded successfully!");
      } else {
        console.error("Error: No draft ID available for file upload.");
      }
    } catch (error) {
      console.error("Error saving draft:", error);
    }
  };

  const handleUpload = async () => {
    try {
      if (!currentDraftId) {
        console.error("Error: No draft ID found, cannot finalize.");
        return;
      }

      console.log(`Finalizing draft ID: ${currentDraftId}`);
      await finalizeDraft(currentDraftId);
      console.log("Draft finalized successfully!");

      setStep(6); // Move to success step
    } catch (error) {
      console.error("Error finalizing draft:", error);
    }
  };

  const nextStep = () => {
    setStep((prev) => prev + 1);
    handleSaveDraft();
  };
  const prevStep = () => setStep((prev) => prev - 1);

  return (
    <div>
      {/* STEP 1 */}
      {step === 1 && (
        <div className="step-1">
          <h2>Step 1 - Beat Information</h2>
          <input type="text" name="title" placeholder="Title" value={draft.title} onChange={handleDraftChange} />
          <input type="number" name="bpm" placeholder="BPM" value={draft.bpm} onChange={handleDraftChange} />
          <input type="text" name="key" placeholder="Key" value={draft.key} onChange={handleDraftChange} />
          <input type="text" name="genre" placeholder="Genre" value={draft.genre} onChange={handleDraftChange} />
          <input type="file" name="cover_image" onChange={handleFileChange} />
          <CollaborationDropDown
            isActive={true}
            onUserSelect={(user) => {
              setDraft((prev) => ({
                ...prev,
                co_artists: prev.co_artists.includes(user.id) ? prev.co_artists.filter((id) => id !== user.id) : [...prev.co_artists, user.id],
              }));
            }}
            selectedUserIds={draft.co_artists}
          />
          <button onClick={nextStep}>Next</button>
        </div>
      )}

      {/* STEP 2 */}
      {step === 2 && (
        <div className="step-2">
          <h2>Step 2 - Select Licenses</h2>
          {licenses.length > 0 ? (
            licenses.map((license) => (
              <LicenseCard
                key={license.id}
                license={license}
                title={license.title || "No Title"}
                description={license.description || "No description available"}
                price={license.price || "0.00"}
                files={license.license_file_types || []}
                conditions={license.conditions || []}
                onUserSelect={() => handleLicenseSelect(license)}
                active={draft.licenses.includes(license.id)}
              />
            ))
          ) : (
            <p>No licenses found.</p>
          )}
          <button onClick={prevStep}>Back</button>
          <button onClick={nextStep}>Next</button>
        </div>
      )}

      {/* STEP 3 */}
      {step === 3 && (
        <div className="step-3">
          <h2>Step 3 - Upload Required Files</h2>
          {selectedLicenseFiles.length > 0 ? (
            selectedLicenseFiles.map((fileType) => (
              <div key={fileType}>
                <label>{fileType.toUpperCase()} File:</label>
                <input type="file" name={fileType} accept={`.${fileType}`} onChange={handleFileChange} />
              </div>
            ))
          ) : (
            <p>No files required based on selected licenses.</p>
          )}
          <button onClick={prevStep}>Back</button>
          <button onClick={nextStep}>Next</button>
        </div>
      )}

      {/* STEP 4 - Recap */}
      {step === 4 && (
        <div className="step-4">
          <h2>Step 4 - Recap</h2>
          <p>
            <strong>Title:</strong> {draft.title}
          </p>
          <p>
            <strong>Genre:</strong> {draft.genre}
          </p>
          <p>
            <strong>BPM:</strong> {draft.bpm}
          </p>
          <p>
            <strong>Key:</strong> {draft.key}
          </p>
          <p>
            <strong>Co-Artists (IDs):</strong> {draft.co_artists.length > 0 ? draft.co_artists.join(", ") : "None"}
          </p>
          <p>
            <strong>Licenses:</strong> {draft.licenses.length > 0 ? draft.licenses.join(", ") : "None"}
          </p>
          <button onClick={prevStep}>Back</button>
          <button onClick={nextStep}>Next</button>
        </div>
      )}

      {/* STEP 5 - Upload */}
      {step === 5 && (
        <div className="step-5">
          <h2>Step 5 - Upload</h2>
          <button onClick={prevStep}>Back</button>
          <button onClick={handleUpload}>Upload</button>
        </div>
      )}

      {/* STEP 6 - Success */}
      {step === 6 && (
        <div className="step-6">
          <h2>Step 6 - Success!</h2>
        </div>
      )}

      <pre>{JSON.stringify({ draft }, null, 2)}</pre>
      <pre>{JSON.stringify({ files }, null, 2)}</pre>
      {currentDraftId}
    </div>
  );
}
