import { useState, useEffect } from "react";
import { useAuth } from "../../../components/context/AuthContext";
import CollaborationDropDown from "../../../components/dashBoard/pageComponents/collaborationDropDown/CollaborationDropDown";
import { getLicenseList } from "../../../api/licence";
import { createDraft, editDraft, deleteDraft, finalizeDraft, getUserDrafts } from "../../../api/beats";
import { serializeBeatData } from "../../../api/utils/serializers";
import LicenseCard from "../../../components/beats/licenses/LicenseCard";
import { useNavigate } from "react-router-dom";

export default function DashBoardCreateBeats() {
  const { user } = useAuth();
  const [showDropDown, setShowDropDown] = useState(false);
  const [licenses, setLicenses] = useState([]);
  const [selectedLicenseFiles, setSelectedLicenseFiles] = useState([]);
  const [serializedData, setSerializedData] = useState();
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
    tracks: {},
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
    if (draft.licenses.includes(selectedLicense.id)) {
      const newLicenses = draft.licenses.filter((id) => id !== selectedLicense.id);
      updateDraftField("licenses", newLicenses);
      const newFiles = licenses.filter((lic) => newLicenses.includes(lic.id)).flatMap((lic) => lic.license_file_types || []);
      setSelectedLicenseFiles(Array.from(new Set(newFiles)));
    } else {
      const newLicenses = [...draft.licenses, selectedLicense.id];
      updateDraftField("licenses", newLicenses);
      const combinedFiles = [...selectedLicenseFiles, ...selectedLicense.license_file_types];
      setSelectedLicenseFiles(Array.from(new Set(combinedFiles)));
    }
  };
  const handleFileUpload = (fileType, event) => {
    const file = event.target.files[0];
    if (file) {
      updateDraftField("tracks", { ...draft.tracks, [fileType]: file });
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
              onUserSelect={() => handleLicenseSelect(license)}
              active={draft.licenses.includes(license.id)}
            />
          ))
        ) : (
          <p>Aucune licence trouvée.</p>
        )}
        <button onClick={() => navigate("/dashboard/licences")}>Crée une licence</button>
      </div>
      <div className="step-3" alt="Fichiers">
        <h2>Upload Required Files</h2>
        {selectedLicenseFiles && selectedLicenseFiles.length > 0 ? (
          selectedLicenseFiles.map((fileType) => (
            <div key={fileType}>
              <label>{fileType.toUpperCase()} File:</label>
              <input type="file" accept={`.${fileType}`} onChange={(e) => handleFileUpload(fileType, e)} />
            </div>
          ))
        ) : (
          <p>Aucun fichier requis basé sur les licences sélectionnées.</p>
        )}
      </div>
      <div className="step-4" alt="Récapitulatif">
        <h2>Récapitulatif</h2>
        <div>
          <p>
            <strong>Titre:</strong> {draft.title}
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
            <strong>Collaborateurs (IDs):</strong> {draft.co_artists.length > 0 ? draft.co_artists.join(", ") : "Aucun"}
          </p>
          <p>
            <strong>Licences:</strong>{" "}
            {draft.licenses.length > 0
              ? draft.licenses
                  .map((licId) => {
                    const lic = licenses.find((l) => l.id === licId);
                    return lic ? `${lic.title} ${lic.artist_name || lic.price || "free"}€` : licId;
                  })
                  .join(" | ")
              : "Aucune"}
          </p>
          <p>
            <strong>Fichiers Uploadés:</strong>{" "}
            {draft.tracks && Object.keys(draft.tracks).length > 0
              ? Object.entries(draft.tracks)
                  .map(([fileType, file]) => `${fileType.toUpperCase()}: ${file.name}`)
                  .join(" | ")
              : "Aucun"}
          </p>
          {draft.cover_image && (
            <div>
              <strong>Image de couverture:</strong>
              <br />
              <img src={coverPreview} alt="Cover Preview" style={{ width: "200px" }} />
            </div>
          )}
        </div>
      </div>

      <div className="step-5" alt="Upload">
        <button>Upload</button>
      </div>
      <div className="step-6" alt="Succes"></div>
      <pre>{JSON.stringify({ draft }, null, 2)}</pre>
      <pre>{JSON.stringify({ selectedLicenseFiles }, null, 2)}</pre>
      <button onClick={() => setSerializedData(serializeBeatData(draft))}>serialize data</button>
      <pre>{JSON.stringify({ serializedData }, null, 2)}</pre>
      {coverPreview && <img src={coverPreview} alt="Cover Preview" style={{ width: "200px" }} />}
    </div>
  );
}
