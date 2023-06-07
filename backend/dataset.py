import os
from pathlib import Path

from PIL import Image
from torchvision.transforms.functional import to_tensor
from torch.utils.data import Dataset


class CatsAndDogsDataset(Dataset):
    def __init__(self, path):
        self.path = Path(path)
        self.files = [
            self.path / "Cat" / file
            for file in os.listdir(self.path / "Cat")
            if file.endswith(".jpg")
        ] + [
            self.path / "Dog" / file
            for file in os.listdir(self.path / "Dog")
            if file.endswith(".jpg")
        ]
        self.indices = list(range(len(self.files)))
        self.targets = [0] * len(os.listdir(self.path / "Cat")) + [1] * len(
            os.listdir(self.path / "Dog")
        )

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        img = Image.open(self.files[index])
        img = img.resize((224, 224))
        img = img.convert("RGB")  # needed to avoid grayscale
        img = to_tensor(img)
        target = self.targets[index]
        return index, img, target
