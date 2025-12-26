import { useState } from "react";
import { login, googleLogin } from "./api";
import { GoogleLogin } from "@react-oauth/google";

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [isSignup, setIsSignup] = useState(false);

  async function handleLogin() {
    setError("");
    try {
      let res;

      if (isSignup) {
        res = await fetch("http://localhost:8000/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name })
        }).then(r => r.json());
      } else {
        res = await login(email, password);
      }

      if (!res.access_token) {
        setError(isSignup ? "Signup failed" : "Invalid credentials");
        return;
      }

      localStorage.setItem("access_token", res.access_token);
      onLoginSuccess(res.access_token);
    } catch (e) {
      setError(isSignup ? "Signup failed" : "Login failed");
    }
  }

  return (
    <div>
      <h3>{isSignup ? "Create Account" : "Login"}</h3>

      <input
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />

      <br /><br />

      {isSignup && (
        <>
          <input
            placeholder="Name"
            value={name}
            onChange={e => setName(e.target.value)}
          />
          <br /><br />
        </>
      )}

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />

      <br /><br />

      <button onClick={handleLogin}>{isSignup ? "Sign Up" : "Login"}</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <hr />

      <button onClick={() => setIsSignup(!isSignup)}>
        {isSignup ? "Already have an account?" : "Create account"}
      </button>

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
            localStorage.setItem("access_token", res.access_token);
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
