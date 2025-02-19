import React from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import axios from "axios";
import "./App.css";
import TopBar from "./components/topbar/TopBar";
import TopBarButtonDropDown from "./components/topbar/subComponents/TopBarButtonDropDown";
import TopBarButton from "./components/topbar/subComponents/TopBarButton";
import MainLogo from "./assets/main_logo.svg";
import LandingPage from "./pages/site/LandingPage";
import LogIn from "./pages/user/LogIn";
import Register from "./pages/user/Register";
import Account from "./pages/user/Account";
import { NotificationProvider } from "./components/context/NotificationContext";
import { WebSocketProvider } from "./components/context/WebSocketContext";
import { AuthProvider, useAuth } from "./components/context/AuthContext"; // Import your Auth context
import { useNotification } from "./components/context/NotificationContext";
import ProfilePage from "./pages/user/ProfilePage";
import userApi from "./api/user";
import { logout } from "./api/auth";

import DashboardLayout from "./pages/dashboard/DashBoardLayout";
import DashBoardLicence from "./pages/dashboard/licences/DashBoardLicence";
import DashBoardBeats from "./pages/dashboard/beats/DashBoardBeats";
import DashboardUpload from "./pages/dashboard/beats/DashBoardUpload";
import DashBoardAnalytics from "./pages/dashboard/statistics/DashBoardAnalytics";
import DashBoardProfile from "./pages/dashboard/accounts/DashBoardProfile";
import DashBoardSettings from "./pages/dashboard/accounts/DashBoardSettings";
import DashBoardSupport from "./pages/dashboard/utils/DashBoardSupport";
import DashBoardMessages from "./pages/dashboard/accounts/DashBoardMessages";
import DashBoardCreateBeats from "./pages/dashboard/beats/DashBoardCreateBeats";
import DebugPage from "./pages/DebugPage";

const clientId = "162639459241-vfs3ogmpn0fb9jhva7fhfc18k1qlqqm0.apps.googleusercontent.com";

const AppContent = () => {
  const navigate = useNavigate();
  // Get the global auth state from the context
  const { loggedIn, logoutUser } = useAuth();
  const { addNotification } = useNotification();

  const handleNotify = (message, type) => {
    addNotification({ message, type });
  };

  // Define your options for the account dropdown
  const accountsOptions = [
    ["Profile", () => navigate("/account")],
    ["Settings", () => console.log("Settings")],
    ["Messages", () => console.log("Messages")],
    ["Creators Dashboard", () => navigate("/dashboard/licences/")],
    [
      "Log Out",
      () => {
        logout();
        logoutUser();
        handleNotify("Déconnecté", "error");
        axios.defaults.headers.common["Authorization"] = null;
        window.location.reload();
      },
    ],
  ];

  const ExploreOptions = [
    ["Beats", () => console.log("Beats")],
    ["SoundTracks", () => console.log("SoundTracks")],
    ["Trending", () => console.log("Trending")],
    ["Free", () => console.log("Free")],
  ];

  return (
    <>
      <TopBar
        leftComponents={
          <>
            <div className="SoundRiseLogoContainer">
              <img src={MainLogo} alt="SoundRise Logo" className="SoundRiseLogoMain" onClick={() => navigate("/")} />
              <p className="SoundRiseLogoText" onClick={() => navigate("/")}>
                SoundRise
              </p>
            </div>
            <TopBarButtonDropDown title="Feed" optionList={ExploreOptions} position="center" />
          </>
        }
        rightComponents={
          <>
            {loggedIn ? (
              <>
                <TopBarButtonDropDown title="Accounts" optionList={accountsOptions} position="center" />
                <TopBarButton title="Refresh Token" action={() => userApi.refreshAccessToken()} />
              </>
            ) : (
              <>
                <TopBarButton title="Log In" action={() => navigate("/login")} />
                <TopBarButton title="Register" action={() => navigate("/register")} />
              </>
            )}
          </>
        }
      />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LogIn />} />
          <Route path="/register" element={<Register />} />
          <Route path="/account" element={<Account />} />
          <Route path="/profile/:id" element={<ProfilePage />} />
          <Route path="/dashboard/" element={<DashboardLayout />}>
            <Route path="my-beats" element={<DashBoardBeats />} />
            <Route path="upload-beat" element={<DashboardUpload />} />
            <Route path="licences" element={<DashBoardLicence />} />
            <Route path="analytics" element={<DashBoardAnalytics />} />
            <Route path="profile" element={<DashBoardProfile />} />
            <Route path="settings" element={<DashBoardSettings />} />
            <Route path="messages" element={<DashBoardMessages />} />
            <Route path="support" element={<DashBoardSupport />} />
            <Route path="upload-a-banger" element={<DashBoardCreateBeats />} />
          </Route>
          <Route path="/debug" element={<DebugPage />} />
        </Routes>
      </div>
    </>
  );
};

const App = () => {
  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        <WebSocketProvider>
          <NotificationProvider>
            <Router>
              <AppContent />
            </Router>
          </NotificationProvider>
        </WebSocketProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
