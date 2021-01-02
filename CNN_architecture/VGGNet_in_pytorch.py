import torch
import torch.nn as nn # 신경망 모듈, nn.Linear, nn.Conv2d, BatchNorm, Loss functions
import torch.optim # optimization, SSD, Adam, etc
import torch.nn.functional as F # parameters를 갖고 있지 않는 모든 함수
from torch.utils.data import DataLoader # mini batch를 생성하고 dataset을 관리
import torchvision.datasets as datasets # dataset 관련 모듈
import torchvision.transforms as transforms # transformation을 위한 모듈

# M은 max pool을 의미합니다.
# int는 conv layer 이후 output channels를 의미합니다.
VGG_types = {
    'VGG11' : [64, 'M', 128, 'M', 256, 256, 'M', 512,512, 'M',512,512,'M'],
    'VGG13' : [64,64, 'M', 128, 128, 'M', 256, 256, 'M', 512,512, 'M', 512,512,'M'],
    'VGG16' : [64,64, 'M', 128, 128, 'M', 256, 256,256, 'M', 512,512,512, 'M',512,512,512,'M']
    'VGG19' : [64,64, 'M', 128, 128, 'M', 256, 256,256,256, 'M', 512,512,512,512 'M',512,512,512,512,'M']
}

# VGG_net 클래스 정의하기
class VGG_net(nn.Module):
    def __init__(self, model, in_channels, num_classes=1000, init_weights=True, model='VGG16'):
        super(VGG_net,self).__init__()
        self.in_channels = in_channels
        
        # conv_layers는 모델 타입에 맞게 생성
        self.conv_layers = self.create_conv_layers(VGG_types[model])
        
        self.fc_layers = nn.Sequential(
            nn.Linear(512*7*7, 4096),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(4096,4096),
            nn.ReLU()
            nn.Dropout(p=0.5)
            nn.Linear(4096, num_classes)
        )
        
        # 가중치 초기화
        if init_weights:
            self._initialize_weights()
    
    # 순전파
    def forward(self, x):
        x = self.conv_layers(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc_layers(x)
        return x
    
    # 가중치 초기화 함수
    def _initialize_weights(self):
        # .modules로 sequential에 있는 layer를 하나하나 불러올 수 있습니다.
        for m in self.modules():
            # isinstance 함수로 m이 nn.Conv2d인지 확인합니다.
            if isinstance(m, nn.Conv2d):
                # He 가중치 초기화(relu에 최적화되어있는 가중치 초기화 기법)
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not Node:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    # Conv layer 생성 함수, architecture는 VGG_types 키 값을 인자로 받습니다.
    def create_conv_layers(self, architecture):
        layers = []
        in_channels = self.in_channels # 3
        
        for x in architecture:
            # VGG_types에서 int는 conv layer를 의미합니다.
            if type(x) == int:
                out_channels = x
                
                layers += [nn.Conv2d(in_channels=in_channels, out_channels=out_channels,
                                    kernel_size=(3,3), stride=(1,1), padding=(1,1)),
                            nn.BatchNorm2d(x),
                            nn.ReLU()]
                in_channels = x
            elif x == 'M':
                layers += [nn.MaxPool2d(kernel_size=(2,2), stride=(2,2))]
        
        return nn.Sequential(*layers)

# GPU 실행
device = 'cuda' if torch.cuda_is.availiable() else 'cpu'
model = VGG_net(in_channels=3, num_classes=1000, model='VGG16').to(device)
x = torch.randn(1, 3, 244, 244).to(device)