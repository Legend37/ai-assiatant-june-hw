import cv2
import torch
import numpy as np
class LeNet(torch.nn.Module):
    def __init__(self, num_classes=10):
        super(LeNet, self).__init__()
        
        self.layer1 = torch.nn.Sequential(
            torch.nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2),
            torch.nn.BatchNorm2d(16),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))
        
        self.layer2 = torch.nn.Sequential(
            torch.nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            torch.nn.BatchNorm2d(32),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))
        
        self.layer3 = torch.nn.Sequential(
            torch.nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            torch.nn.BatchNorm2d(64),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))
        
        self.fc = torch.nn.Linear(3 * 3 * 64, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        return out
    
def pre_process(img, device):
    img = cv2.resize(img, (28, 28))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = img / 255
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device)
    img = img.float()
    img = img.unsqueeze(0)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)
    return img

def inference(model, img):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    img = pre_process(img, device)
    model.to(device)
    model.eval()
    preds = model(img)
    # preds is the outputs for a batch
    label = preds[0].argmax()
    return label

def image_classification(file_path):
    """
    使用LocalAI API调用LeNet模型对上传的MNIST手写数字图片进行分类
    
    Parameters:
        file_path: 上传的图片文件路径
        
    Returns:
        分类结果字符串
    """

    model = LeNet(num_classes=10)

    model_path="lenet.pth"
    load_dict = torch.load(model_path)
    model.load_state_dict(load_dict['state_dict'])

    img = cv2.imread(file_path, )
    label = inference(model, img)

    return f"Classification result: {label.item()}"
