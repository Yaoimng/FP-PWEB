document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('register-form');

    registerForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const nama = document.getElementById('nama').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Validasi frontend sederhana
        if (!nama || !email || !password) {
            showNotification('Semua kolom harus diisi.', 'error');
            return;
        }

        const formData = {
            nama: nama,
            email: email,
            password: password
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                // Tidak lagi menampilkan notifikasi di sini,
                // karena halaman login akan menampilkannya.
                // Cukup arahkan ke halaman login dengan parameter.
                window.location.href = 'login.html?status=registered';
            } else {
                // Tampilkan notifikasi error dari server
                showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Terjadi kesalahan:', error);
            // Tampilkan notifikasi error jika koneksi gagal
            showNotification('Tidak dapat terhubung ke server.', 'error');
        }
    });
}); 
