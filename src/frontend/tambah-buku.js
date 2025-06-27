document.addEventListener('DOMContentLoaded', () => {
    // Fungsi untuk membaca token JWT
    function parseJwt(token) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    }

    // --- 1. KEAMANAN HALAMAN: Pastikan hanya admin yang bisa mengakses ---
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const decodedToken = parseJwt(token);
    if (!decodedToken || decodedToken.role.trim() !== 'admin') {
        alert('Akses ditolak.');
        window.location.href = 'dashboard.html';
        return;
    }

    // --- 2. LOGIKA PENGIRIMAN FORM ---
    const addBookForm = document.getElementById('add-book-form');
    const API_BASE_URL = CONFIG.API_BASE_URL;

    addBookForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Membuat objek FormData untuk mengirim file dan teks
        const formData = new FormData();
        
        // Menambahkan setiap data dari form ke formData
        formData.append('judul', document.getElementById('judul').value);
        formData.append('penulis', document.getElementById('penulis').value);
        formData.append('penerbit', document.getElementById('penerbit').value);
        formData.append('tahun_terbit', document.getElementById('tahun_terbit').value);
        formData.append('isbn', document.getElementById('isbn').value);
        formData.append('jumlah_stok', document.getElementById('jumlah_stok').value);
        formData.append('sinopsis', document.getElementById('sinopsis').value);
        
        const coverImageFile = document.getElementById('cover_image').files[0];
        
        // Validasi: Pastikan file gambar telah dipilih
        if (!coverImageFile) {
            alert("Harap pilih file gambar sampul.");
            return;
        }
        formData.append('cover_image', coverImageFile);

        try {
            // Mengirim FormData ke backend
            const response = await fetch(`${API_BASE_URL}/api/books`, {
                method: 'POST',
                headers: {
                    // PENTING: JANGAN set 'Content-Type'. 
                    // Browser akan melakukannya secara otomatis untuk FormData.
                    'x-access-token': token
                },
                body: formData // Kirim objek FormData secara langsung
            });

            const result = await response.json();
            alert(result.message);

            if (response.ok) {
                // Jika sukses, arahkan kembali ke admin dashboard
                window.location.href = 'admin.html';
            }
            
        } catch (error) {
            console.error('Error saat menambah buku:', error);
            alert('Terjadi kesalahan. Gagal terhubung ke server.');
        }
    });
});