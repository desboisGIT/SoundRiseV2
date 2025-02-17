// src/components/dashBoard/pageComponents/collaborationDropDown/CollaborationDropDown.jsx
import React, { useState, useEffect } from "react";
import { fetchFilteredUsers } from "../../../../api/user"; // adjust path if needed
import "./CollaborationDropDown.css";

export default function CollaborationDropDown({ isActive, onUserSelect }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [users, setUsers] = useState([]);

  // Fetch users using your filtering endpoint; default is first 10 users.
  const fetchUsers = async (term = "") => {
    try {
      const data = await fetchFilteredUsers({
        fields: ["profile_picture", "username", "id"],
        limit: 10,
        offset: 0,
        username: term,
      });
      setUsers(data.users);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  // On mount, fetch the default list.
  useEffect(() => {
    fetchUsers();
  }, []);

  // When the search input changes, update and fetch.
  const handleSearchChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    fetchUsers(term);
  };

  return (
    <div className={`collaboration-dropdown ${isActive ? "active" : ""}`}>
      <input type="text" placeholder="Search user" value={searchTerm} onChange={handleSearchChange} />
      <ul>
        {users.map((u) => (
          <li key={u.id} onClick={() => onUserSelect(u)}>
            <img src={u.profile_picture} alt={u.username} style={{ width: "30px", height: "30px", marginRight: "8px" }} />
            {u.username}
          </li>
        ))}
      </ul>
    </div>
  );
}
