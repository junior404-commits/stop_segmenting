"""
  ____    _    __  __ ____
 / ___|  / \  |  \/  |___ \
 \___ \ / _ \ | |\/| | __) |
  ___) / ___ \| |  | |/ __/
 |____/_/   \_\_|  |_|_____|

+---------------------------------------------------+
|           SAM2 IMAGE SEGMENTATION GUI             |
|---------------------------------------------------|
|     AI-POWERED IMAGE SEGMENTATION & MASKING       |
|                                                   |
|   [ IMAGE INPUT ]  --->  [ SEGMENTATION MASK ]    |
|                                                   |
|   Model: Segment Anything Model 2 (SAM2)          |
|   Interface: Python / Tkinter                     |
|   Architecture: MVVM                              |
|   Dev: Ernesto Ordonez                            |
+---------------------------------------------------+
"""

import ViewModel
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk, Image

class MainController_Callback():
    """
    BASED OFF .NET C# MVVM DOCUMENTATION
    """
    def request_user_file(self, file_type):
        return filedialog.askopenfilename(file_type=[(file_type + ' files', '*.' + file_type)])

    def request_user_directory(self):
        return filedialog.askdirectory()

class MainController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.view_model = ViewModel.ViewModelRoot(MainController_Callback())
        
        screen_width = 1250 #self.winfo_screenwidth()
        screen_height = 850 #self.winfo_screenheight()
        self.minsize(950, 650)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        #set geometry
        self.geometry(f"{screen_width}x{screen_height}+0+0") #+0+0
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        #example_display_container = tk.Frame(self, bg = 'lightblue', width = 200, height = 100, relief = tk.RIDGE)
        container = tk.Frame(self)
        container.grid(sticky='nsew')
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)   
        
        self.frames = {} 

        for F in (HomeMenu, stop_screen, ):
            frame = F(parent = container, controller = self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(HomeMenu)

    def show_frame(self, screen_class):
        frame = self.frames[screen_class]
        frame.tkraise()

    def confirm(self) -> None:
        print("Layers confirmed")
        self.view_model.confirm()

    def _on_close(self) -> None:
        self.destroy()

class HomeMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight = 1) #Expand Grid Row 0
        self.grid_columnconfigure(0, weight = 1) #Expand Grid Column 0
        tk.Label(self, text = "Welcome to the SAM2 data collection tool, an AI Powered Image Segmentation and Masking tool.").grid(row = 0, column = 0)
        tk.Button(self, text = "Enter Application", command = lambda: controller.show_frame(stop_screen)).grid(row = 1, column = 0)
    def start_model_loading(self):
        """maybe we should begin model loading in the home screen."""
        print("Hmmm")

class stop_screen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        #configure rows and columns
        self.grid_rowconfigure(1, weight = 1)   
        self.grid_columnconfigure(0, weight = 1)

        #create Frame for TOP STATUS LABELS
        status_frame = tk.Frame(self)
        status_frame.grid(row=0, column=0, sticky='ew', padx = 10)
        status_frame.grid_columnconfigure(1, weight=1)

        self.device_label = tk.Label(status_frame, text='Device: detecting...')
        self.device_label.grid(row = 0, column = 0, sticky = 'w', padx = (0, 15))

        self.status_label = tk.Label(status_frame, text = 'Loading SAM2...')
        self.status_label.grid(row = 0, column = 1, sticky = 'w')

        self.progress_bar = ttk.Progressbar(status_frame, mode = 'indeterminate', length = 180)
        self.progress_bar.grid(row = 0, column = 2, sticky = 'e')

        image_frame = tk.Frame(self)
        image_frame.grid(row = 1, column = 0, padx = (10, 10), pady = (0, 5), sticky = 'nsew')
        image_frame.grid_rowconfigure(0, weight = 1)
        image_frame.grid_columnconfigure(0, weight = 1)
        self.image_canvas = tk.Canvas(image_frame, background = '#202020', highlightthickness=0, cursor = 'crosshair')
        self.image_canvas.grid(row = 0, column = 0, sticky = 'nsew')
        #self.image_canvas.bind('<Button-1>', self._on_image_click)
        self.image_canvas.bind('<Configure>', self._on_canvas_resize)
        self.canvas_message_id = self.image_canvas.create_text(625,425, text="SAM2 Model Loading... \nOnce Model finishes loading, Select an image directory", fill='white', justify = 'center',font=('Arial', 16))

        information_frame = tk.Frame(self)
        information_frame.grid(row = 2, column = 0, sticky='ew')
        information_frame.grid_columnconfigure(5, weight = 1) #expand column 5
        self.image_information_label = tk.Label(information_frame, text = "Image: 0/0")
        self.image_information_label.grid(row=0, column=0, padx = (10, 0), pady = (0, 10), sticky = 'w')
        self.mask_information_label = tk.Label(information_frame, text = "Masks: 0/0")
        self.mask_information_label.grid(row = 0, column = 1, padx = (10, 0), pady = (0, 10), sticky = 'w')

        button_navigation_frame = tk.Frame(self)
        button_navigation_frame.grid(row = 3, column=0, sticky='ew')
        button_navigation_frame.grid_columnconfigure(6, weight = 1)  #expand column 3, where (0, 1, 2) are filled with widgets
        self.select_directory_button = tk.Button(button_navigation_frame, text = "Select Directory", command = self.select_directory, )
        self.select_directory_button.grid(row = 0, column = 0, padx = (10, 0), pady = (0, 10), sticky = 'w')
        self.previous_image_button = tk.Button(button_navigation_frame, text = "Previous Image", command = self._previous_image,)
        self.previous_image_button.grid(row = 0, column = 1, padx = (15, 0), pady = (0, 10))
        self.next_image_button = tk.Button(button_navigation_frame, text = "Next Image", command = self._next_image, )
        self.next_image_button.grid(row = 0, column = 2, padx = (5, 0), pady = (0, 10))
        #ttk.Separator(button_navigation_frame, orient = 'vertical').pack(side='left', fill = 'y', padx = 10)
        ttk.Separator(button_navigation_frame, orient = 'vertical').grid(row = 0, column = 3, sticky = 'ns', padx = (10, 0))

        self.show_assigned_masks_button = tk.Button(button_navigation_frame, text = "Show Candidates", command = self.show_assignments, )
        self.show_assigned_masks_button.grid(row = 0, column = 4, padx = (10, 0), pady = (0, 10))
        self.remove_previously_selected_candidate_button = tk.Button(button_navigation_frame, text = "Remove Selected Candidate", command = self.remove_selected_candidate, )
        self.remove_previously_selected_candidate_button.grid(row = 0, column = 5, padx = (5, 0), pady = (0, 10))
        self.save_classified_composite_button = tk.Button(button_navigation_frame, text = 'Save Classified Composite', command = self.save_classified_composite, )
        self.save_classified_composite_button.grid(row = 0, column = 6, padx = (0, 10), pady=(0, 10), sticky= 'e') #right side of the panel

        #MODEL LOADING FOR GUI WIDGET CONFIGURATION STATES
        self.is_processing = False # i might want to make a reference to backend self.controller.view_model.is_processing()
        self.is_model_loading = False #currently not being used
        self.is_directory_selected = False

        #IMAGE OBJECTS
        self.current_tk_mask_overlay_photoimage: ImageTk.PhotoImage | None = None #overlay
        self.current_tk_image: ImageTk.PhotoImage | None = None

        #IMAGE STATUS
        self.current_image_index = None
        self._update_controls()
        self.start_model_loading()

    def _update_controls(self) -> None:
        """Button state logic"""
        #valid_image = not processing, image displayed on canvas, model is ready
        controls_blocked = self.is_processing or self.is_model_loading
        valid_image = self.controller.view_model.get_processed_image_paths() is not None   #valid image should be if self.image_paths[self.current_image_index] is true, then valid images exist within the directory
        current_image_index, total_images = self.controller.view_model.get_image_path_info()


        self.select_directory_button.configure(state = tk.NORMAL 
                                               if not self.is_processing 
                                               else tk.DISABLED)


        self.previous_image_button.configure(state = tk.NORMAL 
                                             if valid_image
                                             and current_image_index > 0
                                             and not controls_blocked
                                             else tk.DISABLED)

        self.next_image_button.configure(state = tk.NORMAL
                                          if valid_image
                                          and current_image_index < total_images  
                                          and not controls_blocked
                                          else tk.DISABLED)
        #self.next_image_button.configure(state = tk.NORMAL)
                                          

        #image_control_state = tk.NORMAL if valid_image and not controls_blocked else tk.DISABLED
        self.show_assigned_masks_button.configure(state = tk.NORMAL
                                                  if valid_image
                                                  and not controls_blocked
                                                  else
                                                  tk.DISABLED)

        self.remove_previously_selected_candidate_button.configure(state = tk.NORMAL
                                                                   if valid_image
                                                                   and not controls_blocked
                                                                   else tk.DISABLED)

        #if len(masks) > 0 and not controls blocked, for now just valid image and controls blocked
        self.save_classified_composite_button.configure(state = tk.NORMAL
                                                        if valid_image
                                                        and not controls_blocked
                                                        else
                                                        tk.DISABLED)
        
    def start_model_loading(self) -> None:
        """Make Call to multithreading function in ViewModel which is responsible for running"""
        self.is_processing = True
        self._update_controls()
        
        self.progress_bar.start(10)
        self.controller.view_model.start_model_loading()
        self._start_processing_state()
        
    def _start_processing_state(self):
        """Wait for model status objects to update once model finishes loading.
        Calls _finish_model_loading(), a function that configures the Progress bar,
        Device Label, and Status label that signifies the model status to the GUI state..
        """
        model_status, model_error_status = self.controller.view_model.get_model_status()
        if model_status:
            self._finish_model_loading(model_status_information = "SAM2 model ready!", canvas_message = "SAM2 Finished Loading. \nSelect an Image Directory to Begin.")
            return
        if model_error_status:
            self._finish_model_loading(model_status_information= "SAM2 model failed to load.", canvas_message = "SAM2 model failed to load.")
            return
        self.after(100, self._start_processing_state, )
    
    def _finish_model_loading(self, model_status_information, canvas_message):
        """Configure GUI widgets once the model has finished loading."""
        self.is_processing = False
        self._update_controls()
        self._update_status_frame(model_status_information) # more labels will be added here later
        self.progress_bar.stop()
        self.device_label.configure(text = f"Device: {self.controller.view_model.get_device_name()}")
        
        self._set_canvas_message(canvas_message)
        #MODEL ERROR MESSAGE
        _, model_error = self.controller.view_model.get_model_status()
        if model_error:
            messagebox.showerror("Model Failure", f"Error loading Model: {model_error}")
    
    def _set_canvas_message(self, message: str) -> None:
        """Edit Tkinter Canvas message label."""
        self.image_canvas.delete("all")

        self.canvas_message_id = self.image_canvas.create_text(self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2, text = message, fill = 'white', justify = 'center', font=('Arial', 16), tags = ('canvas_message'))
    
    def select_directory(self):
        """Orchestrator Function: A function for coordinating several smaller operations."""    
        self.controller.view_model.select_directory()
        if not self.controller.view_model.get_selected_directory():
            print('RETURNING NONE SELECTED_DIRECTORY')
            return
        
        if not self.controller.view_model.get_processed_image_paths():
            messagebox.showinfo("!", "Please Select a directory with valid images!")
            return    

        self.is_directory_selected = True
        self._update_image_counter()
        self._update_mask_counter()

        self._display_tkinter_image()
        self._begin_image_inference()

    def _update_image_counter(self):
        current_image_index, total_images = self.controller.view_model.get_image_path_info()
        self.image_information_label.configure(text = f"Images: {current_image_index + 1} / {total_images}")

    def _update_mask_counter(self):
        total_current_masks = self.controller.view_model.get_total_masks()
        self.mask_information_label.configure(text = f"Masks: {total_current_masks}")

    def _update_status_frame(self, model_status_information):
        self.status_label.configure(text = model_status_information)

    def _display_tkinter_image(self) -> None:
        """
        Create and return ImageTk Object in backend, update GUI widget to display the image.

        This function must be ran on the main thread as this function directly modifies the GUI widgets.
        """
        tk_image = self.controller.view_model.retrieve_current_tkimage()
        self.current_tk_image = tk_image
        self.canvas_message_id = self.image_canvas.create_image(self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2, image = tk_image, anchor = 'center', tags = ('original_image', ))

    def _display_tkinter_overlay(self) -> bool:
        """
        I would prefer separating determining whether inference is necessary from displaying the overlay.
        display function should be responsible for rendering, not determining whether backend computation has already been performed.
        """
        overlay = self.controller.view_model.retrieve_overlay_image() # we might want to switch this to retrieve_current_overlay image() --> containing logic for current image
        if overlay is None:
            return False
        self.current_tk_mask_overlay_photoimage = overlay
        self.canvas_message_id = self.image_canvas.create_image(self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2, image = self.current_tk_mask_overlay_photoimage, anchor = 'center', tags = ('mask_overlay'))
        return True

    def _begin_image_inference(self):
        """
        Assumes image has been plopped to the screen.
        Dev Note: Take into consideration the multithreading techniques used to start loading the model
        Call backend logic required for running inference on an image using multithreading.
        """
        print('View.stop_screen._begin_image_inference()> inference mode activated')
        #Activate Progress bar, update controls for buttons, and update the status frame to notify the user that the model is currently loading.
        self.progress_bar.start(10)
        self.is_processing = True
        self._update_controls()
        self._update_status_frame(model_status_information = "SAM2 model loading...")
        self.controller.view_model.process_current_image()
        self._processing_image()

    def _processing_image(self) -> None:
        image_status, image_error_status = self.controller.view_model.get_image_processing_status()
        if image_status:
            self._finish_image_processing("SAM2 model finished Processing")
            return

        if image_error_status is not None:
            self._handle_image_processing_error()
            return
        self.after(100, self._processing_image, )

    def _finish_image_processing(self, model_status_information) -> None:
        """Configure GUI widget and label state logic once an image is done running inference using the SAM2 model."""
        print("Finished Image Processing")
        self.is_processing = False
        self.controller.view_model.set_image_processing_status(False, None)
        self._update_controls()
        self._update_status_frame(model_status_information)
        self._update_mask_counter()

        self.progress_bar.stop()
        self.image_canvas.delete("all")
        self._display_tkinter_overlay()
        #self._display_current_image_state()

    def _handle_image_processing_error(self) -> None:
        """logic goes here when running inference on an image fails:
        display error message logic will go here
        """
        print("There was an issue processing the image.")
        self.is_processing = False
        #self.controller.view_model.set_image_processing_status(False, ) reconsider an additional object for the use case of handling image inference error
        self._update_controls()
        self.progress_bar.stop()
        _, image_status_error = self.controller.view_model.get_image_processing_status()
        messagebox.showerror("Image Inference Failed", f"{image_status_error}")

    def _previous_image(self) -> None:
        print('Previous_Image')
        self.controller.view_model.set_previous_image_index()
        self.image_canvas.delete('all')
        self._update_controls()

        self._update_image_counter() 
        self._update_mask_counter() 

        self._display_tkinter_image() 
        self._display_tkinter_overlay() 

    def _next_image(self):
        print("Next Image")
        self.controller.view_model.set_next_image_index()        

        self.image_canvas.delete('all')
        self._update_controls()

        self._update_image_counter()
        self._update_mask_counter() #remember to update mask counter when clicking on a new image, and no masks exist for that particular image

        self._display_tkinter_image()
        if self.controller.view_model.has_cached_inference():
            print("View.stop_screen.next_image> Calling Tkinter Overlay.")
            self._display_tkinter_overlay()
        else:
            print("View.stop_screen.next_image> Calling image inference routine.")
            self._begin_image_inference()
    def show_original(self) -> None:
        """Show original PhotoImage. This button should only be activated if there are generated masks to be displayed"""
        pass

    def show_assignments(self) -> None:
        """Retrieving Image + Mask object overlay to display masked assignments.
        show original and show assignments function
        """
        
        pass

    def remove_selected_candidate(self):
        """Remove the previously selected mask candidate."""
        pass

    def save_classified_composite(self):
        """Save the current classified composite."""
        pass
    def _on_image_click(self, event: tk.Event) -> None:
        print("logic for on image click")
        pass

    def center_canvas(self, event: tk.Event) -> None:
        pass

    def _on_canvas_resize(self, event: tk.Event) -> None:
        """Keep canvas images, overlays, and messages centered."""

        center_x = event.width // 2
        center_y = event.height // 2

        self.image_canvas.coords("original_image", center_x, center_y)
        self.image_canvas.coords("mask_overlay", center_x, center_y)
        self.image_canvas.coords("canvas_message", center_x, center_y)
        



    #def _on_canvas_resize(
    #        self,
    #        _event: tk.Event,
    #    ) -> None:
    #        """Re-render the image or recenter the placeholder message after a canvas resize."""
    #        if self.current_display_array is not None:
    #            self._render_current_display_array()
    #        else:
    #            self._center_canvas_message()

    
if __name__ == "__main__":
    app = MainController()
    app.confirm()
    app.mainloop()