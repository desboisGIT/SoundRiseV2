// ProfilePage.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import "./ProfilePage.css"; // Create and adjust this file for your styling

const ProfilePage = () => {
  // Get the id from the URL parameters.
  const { id } = useParams();

  // Local state to hold profile data, loading and error states.
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch the profile when the component mounts or when the id changes.
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/users/filter/?id=${id}`);

        // Assuming the API returns a JSON object with a "total" and a "users" array.
        if (response.data.total > 0) {
          setProfile(response.data.users[0]);
        } else {
          setError("User not found.");
        }
      } catch (err) {
        console.error(err);
        setError("Error fetching profile data.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [id]);

  // Show a loading indicator while fetching data.
  if (loading) return <div>Loading profile...</div>;

  // Show an error message if something went wrong.
  if (error) return <div>{error}</div>;

  return (
    <div className="profile-page">
      <div className="profile-picture-container">
        <img src={profile.profile_picture} alt={`${profile.username} profile`} className="profile-picture" />
      </div>
      <div className="profile-details">
        <h1>{profile.username}</h1>
        <p className="profile-email">{profile.email}</p>
        <p className="profile-bio">{profile.bio ? profile.bio : "No bio provided."}</p>
        <p className="profile-status">{profile.is_online ? "Online" : "Offline"}</p>
      </div>
    </div>
  );
};

export default ProfilePage;
