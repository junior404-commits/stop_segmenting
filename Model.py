from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
from typing import Any
import torch
class ModelRoot():
    def __init__(self):
        self.sam2_checkpoint = "checkpoints/sam2.1_hiera_large.pt"
        self.model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"

        self.device: torch.device | None = None
        self.device_name: str | None = None
        self.model: Any | None = None
        self.mask_generator: SAM2AutomaticMaskGenerator | None = None
        self.model_status: bool | False = False
        self.model_error: Exception | None = None

    def _select_torch_device(self) -> torch.device:
        if torch.cuda.is_available():
            device = torch.device('cuda')
            self.device_name = 'cuda'
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
            self.device_name = 'mps'
        else:
            device = torch.device('cpu')
            self.device_name = 'cpu'
        self.device = device

    def build_sam2_model(self):
        """Attempt to build SAM2 model on separate thread."""
        try:
            device = self._select_torch_device()
            model = build_sam2(self.model_cfg, self.sam2_checkpoint, device = device)
            mask_generator = SAM2AutomaticMaskGenerator(model = model)
            self._build_sam_objects(model, mask_generator)
        except Exception as e:
            print(f"There was an error loading the model: {e}")
            self.model_error = e
        
    def _build_sam_objects(self, model, mask_generator):
        print("SAM2 MODEL load successfully.")
        self.model = model
        self.mask_generator = mask_generator 
        self.model_status = True
        
    def confirm(self):
        print("Model Layers confirmed")