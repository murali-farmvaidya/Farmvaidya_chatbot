export default function Profile({ setView }) {
  return (
    <div>
      <h3>User Profile</h3>
      <p>Email: (from JWT later)</p>
      <button onClick={() => setView("chat")}>⬅ Back</button>
    </div>
  );
}
