import { useEffect } from "react";

export default function GoogleTest() {
  useEffect(() => {
    /* global google */
    google.accounts.id.initialize({
      client_id: "",
      callback: handleCredentialResponse
    });

    google.accounts.id.renderButton(
      document.getElementById("googleBtn"),
      { theme: "outline", size: "large" }
    );
  }, []);

  function handleCredentialResponse(response) {
    console.log("Google ID Token:", response.credential);
  }

  return <div id="googleBtn"></div>;
}
