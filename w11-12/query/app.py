from flask import Flask, request, jsonify

app = Flask(__name__)

# Dữ liệu mẫu (giả lập 100 bản ghi)
products = [{"id": i, "name": f"Product {i}", "price": i * 10, "category": "A" if i % 2 == 0 else "B"} for i in range(1, 101)]

@app.route('/products', methods=['GET'])
def get_products():
    """
    API Query Pattern hỗ trợ: Filtering, Sorting, Pagination
    """
    result = products
    
    # 1. Filtering (Lọc)
    category = request.args.get('category')
    if category:
        result = [p for p in result if p['category'] == category]
        
    min_price = request.args.get('min_price', type=int)
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]

    # 2. Sorting (Sắp xếp)
    sort_by = request.args.get('sort')
    if sort_by in ['price', '-price']:
        reverse = sort_by.startswith('-')
        sort_key = sort_by.lstrip('-')
        result = sorted(result, key=lambda k: k[sort_key], reverse=reverse)

    # 3. Pagination (Phân trang)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    start = (page - 1) * limit
    end = start + limit
    paginated_result = result[start:end]

    return jsonify({
        "data": paginated_result,
        "meta": {
            "total": len(result),
            "page": page,
            "limit": limit
        }
    })

if __name__ == '__main__':
    app.run(port=5002, debug=True)
