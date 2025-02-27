import React, { useState, useEffect } from "react";
import "./Notification.css";
import { fetchUserById } from "../../api/user";

export default function Notification({ message, id, type, timestamp, sender_id, draft_beat_title, is_live }) {
  const [sender, setSender] = useState(null);

  useEffect(() => {
    if (sender_id) {
      fetchUserById(sender_id)
        .then((user) => {
          setSender(user);
        })
        .catch((error) => {
          console.error("Error fetching sender info:", error);
        });
    }
  }, [sender_id]);

  if (type === "invitation_collab") {
    return (
      <div
        className="notification-card invitation_collab"
        alt={`metadata: message: ${message} id: ${id} type: ${type} timestamp: ${timestamp} sender_id: ${sender_id} draft_beat_title ${draft_beat_title}`}
      >
        <div className="invitation-header">
          {sender && (
            <>
              <div className="notification-top">
                <img className="sender-profile-picture" src={sender.profile_picture} alt={`${sender.username}'s profile`} />
                <p>
                  {is_live && <div className="new-notification-mark"></div>}
                  <span className="sender-username">{sender.username}</span> vous a invité a collaboré sur{" "}
                  <strong>{draft_beat_title ? draft_beat_title : "Beat sans titre"}</strong>{" "}
                  <span className="invitation_collab-actions">
                    <span className="invitation_collab-actions-more text-hover">Plus...</span>
                    <br />
                  </span>
                </p>
              </div>
              <div className="notification-end">
                <span className="notification-end-margin">
                  <span className="text-hover">Accepté</span>
                  <span> ou </span>
                  <span className="text-hover">Refuser</span>
                </span>
                <p className="notification-timestamp">{timestamp}</p>
              </div>
            </>
          )}
        </div>
      </div>
    );
  } else {
    return (
      <div
        className="notification-card"
        alt={`metadata: message: ${message} id: ${id} type: ${type} timestamp: ${timestamp} sender_id: ${sender_id}`}
      >
        <p>{message}</p>
        <p>{timestamp}</p>
        <p>{draft_beat_title}</p>
      </div>
    );
  }
}
