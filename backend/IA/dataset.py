print('importing packages in dataset.py')
import random
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms.functional import to_tensor

from IA.iotofiles import safely_read
print('finished importing packages in dataset.py')


def process_PIL(pil_img: Image) -> torch.Tensor:
    pil_img = pil_img.resize((224, 224))
    pil_img = pil_img.convert("RGB")  # needed to avoid grayscale
    return to_tensor(pil_img)


class FullDataset:
    def __init__(self, annotation_file: str, datadir: str, extensions: list[str] = [".jpg", ".png"]):
        self.datadir = Path(datadir)
        # select files that have the right extension
        self.files = []
        for extension in extensions:
            self.files.extend(list(self.datadir.glob(f"**/*{extension}")))
        self.files = sorted(self.files)
        print(f"{len(self.files)} files found in {self.datadir}")
        assert len(self.files) > 0, f"no files found in {self.datadir}"
        random.seed(0)  # make them mixed, the problem has little sense if not
        random.shuffle(self.files)
        self.indices = list(range(len(self.files)))
        self.annotation_file = Path(annotation_file)
        self.refresh()

    def refresh(self):
        if not self.annotation_file.exists():
            self.annotations = {}
        else:
            self.annotations = safely_read(self.annotation_file)
        self.annotated_indices = list(self.annotations.keys())
        self.to_annotate_indices = list(set(self.indices) - set(self.annotated_indices))

    def unlabeled_getitem(self, index: int) -> (int, str, torch.Tensor):
        chosen_file = self.files[self.to_annotate_indices[index]]
        img = Image.open(chosen_file)
        img = process_PIL(img)
        return index, str(chosen_file), img

    def labeled_getitem(self, index: int) -> (int, str, torch.Tensor, int):
        chosen_file = self.files[self.annotated_indices[index]]
        img = Image.open(chosen_file)
        img = process_PIL(img)
        label = self.annotations[self.annotated_indices[index]]
        return index, str(chosen_file), img, label

    def len_unlabeled(self) -> int:
        return len(self.to_annotate_indices)

    def len_labeled(self) -> int:
        return len(self.annotated_indices)

    def __len__(self) -> int:
        return len(self.files)

    def get_unlabeled_ds(self) -> Dataset:
        return UnlabeledDataset(self)

    def get_labeled_ds(self) -> Dataset:
        return LabeledDataset(self)


# try to not edit these below
class UnlabeledDataset(Dataset):
    def __init__(self, full_dataset: FullDataset):
        super().__init__()
        self.full_dataset = full_dataset

    def __getitem__(self, index: int) -> (int, Path, torch.Tensor):
        return self.full_dataset.unlabeled_getitem(index)

    def __len__(self) -> int:
        return self.full_dataset.len_unlabeled()


class LabeledDataset(Dataset):
    def __init__(self, full_dataset: FullDataset):
        super().__init__()
        self.full_dataset = full_dataset

    def __getitem__(self, index: int) -> (int, Path, torch.Tensor, int):
        return self.full_dataset.labeled_getitem(index)

    def __len__(self) -> int:
        return self.full_dataset.len_labeled()
