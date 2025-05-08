document.addEventListener("DOMContentLoaded", function () {
  const uploadBox = document.getElementById("uploadBox");
  const fileInput = uploadBox.querySelector("input[type='file']");
  const loader = document.getElementById("loader");

  uploadBox.addEventListener("dragover", function (e) {
    e.preventDefault();
    uploadBox.classList.add("hover");
  });

  uploadBox.addEventListener("dragleave", function (e) {
    e.preventDefault();
    uploadBox.classList.remove("hover");
  });

  uploadBox.addEventListener("drop", function (e) {
    e.preventDefault();
    uploadBox.classList.remove("hover");
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      handleFile(file);
    } else {
      alert("Please upload a valid PDF file.");
    }
  });

  uploadBox.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];
    if (file) {
      handleFile(file);
    }
  });

  function handleFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    loader.style.display = "block";

    fetch("/convert", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      loader.style.display = "none";
      if (data.status === "success") {
        window.location.href = data.download_link;
      } else if (data.status === "manual") {
        window.location.href = data.inspect_url;
      } else {
        alert("Conversion failed.");
      }
    });
  }
});
