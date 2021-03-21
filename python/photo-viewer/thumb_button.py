import tkinter as tk

from os.path import basename
from PIL import ImageTk, Image

from label_pixel import LabelPixel

class ThumbButton(tk.Frame):
    def __init__(self, parent, photo_info, thumb_btn_width, **kwargs):
        tk.Frame.__init__(self, parent, width=thumb_btn_width, **kwargs)
        self.photo_info = photo_info
        self.thumb_btn_width = thumb_btn_width

        # setup grid for this widget
        #  self.grid_rowconfigure(0, weight=1, minsize=60)
        self.grid_rowconfigure(0, weight=1, minsize=25)
        #  self.grid_rowconfigure(0, weight=0)
        #  self.grid_rowconfigure(0, weight=1)

        #  self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        #  self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # create child widgets
        #  # background frame to fill the grid
        #  self.top_frame = tk.Frame(self,bg='chartreuse3',width=200,height=50)
        #  self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.thumb_label = tk.Label(
            self, width=self.photo_info.thumb_size, bg="powder blue"
        )
        #  self.photo_text = tk.Label(self,
        self.photo_text = LabelPixel(
            self,
            text=basename(self.photo_info.photo),
            bg="wheat2",
            activebackground="wheat1",
            justify=tk.LEFT,
            anchor=tk.W,
            #  width=self.thumb_btn_width-self.photo_info.thumb_size,
            width=self.thumb_btn_width - self.photo_info.thumb_size - 2,
            #  width=200,
            #  width=230,
            #  width=20,       # https://stackoverflow.com/a/16363832 .....
            #  relief=tk.RAISED,
        )
        #  print(f'what {self.thumb_btn_width-self.photo_info.thumb_size}')
        tkimg = ImageTk.PhotoImage(self.photo_info.thumb)
        self.thumb_label.image = tkimg
        self.thumb_label.configure(image=tkimg)

        self.thumb_label.grid(row=0, column=0)
        #  self.photo_text.grid(row=0, column=1)
        #  self.photo_text.grid(row=0, column=1, sticky='ew')
        #  self.photo_text.grid(row=0, column=1, sticky='ns')
        self.photo_text.grid(row=0, column=1, sticky="nsew")


class ThumbCheckButton(tk.Frame):
    def __init__(self, parent, photo_info, chk_btn_thumb_width, **kwargs):
        tk.Frame.__init__(self, parent, width=chk_btn_thumb_width, **kwargs)
        self.photo_info = photo_info
        self.chk_btn_thumb_width = chk_btn_thumb_width

        # setup grid for this widget
        self.grid_rowconfigure(0, weight=1, minsize=25)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)



