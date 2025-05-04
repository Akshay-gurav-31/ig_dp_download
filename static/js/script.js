document.getElementById("downloadBtn").addEventListener("click", function () {
    const input = document.getElementById("usernameInput").value.trim();
    if (!input) {
        alert("Please enter a valid Instagram username or link.");
        return;
    }

    let username = input;

    // If input is a full Instagram URL
    if (input.includes("instagram.com")) {
        const match = input.match(/instagram\.com\/([a-zA-Z0-9_.]+)/);
        if (match && match[1]) {
            username = match[1];
        } else {
            alert("Invalid Instagram URL.");
            return;
        }
    }

    // Example fallback dummy image URL
    const profileImageUrl = `https://i.imgur.com/ZRDOuzH.jpeg`;  // Static DP for testing

    // Update UI
    document.getElementById("profileSection").classList.remove("d-none");
    document.getElementById("profileImage").src = profileImageUrl;
    document.getElementById("profileName").innerText = username;
    document.getElementById("profileUsername").innerText = "@" + username;

    // Auto-download the image
    const link = document.createElement("a");
    link.href = profileImageUrl;
    link.download = `${username}_profile.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});
