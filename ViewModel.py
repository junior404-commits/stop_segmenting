from abc import ABC, abstractmethod
import threading
import Model
class ViewModelRoot:
    def __init__(self, callbacks):
        self.__callbacks = callbacks
        self.__modelroot = Model.ModelRoot()

    def _notify(self, message):

        print("functions")
        
    def start_model_loading(self):
        """Load SAM2 model on a separate thread."""
        #Create new thread to run model loading function
        try:
            model_thread = threading.Thread(target = self.__modelroot.build_sam2_model(), daemon = True) #shut down thread as soon as program finishes
            model_thread.start()
        except Exception as e:
            self._notify(e)

    def get_model_status(self):
        return self.__modelroot.model_status
            
    def confirm(self):
        self.__modelroot.confirm()