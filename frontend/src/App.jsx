import "./App.css";
import TopBarButtonDropDown from "./components/topbar/subComponents/TopBarButtonDropDown";
import TopBarButton from "./components/topbar/subComponents/TopBarButton";
import TopBar from "./components/topbar/TopBar";
import MainLogo from "./assets/main_logo.svg";
import LandingPage from "./pages/site/LandingPage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LogIn from "./pages/user/LogIn";
import Register from "./pages/user/Register";

const accountsOptions = [
  ["Profile", () => console.log("Profile/")],
  ["Settings", () => console.log("Settings/")],
  ["Messages", () => console.log("Messages/")],
  ["Log Out", () => console.log("Log Out/")],
];

const ExploreOptions = [
  ["Beats", () => console.log("Beats/")],
  ["SoundTracks", () => console.log("SoundTracks/")],
  ["Trending", () => console.log("Trendings/")],
  ["Free", () => console.log("Free/")],
];

function App() {
  return (
    <>
      <Router>
        <TopBar
          leftComponents={
            <>
              <img
                src={MainLogo}
                alt="SoundRise Logo"
                className="SoundRiseLogoMain"
                onClick={() => (window.location.href = "/")}
              />
              <TopBarButtonDropDown
                title="Feed"
                optionList={ExploreOptions}
                position={"center"}
              />
            </>
          }
          centerComponents={<></>}
          rightComponents={
            <>
              <TopBarButtonDropDown
                title="Accounts"
                optionList={accountsOptions}
                position={"center"}
              />
              <TopBarButton
                title="Log In"
                action={() => (window.location.href = "/login/")}
              />
              <TopBarButton
                title="Register"
                action={() => (window.location.href = "/register/")}
              />
            </>
          }
        />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="login/" element={<LogIn />} />
          <Route path="register/" element={<Register />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
