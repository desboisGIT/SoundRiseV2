import "./ProfilePicture.css";
import { useNavigate } from "react-router-dom";

export default function ProfilePicture({ size = "medium", username, userID, clickAction = true, url }) {
  const navigate = useNavigate();

  const handleUserRedirect = () => {
    if (userID) {
      navigate(`/profile/${userID}`);
    }
  };

  return (
    <div
      className={`profile-picture-container ${size}`}
      onClick={clickAction ? handleUserRedirect : undefined}
      role={clickAction ? "button" : undefined}
      tabIndex={clickAction ? 0 : undefined}
    >
      <img
        src={url ? `http://127.0.0.1:8000${url}` : "/default-profile.png"}
        alt={`Photo de profile de: ${username || "Utilisateur"}`}
        className={`profile-picture ${size}`}
      />
    </div>
  );
}
