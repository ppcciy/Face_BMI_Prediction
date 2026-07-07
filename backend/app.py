import io
import zmq
import logging

from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import ZMQ_HOST, ZMQ_PORT, ZMQ_TIMEOUT_MS, FLASK_HOST, FLASK_PORT

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

zmq_context = zmq.Context()


def get_zmq_socket():
    socket = zmq_context.socket(zmq.REQ)
    socket.connect(f"tcp://{ZMQ_HOST}:{ZMQ_PORT}")
    socket.setsockopt(zmq.RCVTIMEO, ZMQ_TIMEOUT_MS)
    socket.setsockopt(zmq.SNDTIMEO, ZMQ_TIMEOUT_MS)
    return socket


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "BMI Prediction Server Running"})


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image field in request"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No selected image"}), 400

    image_bytes = file.read()
    if not image_bytes:
        return jsonify({"success": False, "message": "Empty image data"}), 400

    try:
        Image.open(io.BytesIO(image_bytes))
    except Exception:
        return jsonify({"success": False, "message": "Cannot open image, invalid format"}), 400

    socket = None
    try:
        socket = get_zmq_socket()
        socket.send(image_bytes)
        reply = socket.recv_json()
    except zmq.Again:
        logger.error("ZMQ timeout: inference server not responding")
        return jsonify({"success": False, "message": "Inference server timeout"}), 504
    except Exception as e:
        logger.error(f"ZMQ communication error: {e}")
        return jsonify({"success": False, "message": f"Inference server error: {e}"}), 500
    finally:
        if socket is not None:
            socket.close()

    if not reply.get("success"):
        return jsonify({"success": False, "message": reply.get("message", "Prediction failed")}), 422

    return jsonify({"success": True, "bmi": reply["bmi"]})


if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
