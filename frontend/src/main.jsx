import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { GoogleOAuthProvider } from "@react-oauth/google";

ReactDOM.createRoot(document.getElementById("root")).render(
  <GoogleOAuthProvider clientId="897402487235-m2u1eq4v9ro7jdro3h1gjgmt6h236nhh.apps.googleusercontent.com">
    <App />
  </GoogleOAuthProvider>
);
