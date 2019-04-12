import tkinter as tk

class PhotoFrame(tk.Frame):
    def __init__(self, parent, photo_list, **kwargs):
        # init Frame, standard constructor
        tk.Frame.__init__(self, parent, **kwargs)

        self.photo_index = 0
        self.photo_list = photo_list.copy()

        # setup grid for this widget
        self.grid_rowconfigure(0, weight=1, minsize=60)
        self.grid_columnconfigure(0, weight=1)

        # create child widgets
        self.top_frame = tk.Frame(self, bg='light cyan', width=450, height=50, pady=3) # width will be ignored

        # position them in the grid
        self.top_frame.grid(row=0, sticky="nsew")

    def change_photo_list(self, new_list):
        current_photo = self.photo_list[self.photo_index]

        if current_photo in new_list:
            self.photo_index = new_list.index(current_photo)
        else:
            self.photo_index = 0

        self.photo_list = new_list.copy()



