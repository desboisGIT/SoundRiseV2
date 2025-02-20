export default function Notification({ message, id, type, timestamp }) {
  return (
    <div>
      <p>{message}</p>
      <p>{id}</p>
      <p>{type}</p>
      <p>{timestamp}</p>
    </div>
  );
}
