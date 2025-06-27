# Isi file: src/borrowings/routes.py

from flask import Blueprint
# Impor fungsi-fungsi baru dari controller
from .controllers import borrow_a_book, get_my_borrowings, return_a_book
# Impor decorator dari extensions
from extensions import token_required

# Membuat Blueprint untuk borrowings
borrowings_bp = Blueprint('borrowings', __name__)

# Endpoint untuk meminjam buku (sudah ada)
@borrowings_bp.route('/api/borrow/<int:book_id>', methods=['POST'])
@token_required()
def handle_borrow_book(current_user, book_id):
    return borrow_a_book(current_user, book_id)

# === RUTE BARU 1: Melihat Peminjaman Saya ===
@borrowings_bp.route('/api/my-borrowings', methods=['GET'])
@token_required()
def handle_get_my_borrowings(current_user):
    return get_my_borrowings(current_user)

# === RUTE BARU 2: Mengembalikan Buku ===
@borrowings_bp.route('/api/return/<int:borrow_id>', methods=['POST'])
@token_required()
def handle_return_book(current_user, borrow_id):
    return return_a_book(current_user, borrow_id)
