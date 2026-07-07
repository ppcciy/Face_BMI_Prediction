import torch.nn as nn
from torchvision import models
from torchvision.models import EfficientNet_B3_Weights


class BMI_EfficientNet(nn.Module):

    def __init__(self):
        super().__init__()

        self.model = models.efficientnet_b3(
            weights=EfficientNet_B3_Weights.DEFAULT
        )

        in_features = self.model.classifier[1].in_features

        self.model.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(in_features, 1)
        )

    def forward(self, x):
        return self.model(x).squeeze()
