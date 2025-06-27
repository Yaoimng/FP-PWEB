document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return; 
    }

    const API_BASE_URL = CONFIG.API_BASE_URL;
    const borrowedBooksList = document.getElementById('borrowed-books-list');

    const fetchAndDisplayBorrowedBooks = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/my-borrowings`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'x-access-token': token
                }
            });

            if (!response.ok) throw new Error('Gagal mengambil data peminjaman.');

            const result = await response.json();
            
            // Hapus indikator loading atau pesan sebelumnya
            borrowedBooksList.innerHTML = ''; 

            if (result.data.length === 0) {
                borrowedBooksList.innerHTML = '<div class="bg-white p-8 rounded-xl shadow-md text-center text-stone-500">Anda belum meminjam buku apapun.</div>';
                return;
            }

            result.data.forEach(book => {
                const tglPinjam = new Date(book.tanggal_pinjam).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });
                const tglKembali = new Date(book.tanggal_kembali).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });

                borrowedBooksList.innerHTML += `
                    <div class="bg-white p-6 rounded-xl shadow-md flex flex-col md:flex-row items-start md:items-center justify-between space-y-4 md:space-y-0">
                        <div>
                            <h3 class="text-xl font-bold text-stone-800">${book.judul}</h3>
                            <p class="text-sm text-stone-600">oleh ${book.penulis}</p>
                            <div class="mt-4 text-sm space-y-1">
                                <p><span class="font-semibold">Dipinjam:</span> ${tglPinjam}</p>
                                <p><span class="font-semibold">Batas Kembali:</span> <span class="text-red-600 font-bold">${tglKembali}</span></p>
                            </div>
                        </div>
                        <div class="w-full md:w-auto">
                            <button data-borrow-id="${book.id}" class="return-button w-full bg-amber-800 text-white font-bold px-6 py-2 rounded-lg hover:bg-amber-900 transition duration-200">
                                Kembalikan Buku
                            </button>
                        </div>
                    </div>
                `;
            });
            addReturnEventListeners();
        } catch (error) {
            console.error('Error:', error);
            borrowedBooksList.innerHTML = '<div class="bg-white p-8 rounded-xl shadow-md text-center text-red-500">Terjadi kesalahan saat memuat data.</div>';
        }
    };

    function addReturnEventListeners() {
        document.querySelectorAll('.return-button').forEach(button => {
            button.addEventListener('click', function() {
                returnBook(this.dataset.borrowId);
            });
        });
    }
    
    // --- FUNGSI DIPERBARUI: Menggunakan modal konfirmasi dan notifikasi toast ---
    async function returnBook(borrowId) {
        showConfirmationModal({
            title: 'Konfirmasi Pengembalian',
            message: 'Anda yakin ingin mengembalikan buku ini?',
            confirmText: 'Ya, Kembalikan',
            onConfirm: async () => {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/return/${borrowId}`, {
                        method: 'POST',
                        headers: { 'x-access-token': token }
                    });
                    const result = await response.json();
                    
                    if (response.ok) {
                        showNotification(result.message, 'success');
                        fetchAndDisplayBorrowedBooks(); // Muat ulang daftar peminjaman
                    } else {
                        showNotification(result.message, 'error');
                    }
                } catch (error) {
                    console.error('Error saat mengembalikan buku:', error);
                    showNotification('Gagal mengembalikan buku.', 'error');
                }
            }
        });
    }

    fetchAndDisplayBorrowedBooks();
});
