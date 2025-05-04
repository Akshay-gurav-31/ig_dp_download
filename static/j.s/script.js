document.getElementById("downloadBtn").addEventListener("click", function() {
    const username = document.getElementById("usernameInput").value.trim();
    if (username === "") {
        displayError("Please enter a valid username.");
        return;
    }

    // Clear previous data
    document.getElementById("errorAlert").classList.add("d-none");
    document.getElementById("profileSection").classList.add("d-none");
    document.getElementById("downloadProgress").classList.add("d-none");

    // Show loading progress
    document.getElementById("downloadProgress").classList.remove("d-none");
    document.getElementById("downloadStatus").textContent = "Fetching profile...";

    // Fetch data from your backend (assuming you have an API to handle Instagram data)
    fetch(`/api/instagram/profile/${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                displayError(data.error);
                return;
            }

            // Display profile info
            document.getElementById("profileSection").classList.remove("d-none");
            document.getElementById("profileImage").src = data.profile_image;
            document.getElementById("profileName").textContent = data.name;
            document.getElementById("profileUsername").textContent = `@${data.username}`;
            document.getElementById("followerCount").textContent = data.followers;
            document.getElementById("followingCount").textContent = data.following;
            document.getElementById("postCount").textContent = data.posts;
            document.getElementById("profileBio").textContent = data.bio;

            // Hide progress bar
            document.getElementById("downloadStatus").textContent = "Profile loaded.";
        })
        .catch(error => {
            displayError("An error occurred while fetching the profile.");
            console.error("Error fetching Instagram profile:", error);
        });
});

// Function to display error messages
function displayError(message) {
    const errorAlert = document.getElementById("errorAlert");
    errorAlert.textContent = message;
    errorAlert.classList.remove("d-none");
}
