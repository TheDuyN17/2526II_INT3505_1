import os
import re

# Thư mục chứa code sinh ra
SRC_DIR = "src"

def clean_pydantic_imports(match):
    """
    Sửa lại cú pháp import của pydantic nếu bị script replace nhầm thành "int", "float", "str"
    """
    import_list = match.group(1).split(",")
    # Loại bỏ các kiểu cơ bản (vì không thể import 'int' từ pydantic)
    clean_list = [imp.strip() for imp in import_list if imp.strip() not in ["int", "float", "str"]]
    
    if not clean_list:
        return "" # Nếu import array rỗng thì xoá luôn dòng import
        
    return f"from pydantic import {', '.join(clean_list)}"

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Thay thế các kiểu Strict thành kiểu native của Python
    content = re.sub(r'\bStrictInt\b', 'int', content)
    content = re.sub(r'\bStrictFloat\b', 'float', content)
    content = re.sub(r'\bStrictStr\b', 'str', content)

    # 2. Xử lý logic gộp Union thừa: Union[float, int] -> float (nếu cần)
    content = content.replace("Union[float, int]", "float")
    
    # 3. Dọn dẹp dòng import pydantic bị dính lỗi cú pháp (do thay thế ở bước 1)
    content = re.sub(r'^from pydantic import (.*?)$', clean_pydantic_imports, content, flags=re.MULTILINE)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Đã fix lỗi Strict Type tại tệp: {filepath}")

def main():
    if not os.path.exists(SRC_DIR):
        print(f"❌ Không tìm thấy thư mục {SRC_DIR}/. Vui lòng chạy script này tại gốc thư mục generated-server.")
        return

    count = 0
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                patch_file(filepath)
                count += 1
                
    print(f"🎉 Hoàn tất! Đã quét {count} file python.")

if __name__ == "__main__":
    main()
