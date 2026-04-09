# -*- coding: utf-8 -*-
"""
Python client duoc sinh tu dong tu library-api.apib
Sinh boi: generate_client.py (API Blueprint Codegen Demo)
"""

import sys
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class LibraryAPIClient:
    BASE_URL = "http://localhost:3000/api"

    def __init__(self, base_url=None):
        if base_url:
            self.BASE_URL = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def lay_danh_sach_sach(self, search=None, genre=None):
        """[GET] /books - Lấy danh sách sách"""
        url = self.BASE_URL + "/books"
        params = {k: v for k, v in {'search': search, 'genre': genre}.items() if v}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def them_sach_moi(self, data):
        """[POST] /books - Thêm sách mới"""
        url = self.BASE_URL + "/books"
        resp = self.session.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def lay_sach_theo_id(self, id):
        """[GET] /books/{id} - Lấy sách theo ID"""
        url = self.BASE_URL + f"/books/{id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def cap_nhat_sach(self, id, data):
        """[PUT] /books/{id} - Cập nhật sách"""
        url = self.BASE_URL + f"/books/{id}"
        resp = self.session.put(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def xoa_sach(self, id):
        """[DELETE] /books/{id} - Xóa sách"""
        url = self.BASE_URL + f"/books/{id}"
        resp = self.session.delete(url)
        resp.raise_for_status()
        return resp.json()


if __name__ == '__main__':
    import json

    client = LibraryAPIClient()
    print('=== Demo Python Client (sinh từ API Blueprint) ===')
    print()

    # GET /books
    print('[GET] Danh sách sách:')
    books = client.lay_danh_sach_sach()
    print(json.dumps(books, ensure_ascii=False, indent=2))
    print()

    # POST /books
    print('[POST] Thêm sách mới:')
    new_book = client.them_sach_moi(
        data={'title': 'Design Patterns', 'author': 'Gang of Four', 'year': 1994, 'genre': 'Technology'}
    )
    print(json.dumps(new_book, ensure_ascii=False, indent=2))
    book_id = new_book['id']
    print()

    # GET /books/{id}
    print(f'[GET] Lấy sách ID={book_id}:')
    book = client.lay_sach_theo_id(id=book_id)
    print(json.dumps(book, ensure_ascii=False, indent=2))
    print()

    # PUT /books/{id}
    print(f'[PUT] Cập nhật sách ID={book_id}:')
    updated = client.cap_nhat_sach(
        id=book_id,
        data={'title': 'Design Patterns (Updated)', 'author': 'Gang of Four', 'year': 1995, 'genre': 'Technology'}
    )
    print(json.dumps(updated, ensure_ascii=False, indent=2))
    print()

    # DELETE /books/{id}
    print(f'[DELETE] Xóa sách ID={book_id}:')
    result = client.xoa_sach(id=book_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))