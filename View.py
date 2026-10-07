"""stop sign sam2 gui"""
import ViewModel
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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

        for F in (stop_screen, ):
            frame = F(parent = container, controller = self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(stop_screen)

    def show_frame(self, screen_class):
        frame = self.frames[screen_class]
        frame.tkraise()

    def confirm(self) -> None:
        print("Layers confirmed")
        self.view_model.confirm()

    def _on_close(self) -> None:
        self.destroy()

class stop_screen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        #configure rows and columns
        self.grid_rowconfigure(1, weight = 1)   #row 1, weight 1
        self.grid_columnconfigure(0, weight = 1)#column 0, weight 1

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
        self.image_canvas.bind('<Button-1>', self._on_image_click)
        #self.image_canvas.bind('<Configure>', self._on_cavas_resize)
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
        button_navigation_frame.grid_columnconfigure(3, weight = 1)  #expand column 3(0, 1, 2, 3), where 0 and 1 are filled with widgets
        self.select_directory_button = tk.Button(button_navigation_frame, text = "Select Directory", command = self.select_directory, )
        self.select_directory_button.grid(row = 0, column = 0, padx = (10, 0), pady = (0, 10), sticky = 'w')
        self.previous_image = tk.Button(button_navigation_frame, text = "Previous Image", command = self._previous_image,)
        self.previous_image.grid(row = 0, column = 1, padx = (15, 0), pady = (0, 10))
        self.next_image = tk.Button(button_navigation_frame, text = "Next Image", command = self._next_image, )
        self.next_image.grid(row = 0, column = 2, padx = (10, 0), pady = (0, 10))

        #GUI STATE RELATED OBJECTS
        self.is_processing = None
        self.is_model_loading = None

        self._update_controls()
        self.start_model_loading()

    def _update_controls(self):
        """Button state logic"""
        #valid_image = not processing, image displayed on canvas, model is ready
        self.select_directory_button.configure(state = tk.NORMAL if not self.is_processing else tk.DISABLED)
        self.previous_image.configure(state = tk.NORMAL if not self.is_processing else tk.DISABLED)         #fix this once image has been appended to canvas(once user can see image), 
        self.next_image.configure(state = tk.NORMAL if not self.is_processing else tk.DISABLED)

    def _set_canvas_message(self, message: str):
        self.image_canvas.delete("all")

        self.canvas_message_id = self.image_canvas.create_text(self.image_canvas.winfo_width() / 2, self.image_canvas.winfo_height() / 2, text = message, fill = 'white', justify = 'center', font=('Arial', 16))

    def _finish_model_loading(self):
        self.is_processing = False
        self._update_controls()
        self.progress_bar.stop()
        self.device_label.configure(text=f"Device: {self.controller.view_model.get_device_name()}")
        self.status_label.configure(text = "SAM2 model ready!")
        self._set_canvas_message("SAM2 finished Loading. \nSelect an Image Directory to Begin.")

    def _handle_model_loading_error(self):
        self.is_processing = False
        self._update_controls()
        self.progress_bar.stop()
        self.device_label.configure(text = 'Failed')
        self.status_label.configure(text = "SAM2 model failed to load.")
        self._set_canvas_message("SAM2 model failed to load.")
        _, model_error = self.controller.view_model.get_model_status()
        messagebox.showerror("Model Failure", f"Error loading Model: {model_error}")

    def _start_processing_state(self):
        """
        Configure GUI objects once model finishes loading.
        """
        model_status, model_error_status = self.controller.view_model.get_model_status()
        if model_status:
            self._finish_model_loading()
            return
        if model_error_status:
            self._handle_model_loading_error()
            return
        self.after(100, self._start_processing_state, )

    def start_model_loading(self):
        self.is_processing = True
        self._update_controls()
        self.progress_bar.start(10)
        self.controller.view_model.start_model_loading()
        self._start_processing_state()

    def select_directory(self):
        """Refactor this function: not acceptable: Use callback class """
        try:
            self.controller.view_model.select_directory()
        except Exception as e:
            print(e)
        print("select directory logic")

    def _previous_image(self):
        print("logic for previous image")

    def _next_image(self):
        print("logic for next image")

    def _on_image_click(self, event: tk.Event) -> None:
        if self.is_processing:
            return

    #def _on_canvas_resize(self, _event: tk.Event) -> None:


    
if __name__ == "__main__":
    app = MainController()
    app.confirm()
    app.mainloop()