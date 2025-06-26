# Isi file: src/books/routes.py

from flask import Blueprint
from .controllers import get_all_books, get_book_by_id, add_new_book, update_book_by_id, delete_book_by_id
# Kita perlu import decorator dari file utama
from app import token_required

# Membuat Blueprint
books_bp = Blueprint('books', __name__)

@books_bp.route('/api/books', methods=['GET'])
def books_get_all():
    return get_all_books()

@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def books_get_by_id(book_id):
    return get_book_by_id(book_id)

@books_bp.route('/api/books', methods=['POST'])
@token_required(allowed_roles=['admin']) # <-- Proteksi untuk admin
def books_add_new(current_user): # <-- Menerima current_user dari decorator
    return add_new_book()

@books_bp.route('/api/books/<int:book_id>', methods=['PUT'])
@token_required(allowed_roles=['admin'])
def books_update_by_id(current_user, book_id):
    return update_book_by_id(book_id)

@books_bp.route('/api/books/<int:book_id>', methods=['DELETE'])
@token_required(allowed_roles=['admin'])
def books_delete_by_id(current_user, book_id):
    return delete_book_by_id(book_id)