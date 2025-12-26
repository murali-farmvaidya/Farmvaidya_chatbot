export default function Profile({ setView }) {
  const token = localStorage.getItem("access_token");

  let email = "Unknown";
  let name = "User";

  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      email = payload.email;
      name = email.split("@")[0];
    } catch {}
  }

  return (
    <div>
      <h3>User Profile</h3>
      <p><b>Name:</b> {name}</p>
      <p><b>Email:</b> {email}</p>
      <button onClick={() => setView("chat")}>⬅ Back</button>
    </div>
  );
}
