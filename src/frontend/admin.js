document.addEventListener('DOMContentLoaded', () => {

    function parseJwt(token) { try { return JSON.parse(atob(token.split('.')[1])); } catch (e) { return null; } }

    const token = localStorage.getItem('token');
    if (!token) { window.location.href = 'login.html'; return; }

    const decodedToken = parseJwt(token);
    if (!decodedToken || decodedToken.role.trim() !== 'admin') {
        alert('Akses ditolak.');
        localStorage.removeItem('token');
        window.location.href = 'login.html';
        return;
    }

    const API_BASE_URL = 'http://127.0.0.1:5000';
    const bookListBody = document.getElementById('admin-book-list');

    async function fetchAndDisplayAllBooks() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/books`);
            if (!response.ok) throw new Error('Gagal mengambil data buku.');

            const result = await response.json();
            bookListBody.innerHTML = ''; 

            if (result.data.length === 0) {
                bookListBody.innerHTML = '<tr><td colspan="5" class="p-8 text-center text-stone-500">Belum ada buku di katalog.</td></tr>';
                return;
            }

            result.data.forEach(book => {
                const imageUrl = book.cover_image ? `${API_BASE_URL}/uploads/covers/${book.cover_image}` : 'https://i.imgur.com/6B6V5h8.png';
                const row = `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                                <div class="flex-shrink-0 h-16 w-12">
                                    <img class="h-16 w-12 object-cover rounded-md" src="${imageUrl}" alt="Cover">
                                </div>
                                <div class="ml-4">
                                    <div class="text-sm font-medium text-stone-900">${book.judul}</div>
                                    <div class="text-sm text-stone-500">${book.penerbit}</div>
                                </div>
                            </div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-stone-500">${book.penulis}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-stone-500">
                            Tersedia: ${book.stok_tersedia} <br> 
                            Total: ${book.jumlah_stok || book.stok_total}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-stone-500">${book.status || 'tersedia'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button data-book-id="${book.id}" class="edit-button text-amber-600 hover:text-amber-900">Edit</button>
                            <button data-book-id="${book.id}" class="delete-button ml-4 text-red-600 hover:text-red-900">Arsipkan</button>
                        </td>
                    </tr>
                `;
                bookListBody.innerHTML += row;
            });
            
            addEventListeners();

        } catch (error) {
            console.error(error);
            bookListBody.innerHTML = '<tr><td colspan="5" class="p-8 text-center text-red-500">Gagal memuat data.</td></tr>';
        }
    }

    function addEventListeners() {
        // Listener untuk tombol Hapus/Arsipkan
        document.querySelectorAll('.delete-button').forEach(button => {
            button.addEventListener('click', function() {
                const bookId = this.dataset.bookId;
                archiveBook(bookId); // Nama fungsi diubah agar lebih sesuai
            });
        });

        // Listener untuk tombol Edit
        document.querySelectorAll('.edit-button').forEach(button => {
            button.addEventListener('click', function() {
                const bookId = this.dataset.bookId;
                window.location.href = `edit-buku.html?id=${bookId}`;
            });
        });
    }

    // Nama fungsi diubah menjadi archiveBook agar lebih jelas
    async function archiveBook(bookId) {
        // --- PERUBAHAN TEKS KONFIRMASI ---
        Swal.fire({
            title: 'Anda Yakin?',
            text: "Buku ini akan disembunyikan dari katalog dan diarsipkan. Anda tidak bisa mengembalikannya.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Ya, arsipkan!',
            cancelButtonText: 'Batal'
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    // Endpoint tetap sama, yaitu /api/books/{id} dengan method DELETE
                    const response = await fetch(`${API_BASE_URL}/api/books/${bookId}`, {
                        method: 'DELETE',
                        headers: { 'x-access-token': token }
                    });
                    const resData = await response.json();
                    
                    if (response.ok) {
                        // --- PERUBAHAN TEKS SUKSES ---
                        Swal.fire(
                            'Diarsipkan!',
                            resData.message,
                            'success'
                        );
                        fetchAndDisplayAllBooks();
                    } else {
                        Swal.fire('Gagal!', resData.message, 'error');
                    }
                } catch (error) {
                    Swal.fire('Error!', 'Tidak dapat terhubung ke server.', 'error');
                }
            }
        });
    }

    document.getElementById('logout-button-admin').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    });
    
    document.getElementById('add-book-button').addEventListener('click', () => {
        window.location.href = 'tambah-buku.html';
    });

    fetchAndDisplayAllBooks();
});