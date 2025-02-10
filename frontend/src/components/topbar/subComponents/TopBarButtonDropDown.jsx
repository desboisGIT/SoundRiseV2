import { useState, useEffect, useRef } from "react";

function TopBarButtonDropDown({ title, optionList, position }) {
    const [isActive, setIsActive] = useState(false);
    const dropdownRef = useRef(null);

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
        <div className="TopBarButtonDropDown" ref={dropdownRef}>
            <div onClick={() => setIsActive(!isActive)} className="TopBarButton">{title}</div>
            <ul className={`TopBarDropdownMenu ${isActive ? "active" : ""} ${position}`} draggable='false'>
                {optionList.map((option, index) => (
                    <li draggable='false' key={index} onClick={option[1]} className={`TopBarDropdownMenuOption ${isActive ? "active" : ""}`} >
                        {option[0]}
                    </li>
                ))}
            </ul>
        </div >
    );
}

export default TopBarButtonDropDown;
