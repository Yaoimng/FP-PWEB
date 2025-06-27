/**
 * Konfigurasi global aplikasi
 */
const CONFIG = {
    // Deteksi lingkungan secara otomatis (contoh sederhana)
    // Jika menggunakan localhost, berarti development
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:5000'  // Development URL
        : 'https://fp-pweb-production.up.railway.app', // Production URL
    
    // Konfigurasi lainnya
    APP_VERSION: '1.0.0',
    APP_NAME: 'E-Library'
};