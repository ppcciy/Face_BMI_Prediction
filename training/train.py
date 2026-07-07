import os
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader, Subset
from PIL import Image
from torchvision import transforms
from torchvision import models
from torchvision.models import EfficientNet_B3_Weights
from torchvision.models import ResNet18_Weights
import torch.nn as nn
from torch.optim import AdamW
from tqdm import tqdm
from facenet_pytorch import MTCNN
import torch.optim.lr_scheduler as lr_scheduler
import matplotlib.pyplot as plt
from torch.utils.data import random_split


# 初始化列表来保存损失值
train_losses = []
valid_losses = []

# 初始化 MTCNN 检测器
target_size = (240, 320)

# 检查是否有可用的 GPU
if torch.cuda.is_available():
    available_gpus = torch.cuda.device_count()
    print(f"Available GPUs: {available_gpus}")
    device = torch.device("cuda:0")
    gpu_name = torch.cuda.get_device_name(device)
    print(f"Using GPU: {gpu_name}")
else:
    device = torch.device("cpu")


# 自定义数据集类
class BMI_Dataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.data_frame = pd.read_csv(csv_file)
        # 删除BMI为空的数据
        self.data_frame = self.data_frame.dropna(subset=["bmi"])
        # 确保BMI为float
        self.data_frame["bmi"] = self.data_frame["bmi"].astype(float)
        # 确保id为字符串
        self.data_frame["id"] = self.data_frame["id"].astype(str)
        # 过滤异常样本
        self.data_frame = self.data_frame[
            (self.data_frame["bmi"] >= 10) &
            (self.data_frame["bmi"] <= 60)
        ]
        print("有效样本数：", len(self.data_frame))
        self.root_dir = root_dir
        self.transform = transform
       
    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        image_id = self.data_frame.iloc[idx]["id"]
        img_name = os.path.join(
            self.root_dir,
            image_id + ".jpg"
        )
       
        image = Image.open(img_name).convert("RGB")

        bmi = self.data_frame.iloc[idx]["bmi"]

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(bmi, dtype=torch.float32)

class TransformDataset(Dataset):
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        image, bmi = self.subset[idx]

        if self.transform:
            image = self.transform(image)

        return image, bmi

# 数据集路径
csv_file = r'E:\Desktop\Face_BMI_Prediction\data\bmi.csv'
root_dir = r'E:\Desktop\Face_BMI_Prediction\data\front\processed'


train_transform = transforms.Compose([

    transforms.Resize((300,300)),

    transforms.RandomHorizontalFlip(p=0.5),

    transforms.RandomRotation(5),

    transforms.RandomAffine(
        degrees=0,
        translate=(0.05,0.05),
        scale=(0.95,1.05)
    ),

    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),

     transforms.RandomPerspective(
        distortion_scale=0.15,
        p=0.3
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    ),

    transforms.RandomErasing(
        p=0.25,
        scale=(0.02,0.08)
    )

])

valid_transform = transforms.Compose([

    transforms.Resize((300,300)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])


full_dataset = BMI_Dataset(
    csv_file,
    root_dir,
    transform=None
)

train_size = int(len(full_dataset) * 0.7)
val_size = int(len(full_dataset) * 0.15)
test_size = len(full_dataset) - train_size - val_size

train_subset, val_subset, test_subset = random_split(
    full_dataset,
    [train_size, val_size, test_size],
    generator=torch.Generator().manual_seed(42)
)

train_dataset = TransformDataset(train_subset,train_transform)
val_dataset = TransformDataset(val_subset,valid_transform)
test_dataset = TransformDataset(test_subset,valid_transform)

train_loader = DataLoader(
    train_dataset,
    batch_size=16,
    shuffle=True,
    num_workers=0,
    pin_memory=True
)

valid_loader = DataLoader(
    val_dataset,
    batch_size=16,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=16,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)

""" # 使用预训练的 ResNet18
class BMI_ResNet(nn.Module):
    def __init__(self):
        super(BMI_ResNet, self).__init__()
        self.resnet = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        # 修改最后的全连接层
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, 1)

    def forward(self, x):
        out = self.resnet(x)
        return out.squeeze()
 """

""" class BMI_EfficientNet(nn.Module):

    def __init__(self):
        super().__init__()

        self.model = models.efficientnet_b0(
            weights=EfficientNet_B0_Weights.DEFAULT
        )

        in_features = self.model.classifier[1].in_features

        self.model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features,1)
        )

    def forward(self,x):
        return self.model(x).squeeze()"""

class BMI_EfficientNet(nn.Module):

    def __init__(self):
        super().__init__()

        self.model = models.efficientnet_b3(
            weights=EfficientNet_B3_Weights.DEFAULT
        )

        in_features = self.model.classifier[1].in_features

        self.model.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(in_features,1)
        )

    def forward(self,x):
        return self.model(x).squeeze()
    
# 实例化模型并将其移动到 GPU
# model = BMI_ResNet().to(device)
model = BMI_EfficientNet().to(device)

# 损失函数和优化器
# criterion = nn.MSELoss()
criterion = nn.SmoothL1Loss(beta=1.0)
optimizer=AdamW(
    model.parameters(),
    lr=1e-4,
    weight_decay=1e-4
)

# 学习率调度器
scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(

    optimizer,
    T_max=30,
    eta_min=1e-6

)

# 训练轮数
num_epochs = 30

# 记录最佳验证损失
best_loss = float("inf")
patience=5
counter=0

# 训练过程
for epoch in range(num_epochs):
    model.train()  
    running_loss = 0.0

    # 使用 tqdm 包装 data_loader，显示训练进度
    for images, bmis in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}'):
        images = images.to(device)  # 将图像数据移动到 GPU
        bmis = bmis.to(device)  # 将 BMI 标签移动到 GPU

        optimizer.zero_grad()  # 清空梯度

        outputs = model(images)  # 前向传播
        outputs = outputs.squeeze()  # 输出从 (batch_size, 1) 调整为 (batch_size,)

        loss = criterion(outputs, bmis)  # 计算损失
        loss.backward()  # 反向传播
        optimizer.step()  # 更新参数

        # 累加训练损失
        running_loss += loss.item()

    # 计算并记录训练损失
    avg_train_loss = running_loss / len(train_loader)
    train_losses.append(avg_train_loss)

    # 验证过程
    model.eval()  # 设置模型为评估模式
    valid_loss = 0.0
    valid_mae = 0.0
    with torch.no_grad():
        for images, bmis in tqdm(valid_loader, desc=f'Validation Epoch {epoch+1}/{num_epochs}'):
            images = images.to(device)
            bmis = bmis.to(device)

            outputs = model(images)
            outputs = outputs.squeeze()

            loss = criterion(outputs, bmis)
            valid_loss += loss.item()

            mae = torch.mean(torch.abs(outputs - bmis))
            valid_mae += mae.item()

    avg_valid_loss = valid_loss / len(valid_loader)
    avg_valid_mae = valid_mae / len(valid_loader)
    valid_losses.append(avg_valid_loss)

    # 如果当前模型更好，则保存
    if avg_valid_loss < best_loss:
        best_loss = avg_valid_loss
        counter = 0
        torch.save(
            model.state_dict(),
            r"E:\Desktop\Face_BMI_Prediction\EfficientNetB3_model.pth"
        )
        print(f"保存最佳模型，Validation Loss = {best_loss:.4f}")
    else:
        counter += 1
        print(f"EarlyStopping {counter}/{patience}")
        if counter >= patience:
            print("提前停止训练")
            break

    # 更新学习率
    scheduler.step()

    # 打印每个 epoch 的损失
    print(
        f"Epoch [{epoch+1}/{num_epochs}] "
        f"Train Loss: {avg_train_loss:.4f} "
        f"Validation Loss: {avg_valid_loss:.4f} "
        f"Validation MAE: {avg_valid_mae:.4f}"
    )

print("\n========== Test ==========")

model.load_state_dict(
    torch.load(
        r"E:\Desktop\Face_BMI_Prediction\EfficientNetB3_model.pth"
    )
)

model.eval()

test_mae = 0
test_loss = 0

with torch.no_grad():

    for images,bmis in test_loader:

        images = images.to(device)
        bmis = bmis.to(device)

        outputs = model(images).squeeze()

        loss = criterion(outputs,bmis)

        test_loss += loss.item()

        mae = torch.mean(torch.abs(outputs-bmis))

        test_mae += mae.item()

print("Test Loss:",test_loss/len(test_loader))
print("Test MAE :",test_mae/len(test_loader))