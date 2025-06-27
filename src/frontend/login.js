document.addEventListener('DOMContentLoaded', function () {
    
    // --- Bagian untuk menampilkan notifikasi setelah registrasi ---
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('status') === 'registered') {
        // Tampilkan notifikasi toast sukses
        showNotification('Registrasi berhasil. Silakan login.', 'success');
    }

    // Fungsi untuk mem-parse token dan mendapatkan payload-nya
    function parseJwt(token) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    }

    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('https://fp-pweb-production.up.railway.app/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, password: password })
            });

            const result = await response.json();

            if (response.ok) {
                localStorage.setItem('token', result.token);
                const decodedToken = parseJwt(result.token);

                let redirectUrl = 'dashboard.html'; // Default redirect
                let role = 'anggota'; // Default role

                if (decodedToken && decodedToken.role) {
                    // Membersihkan kemungkinan spasi ekstra dari data peran
                    role = decodedToken.role.trim(); 
                }
                
                if (role === 'admin') {
                    redirectUrl = 'admin.html'; // Arahkan admin ke halaman admin
                }
                
                // Tampilkan notifikasi sukses sebelum redirect
                showNotification('Login berhasil! Mengarahkan...', 'success');

                // Beri jeda agar notifikasi sempat terbaca
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 1500); // Tunggu 1.5 detik

            } else {
                // Tampilkan notifikasi error jika login gagal
                showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Terjadi kesalahan:', error);
            // Tampilkan notifikasi error jika tidak bisa terhubung
            showNotification('Tidak dapat terhubung ke server.', 'error');
        }
    });
});
