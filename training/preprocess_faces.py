import os
import pandas as pd
import torch
from PIL import Image
from facenet_pytorch import MTCNN

mtcnn = MTCNN(keep_all=False, device='cuda' if torch.cuda.is_available() else 'cpu')

input_dir = r'E:\Desktop\Face_BMI_Prediction\data\front\front'
output_dir = r'E:\Desktop\Face_BMI_Prediction\data\front\processed'

os.makedirs(output_dir, exist_ok=True)

csv_file = r'E:\Desktop\Face_BMI_Prediction\data\bmi.csv'
df = pd.read_csv(csv_file)

for i, row in df.iterrows():
    img_id = str(row["id"])
    path = os.path.join(input_dir, img_id + ".jpg")

    img = Image.open(path).convert("RGB")

    boxes, _ = mtcnn.detect(img)

    if boxes is not None:
        x1, y1, x2, y2 = boxes[0]
        face = img.crop((x1, y1, x2, y2))
    else:
        face = img  # 检测失败直接用原图

    face = face.resize((240, 320))

    face.save(os.path.join(output_dir, img_id + ".jpg"))