import React, { useEffect, useState } from "react";
import { getUserInfo } from "../../api/user";
import { logout } from "../../api/auth";
import { useNavigate } from "react-router-dom";
import LogOutButton from "../../components/actionsButtons/logOut/LogOutButton";

export default function Account() {
  const [userInfo, setUserInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch user info when the component mounts
    getUserInfo()
      .then((data) => {
        if (data) {
          setUserInfo(data);
        } else {
          // No user info available: log out and redirect to login page
          logout();
          navigate("/login");
        }
      })
      .catch((error) => {
        console.error("Error fetching user info:", error);
        logout();
        navigate("/login");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [navigate]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  // If userInfo is still null (shouldn't happen because of the redirect logic), render nothing.
  if (!userInfo) {
    return null;
  }

  return (
    <div>
      <h1>Account</h1>
      <p>Welcome to your account!</p>
      <p>ID: {userInfo.id}</p>
      <p>Username: {userInfo.username}</p>
      <p>Email: {userInfo.email}</p>
      <p>
        Profile Picture: <img src={userInfo.profile_picture} alt="Profile" />
      </p>
      <p>Bio: {userInfo.bio}</p>
      <LogOutButton />
    </div>
  );
}
