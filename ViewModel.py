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

    def select_directory(self):
        selected_directory = self.__callbacks.request_user_directory()
        print(selected_directory)
        #self.__modelroot.set_image_directory(selected_directory)

    def _notify(self, message):
        print(message)
        
    def start_model_loading(self):
        """Load SAM2 model on a separate thread."""
        #Create new thread to run model loading function
        try:
            threading.Thread(target = self.__modelroot.build_sam2_model, daemon = True).start() #shut down thread as soon as program finishes
        except Exception as e:
            self._notify(e)

    def get_device_name(self):
        """Retrieve Device Name for GUI STATE
        
        Return Type:
            str
        """
        return self.__modelroot.device_name
    def get_model_status(self):
        """Retrieve Model Status for GUI state.
        
        Return Type:
            bool, bool
        """
        return self.__modelroot.model_status, self.__modelroot.model_error
            
    def confirm(self):
        self.__modelroot.confirm()