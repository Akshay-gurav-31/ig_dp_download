document.getElementById("downloadBtn").addEventListener("click", function () {
    const input = document.getElementById("usernameInput").value.trim();
    if (!input) {
        alert("Please enter a valid Instagram username or link.");
        return;
    }

    let username = input;

    // If input is full URL, extract username
    if (input.includes("instagram.com")) {
        const match = input.match(/instagram\.com\/([a-zA-Z0-9_.]+)/);
        if (match && match[1]) {
            username = match[1];
        } else {
            alert("Invalid Instagram URL.");
            return;
        }
    }

    // Construct the profile image URL (this doesn't always work now due to Instagram restrictions)
    const profileImageUrl = `https://www.instagram.com/${username}/profile_pic`;

    // Display the image
    const img = document.getElementById("profileImage");
    img.src = profileImageUrl;
    img.classList.remove("d-none");

    // Update rest of the UI
    document.getElementById("profileSection").classList.remove("d-none");
    document.getElementById("profileName").innerText = username;
    document.getElementById("profileUsername").innerText = "@" + username;

    // Hide download/progress sections
    document.getElementById("downloadProgress").classList.add("d-none");
    document.getElementById("errorAlert").classList.add("d-none");
});
