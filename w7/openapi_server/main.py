# coding: utf-8
"""
Tạo và cấu hình Connexion application.

Connexion tự động:
- Đọc openapi.yaml và tạo routes tương ứng
- Map operationId -> Python function trong controllers
- Validate request/response theo schema
- Serve Swagger UI tại /api/ui/
"""

import connexion
from openapi_server.encoder import JSONEncoder


def create_app() -> connexion.App:
    """
    Khởi tạo Connexion app.

    specification_dir: thư mục chứa openapi.yaml (tương đối với package)
    pythonic_params: tự động chuyển camelCase -> snake_case cho params
    """
    app = connexion.App(__name__, specification_dir="openapi/")

    # Dùng custom JSON encoder để xử lý datetime và Model objects
    app.app.json_provider_class = JSONEncoder
    app.app.json = JSONEncoder(app.app)

    app.add_api(
        "openapi.yaml",
        arguments={"title": "Product Management API"},
        pythonic_params=True,
    )

    # Kết nối MongoDB khi khởi động app
    from openapi_server.database.connection import init_db

    with app.app.app_context():
        init_db()

    return app


# Tạo app instance ở module level để các tool như gunicorn có thể import
app = create_app()
