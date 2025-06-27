document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (!token) { window.location.href = 'login.html'; return; }
    
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('id');
    if (!bookId) { alert('ID buku tidak ditemukan.'); window.location.href = 'admin.html'; return; }

    const API_BASE_URL = 'https://fp-pweb-production.up.railway.app';
    const formTitle = document.getElementById('form-title');
    const editBookForm = document.getElementById('edit-book-form');

    // Fungsi ini sekarang akan mengisi SEMUA kolom
    function populateForm(book) {
        document.getElementById('judul').value = book.judul;
        document.getElementById('penulis').value = book.penulis;
        document.getElementById('penerbit').value = book.penerbit;
        document.getElementById('tahun_terbit').value = book.tahun_terbit;
        document.getElementById('jumlah_stok').value = book.jumlah_stok || book.stok_total;
        document.getElementById('isbn').value = book.isbn || '';
        document.getElementById('sinopsis').value = book.sinopsis || '';
    }

    async function fetchBookDetails() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/books/${bookId}`);
            if (!response.ok) throw new Error('Gagal mengambil detail buku.');
            const result = await response.json();
            formTitle.textContent = `Edit Buku: ${result.data.judul}`;
            populateForm(result.data);
        } catch (error) {
            console.error(error);
            formTitle.textContent = 'Gagal Memuat Data';
        }
    }

    // Fungsi submit ini sekarang mengirim SEMUA data
    editBookForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const updatedData = {
            judul: document.getElementById('judul').value,
            penulis: document.getElementById('penulis').value,
            penerbit: document.getElementById('penerbit').value,
            tahun_terbit: document.getElementById('tahun_terbit').value,
            jumlah_stok: document.getElementById('jumlah_stok').value,
            isbn: document.getElementById('isbn').value,
            sinopsis: document.getElementById('sinopsis').value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/books/${bookId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'x-access-token': token },
                body: JSON.stringify(updatedData)
            });
            const result = await response.json();
            alert(result.message);
            if (response.ok) { window.location.href = 'admin.html'; }
        } catch (error) {
            alert("Terjadi kesalahan saat mengupdate buku.");
        }
    });

    fetchBookDetails();
});