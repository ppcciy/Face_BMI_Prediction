import torch
from torchvision import transforms
from facenet_pytorch import MTCNN
from PIL import Image

from model import BMI_EfficientNet
from config import MODEL_PATH, DEVICE, MTCNN_EXPAND_RATIO

_mtcnn = None
_model = None
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def load_model():
    global _mtcnn, _model

    _mtcnn = MTCNN(device=DEVICE)

    _model = BMI_EfficientNet().to(DEVICE)
    _model.load_state_dict(
        torch.load(MODEL_PATH, map_location=DEVICE)
    )
    _model.eval()


def detect_and_crop_face(image, expand=MTCNN_EXPAND_RATIO):
    boxes, _ = _mtcnn.detect(image)

    if boxes is None or len(boxes) == 0:
        return None

    x1, y1, x2, y2 = boxes[0]
    w = x2 - x1
    h = y2 - y1

    x1 = max(0, x1 - expand * w)
    y1 = max(0, y1 - expand * h)
    x2 = min(image.width, x2 + expand * w)
    y2 = min(image.height, y2 + expand * h)

    return image.crop((x1, y1, x2, y2))


def predict(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    face = detect_and_crop_face(image)
    if face is None:
        return {"success": False, "message": "No face detected"}

    tensor = _transform(face).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        bmi = _model(tensor)

    return {"success": True, "bmi": round(float(bmi.item()), 2)}
