import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from weaver.server.routes.chat_route import chat_bp
from weaver.server.routes.file_route import file_bp
from weaver.server.routes.memory_route import memory_bp
from weaver.util.init_chat2graph import init_chat2graph


def create_app() -> Flask:
    """Create and configure Flask app."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "weaver-memory-secret-key"
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")

    # Create upload directory if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- BEGIN CORS MODIFICATION ---
    # Define all allowed frontend origins
    allowed_origins = [
        "http://localhost:5889",  # 你的 python -m http.server 运行的前端
        "http://127.0.0.1:5889",  # 同上，用 127.0.0.1 访问时
        "http://localhost:3000",  # 之前配置中允许的源
        "http://127.0.0.1:3000",  # 同上，用 127.0.0.1 访问时
    ]

    # Enable CORS for the entire app (applies to routes like /health, /demo, etc.
    # and serves as a default for blueprints if they don't have more specific config)
    CORS(app, origins=allowed_origins)

    # Enable CORS for all API blueprints, making their routes accessible
    # from the defined origins.
    # The r"*": {"origins": allowed_origins} means all routes within each blueprint
    # will accept requests from the origins listed in allowed_origins.
    blueprint_resource_config = {r"*": {"origins": allowed_origins}}
    CORS(memory_bp, resources=blueprint_resource_config)
    CORS(chat_bp, resources=blueprint_resource_config)  # chat_bp 现在明确使用 allowed_origins
    CORS(file_bp, resources=blueprint_resource_config)
    # --- END CORS MODIFICATION ---

    # Initialize chat2graph
    init_chat2graph()

    # Register blueprints
    app.register_blueprint(memory_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")  # /api/chat 路由在此
    app.register_blueprint(file_bp, url_prefix="/api")

    # Serve static files (HTML demo page)
    @app.route("/")
    def serve_demo():
        return send_from_directory("../src", "demo_page_v2.html")

    @app.route("/demo")
    def serve_demo_alt():
        return send_from_directory("../src", "demo_page_v2.html")

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"})

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({"error": "File too large"}), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
