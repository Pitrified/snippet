import tkinter as tk

class PhotoFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        # init Frame, standard constructor
        tk.Frame.__init__(self, parent, **kwargs)

        # setup grid for this widget
        self.grid_rowconfigure(0, weight=1, minsize=60)
        self.grid_columnconfigure(0, weight=1)

        # create child widgets
        self.top_frame = tk.Frame(self, bg='light cyan', width=450, height=50, pady=3) # width will be ignored

        # position them in the grid
        self.top_frame.grid(row=0, sticky="nsew")


