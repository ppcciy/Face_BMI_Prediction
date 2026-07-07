# Face BMI Prediction

> 基于深度学习的人脸 BMI（Body Mass Index）预测系统

![Python](https://img.shields.io/badge/Python-3.10-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)
![Vue3](https://img.shields.io/badge/Vue3-Frontend-42b883)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 项目简介

Face BMI Prediction 是一个基于深度学习的人脸 BMI 预测系统。

项目利用 **MTCNN** 进行人脸检测，结合 **EfficientNet** 网络预测人体 BMI，并采用 **Flask + ZeroMQ + Vue3** 构建完整的前后端推理系统，实现图片上传、模型推理及 BMI 可视化展示。

整个项目包含：

* 数据预处理
* 模型训练
* 模型测试
* Flask 后端
* ZeroMQ 推理服务
* Vue3 前端界面

---

## 项目特点

✔ EfficientNet 迁移学习

✔ MTCNN 自动人脸检测

✔ GPU 加速推理（CUDA）

✔ Flask REST API

✔ ZeroMQ 高性能通信

✔ Vue3 + Element Plus 前端

✔ 前后端完全分离

---

## 系统架构

```text
                上传图片
                   │
                   ▼
           Vue3 Frontend
                   │
              HTTP Request
                   │
                   ▼
              Flask Backend
                   │
                 ZeroMQ
                   │
                   ▼
           Inference Server
                   │
         MTCNN Face Detection
                   │
                   ▼
          EfficientNet Model
                   │
                   ▼
            BMI Prediction
                   │
                   ▼
             返回预测结果
```

---

## 项目结构

```text
Face_BMI_Prediction
│
├── backend
│   ├── app.py                # Flask API
│   ├── zmq_server.py         # ZeroMQ 推理服务
│   ├── infer.py              # 推理流程
│   ├── model.py              # EfficientNet 模型
│   ├── config.py
│   └── requirements.txt
│
├── frontend
│   ├── src
│   ├── public
│   └── package.json
│
├── data
│   ├── bmi.csv
│   └── front
│
├── traincode.py              # 模型训练
├── test.py                   # 单张图片测试
└── README.md
```

---

## 技术栈

### 深度学习

* PyTorch
* torchvision
* EfficientNet
* MTCNN

### 后端

* Flask
* ZeroMQ
* Pillow

### 前端

* Vue3
* Vite
* Axios
* Element Plus

---

## 数据集

本项目使用 Illinois DOC Labeled Faces Dataset。数据集包含超过 6 万张人脸图像，并提供 BMI、身高、体重等标签信息。

训练过程中：

* 删除 BMI 缺失样本
* 去除异常 BMI 数据
* 仅使用正面人脸图像
* Resize 到 224×224

数据划分：

```text
Train : 70%
Validation : 15%
Test : 15%
```

---

## 模型

目前支持：

| Model           | Status |
| --------------- | ------ |
| ResNet18        | ✓      |
| EfficientNet-B0 | ✓      |
| EfficientNet-B3 | ✓ 推荐   |

采用迁移学习，仅替换最后全连接层进行 BMI 回归预测。

损失函数：

```
SmoothL1Loss
```

优化器：

```
AdamW
```

学习率调度：

```
ReduceLROnPlateau
```

---

## 环境配置

Python

```
3.10
```

安装依赖

```bash
pip install -r backend/requirements.txt
```

---

## 模型训练

```bash
python traincode.py
```

训练过程中将：

* 保存最佳模型
* 输出 Train Loss
* 输出 Validation Loss
* 输出 Validation MAE

---

## 启动系统

### ① 启动推理服务器

```bash
cd backend

python zmq_server.py
```

### ② 启动 Flask

```bash
cd backend

python app.py
```

### ③ 启动 Vue

```bash
cd frontend

npm install

npm run dev
```

浏览器访问

```
http://localhost:3000
```

---

## 效果展示
<img width="2560" height="1528" alt="36f708ef41f6e6e9b6472afd57a3ca18" src="https://github.com/user-attachments/assets/6649d410-9792-4d98-b251-3c20e4bb8ebf" />

---

## 后续优化方向

* 支持多人脸检测
* Grad-CAM 可解释性分析
* ONNX / TensorRT 部署
* Docker 一键部署
* FastAPI 替代 Flask
* 支持批量图片预测
* 在线摄像头实时预测

---

## License

MIT License
