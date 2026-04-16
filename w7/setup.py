# coding: utf-8
# Được sinh tự động bởi OpenAPI Generator — không chỉnh sửa thủ công.

from setuptools import setup, find_packages

NAME = "openapi_server"
VERSION = "1.0.0"

REQUIRES = [
    "connexion[swagger-ui]>=2.6.0,<3.0.0",
    "swagger-ui-bundle>=0.0.2",
    "python_dateutil>=2.6.0",
    "pymongo>=4.6.0",
    "python-dotenv>=1.0.0",
    "Flask>=2.3.0,<3.0.0",
    "Werkzeug>=2.3.0,<3.0.0",
    "six>=1.16.0",
]

setup(
    name=NAME,
    version=VERSION,
    description="Product Management API — OpenAPI Generator (python-flask)",
    author="OpenAPI Generator",
    url="https://github.com/OpenAPITools/openapi-generator",
    keywords=["OpenAPI", "Product Management API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={"openapi_server": ["openapi/openapi.yaml"]},
    include_package_data=True,
    entry_points={
        "console_scripts": ["product-api=openapi_server.__main__:main"]
    },
    python_requires=">=3.11",
    long_description="",
)
