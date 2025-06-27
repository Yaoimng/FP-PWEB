document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    // Jika tidak ada token, langsung arahkan ke login.
    // Tidak perlu alert karena halaman ini memang tidak bisa diakses tanpa login.
    if (!token) { 
        window.location.href = 'login.html'; 
        return; 
    }

    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('id');

    // Inisialisasi variabel
    const API_BASE_URL = 'https://fp-pweb-production.up.railway.app';
    const bookDetailContainer = document.getElementById('book-detail-container');
    const loadingText = document.getElementById('loading-text');

    // Cek apakah ID buku ada di URL
    if (!bookId) {
        if(loadingText) loadingText.textContent = 'ID buku tidak valid atau tidak ditemukan di URL.';
        // Gunakan notifikasi baru jika ID tidak ada
        showNotification('ID buku tidak ditemukan.', 'error');
        return;
    }

    // Fungsi untuk menampilkan detail buku yang diterima dari API
    function displayBookDetails(book) {
        document.title = `${book.judul} - E-Library`;
        
        const isAvailable = book.stok_tersedia > 0;
        
        // Logika untuk menentukan URL gambar sampul
        const imageUrl = book.cover_image 
            ? `${API_BASE_URL}/uploads/covers/${book.cover_image}` 
            : 'https://source.unsplash.com/400x600/?book,cover';

        const detailHTML = `
            <div class="bg-white rounded-2xl shadow-xl overflow-hidden md:grid md:grid-cols-3 md:gap-x-12">
                <div class="col-span-1">
                    <img id="book-cover-image" 
                         src="${imageUrl}" 
                         alt="Sampul Buku ${book.judul}" class="w-full h-full object-cover bg-stone-200">
                </div>

                <div class="col-span-2 p-8 md:py-10 md:pr-10">
                    <h1 class="text-4xl lg:text-5xl font-extrabold text-stone-900">${book.judul}</h1>
                    <p class="mt-3 text-lg text-stone-600">oleh <span class="font-semibold">${book.penulis}</span></p>
                    <hr class="my-8">
                    <div>
                        <h3 class="font-bold text-stone-800 tracking-wide mb-3">SINOPSIS</h3>
                        <p class="text-stone-600 leading-relaxed text-justify">${book.sinopsis || 'Tidak ada sinopsis.'}</p>
                    </div>
                    <hr class="my-8">
                    <div class="grid grid-cols-2 gap-6 text-sm">
                        <div>
                            <p class="font-semibold text-stone-500 uppercase tracking-wider">Penerbit</p>
                            <p class="text-stone-800">${book.penerbit}</p>
                        </div>
                        <div>
                            <p class="font-semibold text-stone-500 uppercase tracking-wider">Tahun Terbit</p>
                            <p class="text-stone-800">${book.tahun_terbit}</p>
                        </div>
                        <div>
                            <p class="font-semibold text-stone-500 uppercase tracking-wider">ISBN</p>
                            <p class="text-stone-800">${book.isbn || '-'}</p>
                        </div>
                    </div>
                    <div class="mt-10 bg-stone-50 rounded-lg p-5 flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
                        <div class="text-lg">
                            <span class="font-medium">Stok Tersedia:</span>
                            <span class="font-bold text-2xl ${isAvailable ? 'text-green-600' : 'text-red-500'}">${book.stok_tersedia}</span>
                        </div>
                        <button id="borrow-button" 
                                class="w-full sm:w-auto text-white font-bold py-4 px-8 rounded-lg transition duration-300 shadow-lg transform hover:scale-105 ${isAvailable ? 'bg-amber-800 hover:bg-amber-900' : 'bg-stone-400 cursor-not-allowed'}"
                                ${!isAvailable ? 'disabled' : ''}>
                            ${isAvailable ? 'Pinjam Buku Ini' : 'Stok Habis'}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        if(loadingText) loadingText.remove();
        bookDetailContainer.innerHTML = detailHTML;

        // Tambahkan listener hanya jika buku tersedia
        if (isAvailable) {
            document.getElementById('borrow-button').addEventListener('click', () => {
                borrowBook(book.id);
            });
        }
    }

    // Fungsi untuk mengambil detail buku dari API
    async function fetchBookDetails() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/books/${bookId}`);
            if (!response.ok) throw new Error('Gagal mengambil detail buku.');
            const result = await response.json();
            displayBookDetails(result.data);
        } catch (error) {
            console.error(error);
            if(loadingText) {
                loadingText.textContent = 'Gagal memuat data buku. Silakan kembali ke katalog.';
                loadingText.classList.add('text-red-500');
            }
        }
    }

    // --- FUNGSI DIPERBARUI: Menggunakan modal konfirmasi dan notifikasi toast ---
    async function borrowBook(id) {
        showConfirmationModal({
            title: 'Konfirmasi Peminjaman',
            message: 'Apakah Anda yakin ingin meminjam buku ini?',
            confirmText: 'Ya, Pinjam',
            onConfirm: async () => {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/borrow/${id}`, {
                        method: 'POST',
                        headers: { 'x-access-token': token }
                    });
                    const result = await response.json();
                    
                    if(response.ok) {
                        showNotification(result.message, 'success');
                        fetchBookDetails(); // Muat ulang detail untuk update stok
                    } else {
                        showNotification(result.message, 'error');
                    }
                } catch (error) {
                    showNotification('Terjadi kesalahan saat meminjam buku.', 'error');
                }
            }
        });
    }

    // Panggil fungsi utama untuk memulai pengambilan data
    fetchBookDetails();
});
