import "./LicenseCard.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark, faPencil } from "@fortawesome/free-solid-svg-icons";

export default function LicenseCard({ title, description, price, files, conditions, onEdit, onDelete }) {
  return (
    <div className="license-card">
      <div className="flex space aling-center">
        <h2 className="license-card-title no-overflow">{title || "Titre"}</h2>
        {(onEdit || onDelete) && (
          <div className="flex gap-10">
            {onDelete && (
              <span onClick={onDelete} style={{ cursor: "pointer" }}>
                <FontAwesomeIcon icon={faXmark} color="#fff" />
              </span>
            )}
            {onEdit && (
              <span onClick={onEdit} style={{ cursor: "pointer" }}>
                <FontAwesomeIcon icon={faPencil} color="#fff" />
              </span>
            )}
          </div>
        )}
      </div>
      <p className="license-card-description no-overflow">{description || "Description..."}</p>
      <div className="license-card-separator"></div>
      <div className="license-card-conditions">
        {conditions.length > 3 ? (
          <>
            {conditions.slice(0, 2).map((condition, index) => (
              <p key={index} className="no-overflow">
                • {condition}
              </p>
            ))}
            <p key="more" className="license-card-more">
              + <span className="underlined">{`${conditions.length - 2} autres conditions.`}</span>
            </p>
          </>
        ) : (
          conditions.map((condition, index) => <p key={index}>{condition}</p>)
        )}
      </div>
      <div className="license-card-separator"></div>
      <div className="license-card-bottom-section">
        <p className="license-card-files no-overflow">{files.length === 0 ? "formats..." : files.join(", ")}</p>
        <p className="license-card-price">{price || "0,00"}€</p>
      </div>
    </div>
  );
}
