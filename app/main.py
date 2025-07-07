from flask import Flask, jsonify
import logging
import os
import time
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Application metadata
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
START_TIME = datetime.utcnow()


@app.route("/")
def home():
    logger.info("Home endpoint accessed")
    return "Hello from Flask CI/CD!"


@app.route("/health")
def health():
    """Health check endpoint for container orchestration"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": APP_VERSION
    }), 200


@app.route("/ready")
def ready():
    """Readiness check endpoint"""
    # Add any dependency checks here (database, external APIs, etc.)
    return jsonify({
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - START_TIME).total_seconds()
    }), 200


@app.route("/metrics")
def metrics():
    """Basic metrics endpoint (Prometheus format would be better)"""
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    return jsonify({
        "uptime_seconds": uptime,
        "version": APP_VERSION,
        "start_time": START_TIME.isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info(f"Starting Flask app version {APP_VERSION}")
    app.run(host="0.0.0.0", port=5000, debug=False)
