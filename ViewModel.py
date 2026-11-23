from abc import ABC, abstractmethod
import threading
import Model

class ViewModel_Callbacks(ABC):
    """Trigger instantiation blocking until data is returned."""
    @abstractmethod
    def request_user_file(self, file_type):
        """Callback function for requesting user file."""
        pass

    @abstractmethod
    def request_user_directory(self):
        """Callback function for requesting User Directory."""
        pass

class ViewModelRoot():
    def __init__(self, callbacks):
        self.__callbacks = callbacks
        self.__modelroot = Model.ModelRoot()

    def _notify(self, message):
        """Provide Notifcations to the View State."""
        print(message)
               
    def select_directory(self):
        selected_directory = self.__callbacks.request_user_directory()
        self.__modelroot.set_image_directory(selected_directory)

    def get_selected_directory(self):
        if not self.__modelroot.selected_image_directory:
            return None
        return self.__modelroot.selected_image_directory

    def get_processed_image_paths(self):
        if not self.__modelroot.get_current_image_paths():
            return None
        return self.__modelroot.get_current_image_paths()

    #def get_processed_image_paths(self):
    #    return self.__modelroot.image_paths

    def start_model_loading(self):
        """Load SAM2 model on a separate thread."""
        #Create new thread to run model loading function
        try:
            threading.Thread(target = self.__modelroot.build_sam2_model, daemon = True).start() #shut down thread as soon as program finishes
        except Exception as e:
            self._notify(e)

    def process_current_image(self):
        """Process the current image that is on the Tkinter screen using a separate thread."""
        try:
            threading.Thread(target = self.__modelroot.process_current_image, daemon = True).start()
        except Exception as e:
            self._notify(e)

    def get_device_name(self) -> str | None:
        """Retrieve Device Name for GUI label.
        
        Return Type:
            Str or None
        """
        if self.__modelroot.device_name is None:
            return None
        return self.__modelroot.device_name
    
    def get_model_status(self):
        """Retrieve Model Status for GUI state.
        
        Return Type:
            bool, bool
        """
        return self.__modelroot.model_status, self.__modelroot.model_error

    def get_current_image_path(self):
        current_image_path = self.__modelroot.get_current_image_path()
        if not current_image_path:
            return None
        return current_image_path

    def get_image_processing_status(self):
        """Objects used for Polling Technique."""
        return self.__modelroot.image_status, self.__modelroot.image_error_status

    def retrieve_current_tkimage(self):
        """
            Return Type: ImageTk.PhotoImage
        """
        return self.__modelroot.display_tk_image()

    def retrieve_overlay_image(self):
        """        
            Return Type: ImageTk.PhotoImage
        """
        return self.__modelroot.display_mask()
    
    def get_current_image_index(self) -> int:
        """
        Retrieving current_image_index from Model.py for
        tkinter Image status label.
        """
        return self.__modelroot.current_image_index

    def get_total_masks(self) -> int | None:
        """
        Retrieving current_mask_index, and total_masks from Model.py for
        tkinter mask_label
        
        """
        return self.__modelroot.total_masks

    def get_image_path_info(self):
        """update controls
        find a better name for this function
        """
        return self.__modelroot.current_image_index, self.__modelroot.total_images

    def set_previous_image_index(self):
        """decrement the current_image_index. This object will be used to update the current image path."""
        self.__modelroot.set_previous_image_index()

    def set_next_image_index(self):
        self.__modelroot.set_next_image_index()

    def confirm(self):
        self.__modelroot.confirm()