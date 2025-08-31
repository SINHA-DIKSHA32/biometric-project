document.addEventListener("DOMContentLoaded", () => {
  const scanForm = document.getElementById("scanForm");
  const resultBox = document.getElementById("result");

  scanForm.onsubmit = async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("fingerprint");
    if (!fileInput.files[0]) {
      resultBox.innerText = "❗ Please upload a fingerprint image.";
      return;
    }

    const formData = new FormData();
    formData.append("fingerprint", fileInput.files[0]);

    try {
      const res = await fetch("http://localhost:5000/scan", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.error) {
        resultBox.innerText = "❌ " + data.error;
      } else {
        // Store matched patient info and redirect
        localStorage.setItem("patient", JSON.stringify(data));
        window.location.href = "patient.html";
      }

    } catch (err) {
      resultBox.innerText = "❌ Server error or connection issue.";
      console.error("Scan error:", err);
    }
  };
});
