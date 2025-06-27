document.addEventListener('DOMContentLoaded', function () {
    
    // --- 1. KEAMANAN & INISIALISASI ---
    const token = localStorage.getItem('token');
    const API_BASE_URL = 'https://fp-pweb-production.up.railway.app/';
    
    // --- PENAMBAHAN BARU: Variabel untuk Carousel ---
    const featuredCarousel = document.getElementById('featured-books-carousel');
    
    const bookListContainer = document.getElementById('book-list-container');
    const searchInput = document.getElementById('search-input');
    const logoutButton = document.getElementById('logout-button');
    const userNamePlaceholder = document.getElementById('user-name-placeholder');
    const userRolePlaceholder = document.getElementById('user-role-placeholder');
    let allBooks = []; 

    if (!token) {
        window.location.href = 'login.html';
        return; 
    }

    // --- 2. FUNGSI-FUNGSI UTAMA ---

    // Mengambil profil pengguna (tidak berubah)
    async function fetchUserProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/profile`, {
                method: 'GET',
                headers: { 'x-access-token': token }
            });
            if (!response.ok) throw new Error('Sesi tidak valid.');
            
            const result = await response.json();
            if (userNamePlaceholder) userNamePlaceholder.textContent = result.user.nama;
            if (userRolePlaceholder) {
                userRolePlaceholder.textContent = result.user.role;
                if(result.user.role === 'admin') {
                    userRolePlaceholder.classList.remove('bg-green-100', 'text-green-800');
                    userRolePlaceholder.classList.add('bg-red-100', 'text-red-800');
                }
            }
        } catch (error) {
            handleAuthError(error);
        }
    }

    // Mengambil semua buku dan memicu semua tampilan
    async function fetchAllBooks() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/books`);
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);
            
            allBooks = result.data;
            
            // Panggil kedua fungsi tampilan
            displayBookGrid(allBooks); // Untuk katalog utama

            // --- PENAMBAHAN BARU: Panggil fungsi carousel ---
            displayFeaturedBooks(allBooks);

        } catch (error) {
            if(bookListContainer) bookListContainer.innerHTML = '<p class="col-span-full text-center text-red-500">Gagal memuat data buku.</p>';
            if(featuredCarousel) featuredCarousel.innerHTML = '<p class="text-stone-500">Gagal memuat buku unggulan.</p>';
        }
    }
    
    // --- PENAMBAHAN BARU: Fungsi untuk menampilkan carousel ---
    function displayFeaturedBooks(books) {
        if (!featuredCarousel) return;
        
        featuredCarousel.innerHTML = ''; 
        const featured = books.slice(0, 7); // Ambil 7 buku pertama

        if (featured.length === 0) return; // Jangan tampilkan apa-apa jika tidak ada buku

        featured.forEach(book => {
            const imageUrl = book.cover_image ? `${API_BASE_URL}/uploads/covers/${book.cover_image}` : 'https://i.imgur.com/6B6V5h8.png';
            const card = document.createElement('a');
            card.href = `detail-buku.html?id=${book.id}`;
            card.className = 'flex-shrink-0 w-40 group'; // flex-shrink-0 agar tidak gepeng
            card.innerHTML = `
                <div class="rounded-lg shadow-md overflow-hidden transform transition-transform duration-300 group-hover:scale-105 group-hover:shadow-xl">
                    <img src="${imageUrl}" alt="${book.judul}" class="w-full h-60 object-cover">
                </div>
            `;
            featuredCarousel.appendChild(card);
        });
    }

    // Menampilkan katalog utama (sebelumnya bernama displayBooks)
    function displayBookGrid(booksToDisplay) {
        if (!bookListContainer) return;
        bookListContainer.innerHTML = ''; 

        if (booksToDisplay.length === 0) {
            bookListContainer.innerHTML = '<p class="col-span-full text-center text-stone-500">Buku tidak ditemukan.</p>';
            return;
        }

        booksToDisplay.forEach(book => {
            const isAvailable = book.stok_tersedia > 0;
            const bookCardLink = document.createElement('a');
            bookCardLink.href = `detail-buku.html?id=${book.id}`;
            bookCardLink.className = 'bg-white rounded-xl shadow-lg overflow-hidden flex flex-col group transition-all duration-300 hover:shadow-2xl hover:-translate-y-2';
            
            const imageUrl = book.cover_image 
                ? `${API_BASE_URL}/uploads/covers/${book.cover_image}` 
                : `https://placehold.co/400x600/FFF7E8/A16207?text=${book.judul.replace(/ /g,'\\n')}`;

            bookCardLink.innerHTML = `
                <div class="relative">
                    <img src="${imageUrl}" alt="Cover Buku: ${book.judul}" class="w-full h-64 object-cover">
                    <div class="absolute top-2 right-2 px-2 py-1 bg-white/80 backdrop-blur-sm text-xs font-bold ${isAvailable ? 'text-green-800' : 'text-red-800'} rounded-full">
                        Stok: ${book.stok_tersedia}
                    </div>
                </div>
                <div class="p-5 flex flex-col flex-grow">
                    <h3 class="text-lg font-bold text-stone-800 truncate" title="${book.judul}">${book.judul}</h3>
                    <p class="text-sm text-stone-500 mt-1">oleh ${book.penulis}</p>
                    <div class="mt-auto pt-4">
                       <span class="w-full block text-center text-sm font-bold py-2 px-4 rounded-lg bg-stone-800 text-white">
                            Lihat Detail
                       </span>
                    </div>
                </div>
            `;
            bookListContainer.appendChild(bookCardLink);
        });
    }

    // Fungsi filter pencarian (tidak berubah)
    function filterBooks() {
        const query = searchInput.value.toLowerCase();
        const filteredBooks = allBooks.filter(book => 
            book.judul.toLowerCase().includes(query) || 
            book.penulis.toLowerCase().includes(query)
        );
        displayBookGrid(filteredBooks); // Hanya memfilter grid utama
    }
    
    // Fungsi penanganan error otentikasi (tidak berubah)
    function handleAuthError(error) {
        console.error('Error otentikasi:', error);
        // Hapus alert agar tidak mengganggu jika Anda punya notifikasi lain
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }

    logoutButton.addEventListener('click', () => {
        Swal.fire({
            title: 'Konfirmasi Logout',
            text: "Apakah Anda yakin ingin keluar dari sesi ini?",
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Ya, Logout',
            cancelButtonText: 'Batal'
        }).then((result) => {
            // Kode ini hanya berjalan jika pengguna mengklik "Ya, Logout"
            if (result.isConfirmed) {
                // Tampilkan notifikasi '   selamat tinggal' yang manis
                Swal.fire({
                    title: 'Logout Berhasil!',
                    text: 'Anda akan diarahkan ke halaman login.',
                    icon: 'success',
                    timer: 2000, // Notifikasi akan hilang setelah 2 detik
                    showConfirmButton: false
                });
    
                // Hapus token dan arahkan ke halaman login setelah jeda singkat
                setTimeout(() => {
                    localStorage.removeItem('token');
                    window.location.href = 'login.html';
                }, 2000); // 2 detik
            }
        });
    });
    
    if(searchInput) {
        searchInput.addEventListener('input', filterBooks);
    }

    // --- 4. PEMANGGILAN FUNGSI AWAL ---
    fetchUserProfile();
    fetchAllBooks();
});