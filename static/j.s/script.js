document.getElementById('downloadBtn').addEventListener('click', async () => {
    const username = document.getElementById('usernameInput').value.trim();
    if (!username) {
        showError('Please enter a username');
        return;
    }

    // Reset UI
    document.getElementById('errorAlert').classList.add('d-none');
    document.getElementById('profileSection').classList.add('d-none');
    document.getElementById('downloadProgress').classList.remove('d-none');
    document.getElementById('downloadResults').innerHTML = '';
    updateStatus('Fetching profile info...');
    updateProgress(10);

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const result = await response.json();

        if (result.status === 'error') {
            showError(result.message);
            return;
        }

        // Display profile info
        const profile = result.profile;
        document.getElementById('profileImage').src = profile.profile_pic_url;
        document.getElementById('profileName').innerHTML = profile.full_name;
        document.getElementById('profileUsername').innerHTML = `@${profile.username}`;
        document.getElementById('followerCount').innerHTML = profile.followers.toLocaleString();
        document.getElementById('followingCount').innerHTML = profile.following.toLocaleString();
        document.getElementById('postCount').innerHTML = profile.post_count.toLocaleString();
        document.getElementById('profileBio').innerHTML = profile.biography;
        document.getElementById('profileSection').classList.remove('d-none');

        updateStatus(`Downloading to ${result.folder}...`);
        updateProgress(30);

        // Display downloads
        result.downloads.forEach(item => {
            addDownloadItem(item.name, item.status, item.path);
        });

        updateProgress(100);
        updateStatus(`Download complete! Saved in ${result.folder}`, 'success');

    } catch (error) {
        showError(`Error: ${error.message}`);
    }
});

function updateStatus(message, type = 'info') {
    const status = document.getElementById('downloadStatus');
    status.innerHTML = message;
    status.className = 'small mb-3';
    if (type === 'success') status.classList.add('text-success');
    else if (type === 'danger') status.classList.add('text-danger');
    else status.classList.add('text-muted');
}

function updateProgress(percent) {
    const bar = document.getElementById('progressBar');
    bar.style.width = `${percent}%`;
    bar.setAttribute('aria-valuenow', percent);
}

function addDownloadItem(name, status, path) {
    const results = document.getElementById('downloadResults');
    const icon = status === 'success' ? '✓' : '✗';
    const color = status === 'success' ? 'text-success' : 'text-danger';
    
    const item = document.createElement('div');
    item.className = `download-item d-flex justify-content-between align-items-center p-2 mb-2 rounded ${color}`;
    if (status === 'success') {
        item.innerHTML = `
            <span>${name}</span>
            <a href="/download_file/${path}" class="fw-bold text-decoration-none">${icon}</a>
        `;
    } else {
        item.innerHTML = `
            <span>${name}</span>
            <span class="fw-bold">${icon}</span>
        `;
    }
    results.appendChild(item);
}

function showError(message) {
    const error = document.getElementById('errorAlert');
    error.innerHTML = message;
    error.classList.remove('d-none');
    document.getElementById('downloadProgress').classList.add('d-none');
    updateProgress(0);
}
