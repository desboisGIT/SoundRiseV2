import React, { useEffect, useState } from "react";
import { getProfileInfo } from "../../api/user";
import { logout } from "../../api/auth";
import { useNavigate } from "react-router-dom";
import LogOutButton from "../../components/actionsButtons/logOut/LogOutButton";
import "./Account.css";
import ProfilePicture from "../../components/profile/ProfilePicture";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faApple, faInstagram, faSoundcloud, faSpotify, faTiktok, faTwitter, faYoutube } from "@fortawesome/free-brands-svg-icons";
import { faGlobe, faShare } from "@fortawesome/free-solid-svg-icons";
import Spacer from "../../components/utils/Spacer";

export default function Account() {
  const [userInfo, setUserInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [section, setSection] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    getProfileInfo()
      .then((data) => {
        if (data) {
          setUserInfo(data);
        } else {
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

  if (!userInfo) {
    return null;
  }

  const sectionsList = [
    <div className="profile-section profile-section-bio">
      <p>{userInfo.bio}</p>
    </div>,
    <div className="profile-section profile-section-badges">
      <p>Cette fonctionnalité est en encore en développement</p>
    </div>,
    <div className="profile-section profile-section-socials">
      {userInfo.apple_music && (
        <a className="social-link" href={userInfo.apple_music} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faApple} />
          <span> </span>
          <span className="underlined">Apple Music</span>
        </a>
      )}
      {userInfo.instagram && (
        <a className="social-link" href={userInfo.instagram} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faInstagram} />
          <span> </span>
          <span className="underlined">Instagram</span>
        </a>
      )}
      {userInfo.soundcloud && (
        <a className="social-link" href={userInfo.soundcloud} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faSoundcloud} />
          <span> </span>
          <span className="underlined">SoundCloud</span>
        </a>
      )}
      {userInfo.spotify && (
        <a className="social-link" href={userInfo.spotify} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faSpotify} className="social-link-icon" />
          <span> </span>
          <span className="underlined">Spotify</span>
        </a>
      )}
      {userInfo.tiktok && (
        <a className="social-link" href={userInfo.tiktok} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faTiktok} />
          <span> </span>
          <span className="underlined">TikTok</span>
        </a>
      )}
      {userInfo.twitter && (
        <a className="social-link" href={userInfo.twitter} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faTwitter} />
          <span> </span>
          <span className="underlined">Twitter</span>
        </a>
      )}
      {userInfo.website && (
        <a className="social-link" href={userInfo.website} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faGlobe} />
          <span> </span>
          <span className="underlined">Website</span>
        </a>
      )}
      {userInfo.youtube && (
        <a className="social-link" href={userInfo.youtube} target="_blank" rel="noopener noreferrer">
          <FontAwesomeIcon icon={faYoutube} />
          <span> </span>
          <span className="underlined">YouTube</span>
        </a>
      )}
    </div>,
  ];

  return (
    <div className="account-container">
      {/* Blurred & Cropped Background */}
      <div className="profile-header-background" style={{ backgroundImage: `url(http://127.0.0.1:8000${userInfo.profile_picture})` }}></div>
      <div className="profile-header-bottom">
        <div className="profile-header">
          <ProfilePicture size="xl" username={userInfo.username} userID={userInfo.id} clickAction={false} url={userInfo.profile_picture} />
          <div>
            <h1>{userInfo.username}</h1>
            <div className="user-metadata-stats-container">
              <div className="user-metadata-stats">
                <p>154</p>
                <p>Beats</p>
              </div>
              <div className="user-metadata-stats">
                <p>5,5k</p>
                <p>Followers</p>
              </div>
              <div className="user-metadata-stats">
                <p>23</p>
                <p>Suivis</p>
              </div>
            </div>
          </div>
        </div>
        <div className="user-container">
          <div className="user-infos">
            <div className="buttons-container">
              <div className={`button ${section === 0 ? "active" : ""}`} onClick={() => setSection(0)}>
                Bio
              </div>
              <div className={`button ${section === 1 ? "active" : ""}`} onClick={() => setSection(1)}>
                Badges
              </div>
              <div className={`button ${section === 2 ? "active" : ""}`} onClick={() => setSection(2)}>
                Réseaux
              </div>
            </div>
            <div className="info-section-container">{sectionsList[section]}</div>
            <div className="user-action-buttons">
              <div className="large-button-group">
                <button className="follow-button">+ Suivre</button>
                <button className="message-button">Écrire</button>
              </div>
              <button className="share-icon-button">
                <FontAwesomeIcon icon={faShare} style={{ color: "#DEDEDE" }} />
              </button>
            </div>
            <Spacer size="1px" color="#313131" orientation="horizontal" length="100%" />
          </div>
        </div>
      </div>
      <LogOutButton />
    </div>
  );
}
