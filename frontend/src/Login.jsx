import { useState } from "react";
import { login, googleLogin } from "./api";
import { GoogleLogin } from "@react-oauth/google";

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin() {
    setError("");
    try {
      const res = await login(email, password);

      if (!res.access_token) {
        setError("Invalid credentials");
        return;
      }

      onLoginSuccess(res.access_token);
    } catch (e) {
      setError("Login failed");
    }
  }

  return (
    <div>
      <h3>Login</h3>

      <input
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />

      <br /><br />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />

      <br /><br />

      <button onClick={handleLogin}>Login</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <hr />

      <GoogleLogin
        onSuccess={async (cred) => {
          try {
            const token = cred?.credential;
            if (!token) {
              setError("Google token missing");
              return;
            }
            const res = await googleLogin(token);
            if (!res.access_token) {
              setError("Google login failed");
              return;
            }
            onLoginSuccess(res.access_token);
          } catch (e) {
            setError("Google login failed");
          }
        }}
        onError={() => setError("Google Login Failed")}
      />
    </div>
  );
}
