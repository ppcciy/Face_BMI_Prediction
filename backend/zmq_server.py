import zmq
import logging

import io

from PIL import Image
from infer import predict, load_model
from config import ZMQ_HOST, ZMQ_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Loading model...")
    load_model()
    logger.info("Model loaded")

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{ZMQ_HOST}:{ZMQ_PORT}")
    logger.info(f"ZMQ inference server listening on tcp://{ZMQ_HOST}:{ZMQ_PORT}")

    try:
        while True:
            message = socket.recv()
            logger.info(f"Received image, {len(message)} bytes")

            image = Image.open(io.BytesIO(message))
            result = predict(image)
            socket.send_json(result)
    except KeyboardInterrupt:
        logger.info("Shutting down by user interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        socket.close()
        context.term()
        logger.info("ZMQ server stopped")


if __name__ == "__main__":
    main()
