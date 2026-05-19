import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import time


def main():
    # 1. 장치 설정
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"사용 장치: {device}")

    # 2. 데이터 로딩 (CIFAR-10 + augment)
    transform = transforms.Compose(
        [
            transforms.RandomHorizontalFlip(),
            transforms.RandomCrop(32, padding=4),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),  # RGB 3채널
        ]
    )

    train_dataset = datasets.CIFAR10(
        root="./data", train=True, download=True, transform=transform
    )
    train_loader = DataLoader(
        train_dataset, batch_size=512, shuffle=True, num_workers=4, pin_memory=True
    )

    # 3. 모델: ResNet18 사용 (CIFAR-10용으로 수정)
    model = models.resnet18(pretrained=False)

    # CIFAR-10 (32x32)을 위해 첫 번째 conv layer 수정
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()  # maxpool 제거 (작은 이미지에서 불필요)
    model.avgpool = nn.AdaptiveAvgPool2d((1, 1))  # avgpool을 adaptive로 변경

    model.fc = nn.Linear(model.fc.in_features, 10)  # CIFAR-10은 10개 클래스
    model = model.to(device)

    # 4. 손실함수 및 옵티마이저
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 5. 학습 (10 epochs)
    print("ResNet18 학습 시작 (10 epochs)...")
    model.train()
    for epoch in range(10):
        stime = time.time()
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device, non_blocking=True), target.to(
                device, non_blocking=True
            )

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            if batch_idx % 20 == 0:
                print(
                    f"[Epoch {epoch+1}/10] Batch {batch_idx}, Loss: {loss.item():.4f}"
                )
        etime = time.time()
        print(f"[Epoch {epoch+1}/10] Time: {etime - stime:.2f} seconds")
    print("ResNet18 학습 완료.")


# ⚠️ Windows에서 multiprocessing 안전하게 실행하는 필수 구조
if __name__ == "__main__":
    main()
