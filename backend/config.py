import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "EfficientNetB3_model.pth")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ZMQ_HOST = "127.0.0.1"
ZMQ_PORT = 5555
ZMQ_TIMEOUT_MS = 30000

MTCNN_EXPAND_RATIO = 0.2

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
