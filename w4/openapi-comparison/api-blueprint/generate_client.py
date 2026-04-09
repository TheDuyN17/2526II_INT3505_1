"""
Codegen Demo: Sinh Python client từ API Blueprint (.apib)
Chạy: python generate_client.py
"""

import re
import os

APIB_FILE = os.path.join(os.path.dirname(__file__), "library-api.apib")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "generated_client.py")


def parse_apib(filepath):
    """Parse file .apib để trích xuất endpoints."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Lấy HOST
    host_match = re.search(r"^HOST:\s*(.+)$", content, re.MULTILINE)
    base_url = host_match.group(1).strip() if host_match else "http://localhost:3000/api"

    endpoints = []
    # Pattern: ## Resource [/path] và ### Action [METHOD]
    resource_pattern = re.compile(r"^##\s+.+\[(/[^\]]*)\]", re.MULTILINE)
    action_pattern = re.compile(r"^###\s+(.+?)\s+\[([A-Z]+)\]", re.MULTILINE)

    lines = content.split("\n")
    current_path = ""
    for i, line in enumerate(lines):
        rm = resource_pattern.match(line)
        if rm:
            current_path = rm.group(1)
            continue
        am = action_pattern.match(line)
        if am and current_path:
            endpoints.append({
                "description": am.group(1).strip(),
                "method": am.group(2).upper(),
                "path": current_path,
            })

    return base_url, endpoints


def method_name(description):
    """Chuyển description sang tên hàm Python."""
    name = description.lower()
    name = re.sub(r"[àáạảãăắặẳẵấầậẩẫ]", "a", name)
    name = re.sub(r"[èéẹẻẽêếềệểễ]", "e", name)
    name = re.sub(r"[ìíịỉĩ]", "i", name)
    name = re.sub(r"[òóọỏõôốồộổỗơớờợởỡ]", "o", name)
    name = re.sub(r"[ùúụủũưứừựửữ]", "u", name)
    name = re.sub(r"[ỳýỵỷỹ]", "y", name)
    name = re.sub(r"đ", "d", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def generate_code(base_url, endpoints):
    """Sinh Python client code từ danh sách endpoints."""
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "Python client duoc sinh tu dong tu library-api.apib",
        "Sinh boi: generate_client.py (API Blueprint Codegen Demo)",
        '"""',
        "",
        "import sys",
        "import requests",
        "",
        "if hasattr(sys.stdout, 'reconfigure'):",
        "    sys.stdout.reconfigure(encoding='utf-8')",
        "",
        "",
        "class LibraryAPIClient:",
        f'    BASE_URL = "{base_url}"',
        "",
        "    def __init__(self, base_url=None):",
        "        if base_url:",
        "            self.BASE_URL = base_url",
        "        self.session = requests.Session()",
        "        self.session.headers.update({'Content-Type': 'application/json'})",
        "",
    ]

    for ep in endpoints:
        path = ep["path"]
        method = ep["method"]
        desc = ep["description"]
        fname = method_name(desc)

        # Xác định params của hàm
        path_params = re.findall(r"\{(\w+)\}", path)
        has_body = method in ("POST", "PUT", "PATCH")
        has_query = method == "GET" and "/books" in path and "{" not in path

        params = ["self"] + path_params
        if has_body:
            params.append("data")
        if has_query:
            params.append("search=None")
            params.append("genre=None")

        lines.append(f"    def {fname}({', '.join(params)}):")
        lines.append(f'        """[{method}] {path} - {desc}"""')

        # Build URL
        py_path = re.sub(r"\{(\w+)\}", r"{\1}", path)
        if path_params:
            lines.append(f'        url = self.BASE_URL + f"{py_path}"')
        else:
            lines.append(f'        url = self.BASE_URL + "{path}"')

        # Build params / body
        if has_query:
            lines.append("        params = {k: v for k, v in {'search': search, 'genre': genre}.items() if v}")
            lines.append(f"        resp = self.session.{method.lower()}(url, params=params)")
        elif has_body:
            lines.append(f"        resp = self.session.{method.lower()}(url, json=data)")
        else:
            lines.append(f"        resp = self.session.{method.lower()}(url)")

        lines.append("        resp.raise_for_status()")
        lines.append("        return resp.json()")
        lines.append("")

    # Thêm main demo
    lines += [
        "",
        "if __name__ == '__main__':",
        "    import json",
        "",
        "    client = LibraryAPIClient()",
        "    print('=== Demo Python Client (sinh từ API Blueprint) ===')",
        "    print()",
        "",
        "    # GET /books",
        "    print('[GET] Danh sách sách:')",
        "    books = client." + method_name(next(e["description"] for e in endpoints if e["method"] == "GET" and "{" not in e["path"])) + "()",
        "    print(json.dumps(books, ensure_ascii=False, indent=2))",
        "    print()",
        "",
        "    # POST /books",
        "    print('[POST] Thêm sách mới:')",
        "    new_book = client." + method_name(next(e["description"] for e in endpoints if e["method"] == "POST")) + "(",
        "        data={'title': 'Design Patterns', 'author': 'Gang of Four', 'year': 1994, 'genre': 'Technology'}",
        "    )",
        "    print(json.dumps(new_book, ensure_ascii=False, indent=2))",
        "    book_id = new_book['id']",
        "    print()",
        "",
        "    # GET /books/{id}",
        "    print(f'[GET] Lấy sách ID={book_id}:')",
        "    book = client." + method_name(next(e["description"] for e in endpoints if e["method"] == "GET" and "{" in e["path"])) + f"(id=book_id)",
        "    print(json.dumps(book, ensure_ascii=False, indent=2))",
        "    print()",
        "",
        "    # PUT /books/{id}",
        "    print(f'[PUT] Cập nhật sách ID={book_id}:')",
        "    updated = client." + method_name(next(e["description"] for e in endpoints if e["method"] == "PUT")) + "(",
        "        id=book_id,",
        "        data={'title': 'Design Patterns (Updated)', 'author': 'Gang of Four', 'year': 1995, 'genre': 'Technology'}",
        "    )",
        "    print(json.dumps(updated, ensure_ascii=False, indent=2))",
        "    print()",
        "",
        "    # DELETE /books/{id}",
        "    print(f'[DELETE] Xóa sách ID={book_id}:')",
        "    result = client." + method_name(next(e["description"] for e in endpoints if e["method"] == "DELETE")) + "(id=book_id)",
        "    print(json.dumps(result, ensure_ascii=False, indent=2))",
    ]

    return "\n".join(lines)


def main():
    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Reading: {APIB_FILE}")
    base_url, endpoints = parse_apib(APIB_FILE)

    print(f"  HOST: {base_url}")
    print(f"  Found {len(endpoints)} endpoints:")
    for ep in endpoints:
        print(f"    [{ep['method']}] {ep['path']} - {ep['description']}")

    code = generate_code(base_url, endpoints)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\nGenerated: {OUTPUT_FILE}")
    print("\nRun demo:")
    print("  python generated_client.py")


if __name__ == "__main__":
    main()
