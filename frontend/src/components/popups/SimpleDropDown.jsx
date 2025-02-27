import "./SimpleDropDown.css";

export default function SimpleDropDown({ children, isActive }) {
  return <div className={`simple-drop-down ${isActive ? "active" : ""}`}>{children}</div>;
}
