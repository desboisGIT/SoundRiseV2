import React, { useState, useEffect } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

const clientId =
  "162639459241-vfs3ogmpn0fb9jhva7fhfc18k1qlqqm0.apps.googleusercontent.com";

const LoginWithGoogle = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) setIsLoggedIn(true);
  }, []);

  const onSuccess = async (response) => {
    const tokenId = response.credential;

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/api/auth/google/callback/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: tokenId }),
          credentials: "include",
        }
      );

      const data = await res.json();
      console.log("Response from backend:", data);

      if (data.tokens) {
        localStorage.setItem("access_token", data.tokens.access);
        localStorage.setItem("refresh_token", data.tokens.refresh);
        setIsLoggedIn(true);
        console.log("User logged in successfully!");
      } else {
        console.error("Login failed:", data.error);
      }
    } catch (error) {
      console.error("Error authenticating:", error);
    }
  };

  const onFailure = (error) => {
    console.error("Google login failed:", error);
  };

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <div>
        {isLoggedIn ? (
          <p>✅ Logged in! (Token saved)</p>
        ) : (
          <GoogleLogin onSuccess={onSuccess} onError={onFailure} />
        )}
      </div>
    </GoogleOAuthProvider>
  );
};

export default LoginWithGoogle;
