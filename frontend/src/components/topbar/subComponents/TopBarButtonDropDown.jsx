import { useState, useEffect, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown } from "@fortawesome/free-solid-svg-icons";

function TopBarButtonDropDown({ title, optionList, position }) {
  const [isActive, setIsActive] = useState(false);
  const dropdownRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);

  function getArrowDirection() {
    if (isActive) {
      return "rotate-180";
    } else {
      if (isHovered) {
        return "rotate-90";
      } else {
        return "rotate-0";
      }
    }
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsActive(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div
      className={`TopBarButtonDropDown`}
      ref={dropdownRef}
      onClick={() => setIsActive(!isActive)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="TopBarButton DropDownButton">
        <p className={`${isHovered ? "white" : "gray"}`}>{title}</p>
        <FontAwesomeIcon
          icon={faChevronDown}
          className={`chevron-icon ${getArrowDirection()}`}
        />
      </div>

      <ul
        className={`TopBarDropdownMenu ${
          isActive ? "active" : "notActive"
        } ${position}`}
        draggable="false"
      >
        {optionList.map((option, index) => (
          <li
            draggable="false"
            key={index}
            onClick={option[1]}
            className={`TopBarDropdownMenuOption ${isActive ? "active" : ""}`}
          >
            {option[0]}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TopBarButtonDropDown;
