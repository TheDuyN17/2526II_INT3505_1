from __future__ import annotations

import os

try:
    from .app import create_app
except ImportError:
    from app import create_app


def run() -> None:
    app = create_app()
    port = int(os.getenv("PORT", "5014"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"

    print(f"Week13 API as a Product running at http://127.0.0.1:{port}")
    print(f"Developer portal available at http://127.0.0.1:{port}/portal")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    run()
