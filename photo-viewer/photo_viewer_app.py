import tkinter as tk

from photo_frame import PhotoFrame

class PhotoViewerApp():
    def __init__(self):
        self.root = tk.Tk()
        self.root.bind('<Escape>', self.exit)

        self.width = 900
        self.height = 600
        self.root.geometry(f'{self.width}x{self.height}')

        # this will be done in layout_set
        # tell the grid in root to grow with the window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.photo_frame = PhotoFrame(self.root)
        self.photo_frame.grid(row=0, column=0, sticky='nsew')

    def start(self):
        self.root.mainloop()

    def exit(self, e=None):
        self.root.destroy()


