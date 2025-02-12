import "./LogOutButton.css";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../../NotificationContext";
import { useAuth } from "../../context/AuthContext"; // Import the hook to access global auth

export default function LogOutButton() {
  const navigate = useNavigate();
  const { addNotification } = useNotification();
  const { logout } = useAuth(); // Use the global logout function

  const handleNotify = (message, type) => {
    addNotification({ message, type });
  };

  const handleLogout = () => {
    // Call the global logout function to update the auth state
    logout();
    handleNotify("Déconnecté", "error");
    navigate("/");
  };

  return (
    <button className="logout-button" onClick={handleLogout}>
      Log Out
    </button>
  );
}
