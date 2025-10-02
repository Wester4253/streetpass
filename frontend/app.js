// Main app logic
let state = {
    token: localStorage.getItem('token'),
    userId: localStorage.getItem('userId'),
    username: localStorage.getItem('username')
};

// PWA registration
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
        .then(() => console.log('Service Worker registered'))
        .catch(err => console.error('Service Worker failed:', err));
}

// Auth functions
async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!res.ok) throw new Error('Login failed');
        
        const data = await res.json();
        state.token = data.token;
        state.userId = data.user.id;
        state.username = data.user.username;
        
        localStorage.setItem('token', data.token);
        localStorage.setItem('userId', data.user.id);
        localStorage.setItem('username', data.user.username);
        
        showMainApp();
    } catch (err) {
        alert('Login failed: ' + err.message);
    }
}

async function handleRegister() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!res.ok) throw new Error('Registration failed');
        
        const data = await res.json();
        state.token = data.token;
        state.userId = data.id;
        state.username = data.username;
        
        localStorage.setItem('token', data.token);
        localStorage.setItem('userId', data.id);
        localStorage.setItem('username', data.username);
        
        showMainApp();
    } catch (err) {
        alert('Registration failed: ' + err.message);
    }
}

// Navigation
function showMainApp() {
    document.getElementById('setup-page').classList.add('hidden');
    document.getElementById('main-app').classList.remove('hidden');
    showPage('profile');
    loadProfile();
}

function showPage(pageId) {
    document.querySelectorAll('.subpage').forEach(page => page.classList.add('hidden'));
    document.getElementById(pageId + '-page').classList.remove('hidden');
    
    if (pageId === 'scan') startQRScanner();
    if (pageId === 'friends') loadFriends();
}

// Profile
async function loadProfile() {
    try {
        const res = await fetch('/api/profile', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error('Failed to load profile');
        
        const profile = await res.json();
        document.getElementById('profile-info').innerHTML = `
            <h3>${profile.username}</h3>
            <p>Member since: ${new Date(profile.created_at).toLocaleDateString()}</p>
        `;
        document.getElementById('avatar-preview').src = `/api/avatar/${profile.id}`;
    } catch (err) {
        console.error('Profile error:', err);
    }
}

async function uploadAvatar() {
    const file = document.getElementById('avatar-upload').files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch('/api/upload-avatar', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` },
            body: formData
        });
        if (!res.ok) throw new Error('Upload failed');
        
        const data = await res.json();
        document.getElementById('avatar-preview').src = data.avatar_url + '?t=' + Date.now();
    } catch (err) {
        alert('Avatar upload failed: ' + err.message);
    }
}

async function showQR() {
    const qrDiv = document.getElementById('qr-display');
    qrDiv.innerHTML = `<img src="/api/qr/${state.userId}">`;
}

// QR Scanner
let videoStream;

async function startQRScanner() {
    const video = document.getElementById('qr-video');
    const status = document.getElementById('scan-status');
    
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: "environment" }
        });
        video.srcObject = videoStream;
        video.play();
        
        requestAnimationFrame(function scan() {
            if (!video.videoWidth) {
                requestAnimationFrame(scan);
                return;
            }
            
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            const imageData = canvas.getContext('2d').getImageData(
                0, 0, canvas.width, canvas.height
            );
            
            const code = jsQR(imageData.data, imageData.width, imageData.height);
            
            if (code) {
                try {
                    const data = JSON.parse(code.data);
                    if (data.id) {
                        addFriend(data.id);
                        return;
                    }
                } catch (e) {}
            }
            
            if (document.getElementById('scan-page').classList.contains('hidden')) {
                stopQRScanner();
            } else {
                requestAnimationFrame(scan);
            }
        });
    } catch (err) {
        status.textContent = 'Camera error: ' + err.message;
    }
}

function stopQRScanner() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

// Friends
async function addFriend(friendId) {
    try {
        const res = await fetch('/api/add-friend', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${state.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ friend_id: friendId })
        });
        
        if (!res.ok) throw new Error('Failed to add friend');
        
        alert('Friend added successfully!');
        showPage('friends');
    } catch (err) {
        alert('Failed to add friend: ' + err.message);
    }
}

async function loadFriends() {
    try {
        const res = await fetch('/api/friends', {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error('Failed to load friends');
        
        const friends = await res.json();
        const list = document.getElementById('friends-list');
        
        list.innerHTML = friends.map(friend => `
            <div class="friend-card">
                <img src="/api/avatar/${friend.id}" class="avatar">
                <h3>${friend.username}</h3>
                <p>Added: ${new Date(friend.added_at).toLocaleDateString()}</p>
            </div>
        `).join('');
    } catch (err) {
        console.error('Friends error:', err);
    }
}

// Check auth on load
if (state.token) {
    showMainApp();
}