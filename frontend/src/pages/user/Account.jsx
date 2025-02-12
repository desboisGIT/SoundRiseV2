import React, { useEffect, useState } from "react";
import { getUserInfo } from "../../api/user";
import { logout } from "../../api/auth";

export default function Account() {
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    getUserInfo()
      .then((data) => {
        if (data) {
          setUserInfo(data);
        }
      })
      .catch((error) => {
        console.error("Error fetching user info:", error);
      });
  }, []);

  return (
    <div>
      {!userInfo ? (
        <div>Please log in to access your account.</div>
      ) : (
        <div>
          <p>Welcome to your account!</p>
          <p>ID: {userInfo.id}</p>
          <p>Username: {userInfo.username}</p>
          <p>Email: {userInfo.email}</p>
          <p>
            Profile Picture:{" "}
            <img src={userInfo.profile_picture} alt="Profile" />
          </p>
          <p>Bio: {userInfo.bio}</p>
          <p>Status: {userInfo.is_online ? "Online" : "Offline"}</p>
          <p>Status: {userInfo.is_online ? "Online" : "Offline"}</p>
          <button onClick={logout}>🚪 Logout</button> {/* Add Logout Button */}
        </div>
      )}
    </div>
  );
}
