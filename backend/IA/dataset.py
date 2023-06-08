from pathlib import Path

from PIL import Image
from torch.nn.utils import Dataset
from torchvision.transforms.utils import to_tensor

from IA.iotofiles import safely_read



def process_PIL(pil_img):
    pil_img = pil_img.resize((224, 224))
    pil_img = pil_img.convert("RGB")  # needed to avoid grayscale
    pil_img = to_tensor(pil_img)
    return pil_img

class FullDataset:
    def __init__(self, annotation_file, datadir, extension='.jpg'):
        self.datadir = Path(datadir)
        self.files = sorted(self.datadir.glob(f'**/*{extension}'))
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

    def unlabeled_getitem(self, index):
        chosen_file = self.files[self.to_annotate_indices[index]]
        img = Image.open(chosen_file)
        img = process_PIL(img)
        return index, img

    def labeled_getitem(self, index):
        chosen_file = self.files[self.annotated_indices[index]]
        img = Image.open(chosen_file)
        img = process_PIL(img)
        return index, img, self.annotations[index]

    def len_unlabeled(self):
        return len(self.to_annotate_indices)
    
    def len_labeled(self):
        return len(self.annotated_indices)

    def get_unlabeled_ds(self):
        return UnlabeledDataset(self)

    def get_labeled_ds(self):
        return LabeledDataset(self)

# try to not edit these below
class UnlabeledDataset(Dataset):  
    def __init__(self, full_dataset):
        super().__init__()
        self.full_dataset = full_dataset

    def __getitem__(self, index):
        return self.full_dataset.unlabeled_getitem(index)

    def __len__(self):
        return self.full_dataset.len_unlabeled()

class LabeledDataset(Dataset):
    def __init__(self, full_dataset):
        super().__init__()
        self.full_dataset = full_dataset

    def __getitem__(self, index):
        return self.full_dataset.labeled_getitem(index)

    def __len__(self):
        return self.full_dataset.len_labeled()