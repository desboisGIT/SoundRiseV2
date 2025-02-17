import { useState, useEffect } from "react";
import { useAuth } from "../../../components/context/AuthContext";
import CollaborationDropDown from "../../../components/dashBoard/pageComponents/collaborationDropDown/CollaborationDropDown";
import { getLicenseList } from "../../../api/licence";
import LicenseCard from "../../../components/beats/licenses/LicenseCard";
import { useNavigate } from "react-router-dom";

export default function DashBoardCreateBeats() {
  const { user } = useAuth();
  const [showDropDown, setShowDropDown] = useState(false);
  const [licenses, setLicenses] = useState([]);
  const navigate = useNavigate();

  const [draft, setDraft] = useState({
    user: user ? user.id : null,
    title: "",
    bpm: 120,
    key: "",
    genre: "",
    is_public: false,
    cover_image: null,
    co_artists: [],
    tracks: [],
    licenses: [],
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

  const updateDraftField = (field, value) => {
    setDraft((prev) => ({ ...prev, [field]: value }));
  };

  const musicalKeys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

  const [coverPreview, setCoverPreview] = useState(null);

  useEffect(() => {
    if (draft.cover_image) {
      const url = URL.createObjectURL(draft.cover_image);
      setCoverPreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setCoverPreview(null);
    }
  }, [draft.cover_image]);

  const handleUserSelect = (selectedUser) => {
    if (draft.co_artists.some((id) => id === selectedUser.id)) {
      updateDraftField(
        "co_artists",
        draft.co_artists.filter((id) => id !== selectedUser.id)
      );
    } else {
      updateDraftField("co_artists", [...draft.co_artists, selectedUser.id]);
    }
  };

  const handleLicenseSelect = (selectedLicense) => {
    // Toggle license selection: if already selected, remove it; otherwise, add it.
    if (draft.licenses.includes(selectedLicense.id)) {
      updateDraftField(
        "licenses",
        draft.licenses.filter((id) => id !== selectedLicense.id)
      );
    } else {
      updateDraftField("licenses", [...draft.licenses, selectedLicense.id]);
    }
  };

  return (
    <div className="create-beat-page">
      <div className="step-1" alt="Informations">
        <input type="text" name="title" placeholder="Titre" onChange={(e) => updateDraftField("title", e.currentTarget.value)} />
        <input type="text" name="genre" placeholder="Genres" onChange={(e) => updateDraftField("genre", e.currentTarget.value)} />
        <input type="number" name="bpm" placeholder="BPM" onChange={(e) => updateDraftField("bpm", e.currentTarget.value)} />
        <input
          type="file"
          name="cover_image"
          placeholder="Image de couverture"
          onChange={(e) => updateDraftField("cover_image", e.target.files[0])}
        />
        <label htmlFor="key">Key:</label>
        <select name="key" id="key" value={draft.key} onChange={(e) => updateDraftField("key", e.target.value)}>
          <option value="">Select key</option>
          {musicalKeys.map((keyOption) => (
            <option key={keyOption} value={keyOption}>
              {keyOption}
            </option>
          ))}
        </select>
        <div>
          <button onClick={() => setShowDropDown(!showDropDown)}>Ajouter un collaborateur</button>
          <CollaborationDropDown isActive={showDropDown} onUserSelect={handleUserSelect} />
        </div>
      </div>
      <div className="step-2" alt="Licences">
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
              // Pass the toggle handler
              onUserSelect={() => handleLicenseSelect(license)}
              // Pass a prop to indicate if it's selected
            />
          ))
        ) : (
          <p>Aucune licence trouvée.</p>
        )}
        <button onClick={() => navigate("/dashboard/licences")}>Crée une licence</button>
      </div>
      <div className="step-3" alt="Fichiers"></div>
      <div className="step-4" alt="Récapitulatif"></div>
      <div className="step-5" alt="Upload"></div>
      <div className="step-6" alt="Succes"></div>
      <pre>{JSON.stringify(draft, null, 2)}</pre>
      {coverPreview && <img src={coverPreview} alt="Cover Preview" style={{ width: "200px" }} />}
    </div>
  );
}
