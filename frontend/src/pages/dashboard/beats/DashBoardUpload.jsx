import { useNavigate } from "react-router-dom";

export default function DashBoardUpload() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Dashboard Upload 2</h1>
      <button onClick={() => navigate("/dashboard/upload-a-banger/")}>test</button>
    </div>
  );
}
