import React, { useState, useEffect } from "react";
import { GoogleLogin } from "@react-oauth/google";

const LoginWithGoogle = () => {
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
    <GoogleLogin
      onSuccess={onSuccess}
      onError={onFailure}
      theme="filled_black"
      text="continue_with"
      size="large"
      width="283"
      clas
    />
  );
};

export default LoginWithGoogle;
