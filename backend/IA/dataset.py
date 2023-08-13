print('importing packages in dataset.py')
import random
from pathlib import Path
import collections.abc

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

class OrderedSet(collections.abc.Set):
    def __init__(self, iterable=()):
        self.d = collections.OrderedDict.fromkeys(iterable)

    def __len__(self):
        return len(self.d)

    def __contains__(self, element):
        return element in self.d

    def __iter__(self):
        return iter(self.d)

class FullDataset:
    def __init__(self, skipped_file: str, annotation_file: str, datadir: str, extensions: list[str] = [".jpg", ".png"]):
        self.datadir = Path(datadir)
        # select files that have the right extension
        self.files = []
        for extension in extensions:
            self.files.extend(list(self.datadir.glob(f"**/*{extension}")))
        self.files = map(str, self.files)
        self.files = sorted(self.files)
        print(f"{len(self.files)} files found in {self.datadir}")
        assert len(self.files) > 0, f"no files found in {self.datadir}"
        random.seed(0)  # make them mixed, the problem has little sense if not
        random.shuffle(self.files)
        # self.indices = list(range(len(self.files)))
        self.annotation_file = Path(annotation_file)
        self.skipped_file = Path(skipped_file)
        self.refresh()

    def refresh(self):
        if not self.annotation_file.exists():
            self.annotations = {}
        else:
            self.annotations = safely_read(self.annotation_file)
        if not self.skipped_file.exists():
            self.skipped_paths = {}
        else:
            self.skipped_paths = safely_read(self.skipped_file)

        self.annotated_paths = list(self.annotations.keys())
        self.to_annotate_paths = list(OrderedSet(self.files) - OrderedSet(self.annotated_paths) - OrderedSet(self.skipped_paths))

    def unlabeled_getitem(self, index: int) -> (int, str, torch.Tensor):
        chosen_file = self.to_annotate_paths[index]
        img = Image.open(chosen_file)
        img = process_PIL(img)
        return index, str(chosen_file), img

    def labeled_getitem(self, index: int) -> (int, str, torch.Tensor, int):
        chosen_file = self.annotated_paths[index]
        img = Image.open(chosen_file)
        img = process_PIL(img)
        label = self.annotations[chosen_file]
        return index, str(chosen_file), img, label

    def len_unlabeled(self) -> int:
        return len(self.to_annotate_paths)

    def len_labeled(self) -> int:
        return len(self.annotated_paths)

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

    def __getitem__(self, index: int) -> (int, str, torch.Tensor):
        return self.full_dataset.unlabeled_getitem(index)

    def __len__(self) -> int:
        return self.full_dataset.len_unlabeled()


class LabeledDataset(Dataset):
    def __init__(self, full_dataset: FullDataset):
        super().__init__()
        self.full_dataset = full_dataset

    def __getitem__(self, index: int) -> (int, str, torch.Tensor, int):
        return self.full_dataset.labeled_getitem(index)

    def __len__(self) -> int:
        return self.full_dataset.len_labeled()
