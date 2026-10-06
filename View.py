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

        #display_container = tk.Frame(self, bg = 'lightblue', width = 200, height = 100, relief = tk.RIDGE)
        container = tk.Frame(self)
        container.grid(sticky='nsew')
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)   
        #figure out how to configure the container frame
        
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


        #GUI STATE RELATED OBJECTS
        self.is_processing = None
        self.is_model_loading = None

        self.start_model_loading()
        self._update_controls()

    def _update_controls(self):
        if self.is_processing:
            self.progress_bar.start(10)
            self._start_processing_state()
        else:
            self.progress_bar.stop()
    def _start_processing_state(self):
        model_status: bool = self.controller.view_model.get_model_status()
        if model_status:
            self.is_processing = False
            self._update_controls()
        self.after(100, self._start_processing_state,)
    def start_model_loading(self):
        self.is_processing = True
        try:
            self.controller.view_model.start_model_loading()
        except Exception as e:
            messagebox.showerror(e)

    def _on_image_click(self, event: tk.Event) -> None:
        if self.is_processing:
            return

    #def _on_canvas_resize(self, _event: tk.Event) -> None:


    
if __name__ == "__main__":
    app = MainController()
    app.confirm()
    app.mainloop()