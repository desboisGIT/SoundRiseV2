import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell, faChevronDown } from "@fortawesome/free-solid-svg-icons";
import SimpleDropDown from "../popups/SimpleDropDown";
import { useState, useEffect, useRef } from "react";
import "./NotificationBell.css";
import NotificationList from "./NotificationList";

export default function NotificationBell() {
  const [isActive, setIsActive] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const bellRef = useRef(null);

  const handleNotificationBellClick = () => {
    setIsActive((prev) => !prev);
  };

  const handleClickOutside = (event) => {
    if (bellRef.current && !bellRef.current.contains(event.target)) {
      setIsActive(false);
    }
  };

  useEffect(() => {
    if (isActive) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isActive]);

  return (
    <div
      ref={bellRef}
      className="notification-bell"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleNotificationBellClick}
    >
      <FontAwesomeIcon icon={faBell} className="cursor-pointer" />
      <FontAwesomeIcon
        icon={faChevronDown}
        className={`drop-down-arrow ${isActive ? "arrow-rotate-180" : isHovered ? "arrow-rotate-90" : "arrow-rotate-0"}`}
      />
      <SimpleDropDown isActive={isActive}>
        <div className="scroll-bar-container">
          <NotificationList enableWebSocket={true}></NotificationList>
        </div>
      </SimpleDropDown>
    </div>
  );
}
