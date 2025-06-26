// Fungsi untuk menampilkan notifikasi "toast" (tidak berubah)
function showNotification(message, type = 'success') {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✔' : '✖';
    toast.innerHTML = `<div class="icon">${icon}</div><div class="message">${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 5000);
}

// === FUNGSI BARU UNTUK DIALOG KONFIRMASI ===
function showConfirmationModal({ title, message, confirmText, onConfirm, onCancel }) {
    // Buat elemen overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    // Isi HTML untuk dialog
    overlay.innerHTML = `
        <div class="modal-dialog text-center">
            <h3 class="text-2xl font-bold text-stone-800">${title}</h3>
            <p class="text-stone-600 mt-4">${message}</p>
            <div class="mt-8 flex justify-center gap-4">
                <button id="modal-cancel-btn" class="font-bold py-2 px-6 rounded-lg bg-stone-200 text-stone-800 hover:bg-stone-300 transition">
                    Batal
                </button>
                <button id="modal-confirm-btn" class="font-bold py-2 px-6 rounded-lg bg-amber-800 text-white hover:bg-amber-900 transition">
                    ${confirmText || 'Ya, Lanjutkan'}
                </button>
            </div>
        </div>
    `;

    // Tambahkan ke body
    document.body.appendChild(overlay);

    // Tampilkan modal dengan animasi
    setTimeout(() => overlay.classList.add('show'), 10);

    // Fungsi untuk menutup modal
    const closeModal = () => {
        overlay.classList.remove('show');
        overlay.addEventListener('transitionend', () => overlay.remove());
    };

    // Tambahkan event listener ke tombol
    document.getElementById('modal-confirm-btn').addEventListener('click', () => {
        if (onConfirm) onConfirm();
        closeModal();
    });

    document.getElementById('modal-cancel-btn').addEventListener('click', () => {
        if (onCancel) onCancel();
        closeModal();
    });
}
