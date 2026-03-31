// MPSK Admin JavaScript

// Auto-dismiss flash alerts
document.querySelectorAll('.flash-admin .alert').forEach(el => {
    setTimeout(() => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    }, 5000);
});

// Sidebar active state on mobile close
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) && !e.target.closest('[onclick*="sidebar"]')) {
        sidebar.classList.remove('open');
    }
});

// Confirm before delete (backup — also handled inline)
function confirmDelete(msg = 'Delete this item? This action cannot be undone.') {
    return confirm(msg);
}

// Preview image before upload
function previewImage(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (input && preview) {
        input.addEventListener('change', () => {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// Highlight unread rows
document.querySelectorAll('tr[style*="background:#fffef7"]').forEach(row => {
    row.style.borderLeft = '3px solid #C9943A';
});
