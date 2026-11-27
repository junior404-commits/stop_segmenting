from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
from typing import Any
import torch
import numpy as np
from PIL import ImageTk, Image
import os
class ModelRoot():
    def __init__(self):
        #REQUIRED MODEL PATHS
        self.sam2_checkpoint = "checkpoints/sam2.1_hiera_large.pt"
        self.model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
        #IMAGE STATE
        self.selected_image_directory: str | None = None
        self.image_paths: list | None = None
        self.total_images: int | None = None
        self.current_image_index = -1
        self.current_image_path: str | None = None
        self.tk_image: ImageTk.PhotoImage | None = None 
        self.image_status = None
        self.image_error_status = None

        #MASK STATE
        self.tk_mask: ImageTk.PhotoImage | None = None
        self.current_mask_index = 0
        self.current_image_masks: Any | None = None
        self.total_masks: int | None = None
        self.current_mask_image = None
        self.mask_cache = {}

        #MODEL
        self.device: torch.device | None = None
        self.device_name: str | None = None
        self.model: Any | None = None
        self.mask_generator: SAM2AutomaticMaskGenerator | None = None
        self.model_status: bool | False = False
        self.model_error: Exception | None = None

        #MODEL PROCESSING
        self.is_processing = False
    ##############################################
    ##              FOLDER PROCESSING           ##
    ##############################################
    def set_image_directory(self, image_path: str):
        if image_path == "":
            self.selected_image_directory = None #self.selected_image_directory
            print(f"Selected Directory: {image_path}")
            print("ModelRoot> Path is None: Hardcoding path is an option")
        else:
            self.selected_image_directory = image_path
            print(f"Selected Directory: {image_path}")
            print("ModelRoot> Processing Files...")
            self._process_image_directory_files(image_path)
    
    def _process_image_directory_files(self, image_path) -> None:
        """Prepare Image Files"""
        image_files = []
        for image_file in os.listdir(image_path):
            if image_file.endswith('.jpg') or image_file.endswith('.jpeg') or image_file.endswith('.JPEG') or image_file.endswith('.tif') or image_file.endswith('.png'): #remove .png
                image_files.append(image_file)
        if not image_files:
            print("There are no images inside this directory: Exiting the routine.")
            return
        image_paths = []
        for image_file in image_files:
            image_paths.append(os.path.join(image_path, image_file))

        self.image_paths = image_paths
        self.total_images = len(image_paths)
        self.current_image_index = 0
        self.current_image_path = self.image_paths[self.current_image_index]
        print("Image files successfully processed...")

    
    ##############################################
    ##             IMAGE DISPLAY                ##
    ##############################################
    def display_tk_image(self):
        """This function must be called on the main thread. ImageTk.Object is being created and returned in this function, therefore, we must assume
        that this function will be called to create ImageTk.PhotoImage and return such object to manipulate GUI widget. Same goes for display_mask function.
        """
        print("ModelRoot.display_tk_image()> Retrieving Display Image")
        current_image_path = self.get_current_image_path()
        image = Image.open(current_image_path)
        self.tk_image = ImageTk.PhotoImage(image) #add self to avoid garbage collection
        return self.tk_image

    def display_mask(self):
        """This function must be called on the main thread.
        Retrieves an overlay of the original image and its corresonding mask components; Binded to ImageTk.PhotoImage for display.
        """
        cached_data = self.retrieve_generated_masks()
        if cached_data is None:
            print("ModelRoot> There are no masks for this particular image!")
            return None

        current_mask_overlay = cached_data.get('overlay')
        if current_mask_overlay is None:
            print("ModelRoot> No overlay exists for this image")
            return None

        self.tk_mask = ImageTk.PhotoImage(current_mask_overlay)
        return self.tk_mask
    ##############################################
    ##            MODEL INFERENCE               ##
    ##############################################
    def process_current_image(self):
        """Process the current image using the SAM2 model on a separate thread to avoid GUI crashes.
        Load the image, generate segmentation masks using SAM2, process and store the results for display
        """
        current_image_path = self.get_current_image_path()
        image = Image.open(current_image_path)
        image_array = np.array(image.convert("RGB"))
        try:
            with torch.inference_mode():
                print("ModelRoot> Activating Inference Mode...")
                generated_masks = self.mask_generator.generate(image_array)
                overlay = self._process_overlay(current_image_path, generated_masks) #return overlayed object.
                self._cache_generated_masks(current_image_path, generated_masks, overlay)
                self.set_image_processing_status(image_status = True, image_error_status = None)
                self.set_total_masks(len(generated_masks))
        except Exception as e:
           self.set_image_processing_status(image_status = False, image_error_status = e)
        print("image has finished processing")

    def _process_overlay(self, image_path, generated_masks, alpha = 0.5):
        """Return Overlay"""
        

        image = Image.open(image_path).convert('RGBA')
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)) #create overlay, we can add our additional alpha channel here to add transparency to the produced color for the segmentation layer.
        draw_overlay = np.array(overlay)
        for mask_data in generated_masks:
            segmentation = mask_data.get('segmentation')
            if segmentation is None:
                print("mask data is None for this index")
                continue
            color = np.random.randint(0, 255, size = 3) #choose random color
            draw_overlay[segmentation, 0] = color[0]
            draw_overlay[segmentation, 1] = color[1]
            draw_overlay[segmentation, 2] = color[2]
            draw_overlay[segmentation, 3] = int(255 * alpha)  # Opacity: segmentation transparancy, this requires an additional channel            
        mask_overlay_img = Image.fromarray(draw_overlay, "RGBA")
        final_image = Image.alpha_composite(image, mask_overlay_img) #background image -> image, foreground image -> mask overlay
        return final_image.convert('RGB')

    def _cache_generated_masks(self, image_path, generated_masks, overlay):
        """
        Save masks that have been generated for a particular set of images to dictionary.

        Input Args: 
            image_path: path to your images

            generated_masks: list of dictionaries
                Mask generation returns a list over masks, where each mask is a dictionary containing various data about the mask. These keys are:

                segmentation : the mask
                area : the area of the mask in pixels
                bbox : the boundary box of the mask in XYWH format
                predicted_iou : the model's own prediction for the quality of the mask
                point_coords : the sampled input point that generated this mask
                stability_score : an additional measure of mask quality
                crop_box : the crop of the image used to generate this mask in XYWH format
        """
        image_masks = {}
        for mask_index, mask_data in enumerate(generated_masks):
            segmentation = mask_data.get('segmentation')

            if segmentation is not None:
                image_masks[mask_index] = segmentation

        self.mask_cache[image_path] = {
            "masks": image_masks,
            "overlay": overlay
            }

    def retrieve_generated_masks(self):
        """Retrieve cached data for the currently selected image.."""
        current_image_path = self.get_current_image_path()
        return self.mask_cache.get(current_image_path)

    def has_cached_inference(self) -> bool:
        return self.retrieve_generated_masks() is not None

    def set_image_processing_status(self, image_status: bool, image_error_status: Exception) -> None:
        """
        Reset inference status before a new processing request. These objects are required for frontend POLLING technique.
        if image_status is true, model has successfully finished running inference on an image, and an overlay has been generated.
        If image_error_status is not None, issue running inference on image.
        """
        self.image_status = image_status
        self.image_error_status = image_error_status

    def reset_image_processing_status(self) -> None:
        """Reset inference status before a new processing request. These objects are required for frontend POLLING technique."""
        self.image_status = False
        self.image_error_status = None

    def set_total_masks(self, total_masks):
        self.total_masks = total_masks 

    def retrieve_total_masks(self) -> int:
        return len(self.total_masks)

    ##############################################
    ##                  DEVICE                  ##
    ##############################################
    def _select_torch_device(self) -> torch.device:
        if torch.cuda.is_available():
            device = torch.device('cuda')
            self.device_name = 'Cuda'
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
            self.device_name = 'mps'
        else:
            device = torch.device('cpu')
            self.device_name = 'CPU'
        self.device = device
        return device
    ##############################################
    ##                   MODEL                  ##
    ##############################################
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
            self.device_name = None
        
    def _build_sam_objects(self, model, mask_generator):
        print("SAM2 MODEL load successfully.")
        self.model = model
        self.mask_generator = mask_generator 
        self.model_status = True
    ##############################################
    ##            NEXT/PREVIOUS IMAGE`          ##
    ##############################################

    def set_previous_image_index(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
        return self.current_image_index
    
    def set_next_image_index(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
        return self.current_image_index

    def get_current_image_path(self):
        if not self.image_paths:
            return None
        self.current_image_path = self.image_paths[self.current_image_index]
        return self.current_image_path
    
    def get_current_image_paths(self):
        return self.image_paths
            
    def confirm(self):
        print("Model Layers confirmed")