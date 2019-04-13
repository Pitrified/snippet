import tkinter as tk
from os import listdir
from os.path import isfile
from os.path import join
from os.path import splitext
from os.path import basename # Returns the final component of a pathname
#  import re

from photo_frame import PhotoFrame

class PhotoViewerApp():
    def __init__(self, base_dir):
        self.setup_dirs(base_dir)
        self.setup_window()
        self.setup_bind()
        self.setup_layout()

        self.layout_num = 0
        self.set_layout(self.layout_num)

        # misc variables
        self.selection_list = []
        self.fullscreen_state = False

    def setup_dirs(self, base_dir):
        # where the main is, start here the fancy tk dir picker every time
        self.base_dir = base_dir    

        # list of dir to check for photos
        self.dirs = [self.base_dir]

        #  self.is_photo_reg = re.compile('.jpe?g|.png', re.IGNORECASE)
        self.is_photo_ext = set( ('.jpg', '.jpeg', '.png') )

        #  self.photo_index = None
        self.populate_photo_list()

    def populate_photo_list(self):
        '''go through the directories and add the photos that are
        of supported formats'''
        # NO! this is done in frame
        #  if the photo_index is defined, search through the new list
        #  and change its value to point at the same pic'''

        self.photo_list = []
        for directory in self.dirs:
            #  print(f'inside {directory}')
            for photo in listdir(directory):
                photo = join(directory, photo)
                #  print(f'checking {photo}')
                if self.is_photo(photo):
                    self.photo_list.append(photo)
        #  print(f'{self.photo_list}')

    def is_photo(self, photo):
        '''photo is the FULL path to the pic'''
        if not isfile(photo):
            #  print(f'not a file {photo}')
            return False
        #  photo_name = basename(photo)
        _, photo_ext = splitext(photo)
        #  print(f'path {photo} photo_ext {photo_ext}')
        if photo_ext in self.is_photo_ext:
            return True
        else:
            return False

    def setup_window(self):
        self.root = tk.Tk()

        self.width = 900
        self.height = 600
        self.root.geometry(f'{self.width}x{self.height}')

    def setup_bind(self):
        #  self.root.bind('<Escape>', self.exit)
        #  self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<KeyRelease>", self.keyup)

    def keyup(self, e):
        #  print(f'key released {e}')
        if e.keysym == 'Escape': self.exit()
        if e.keysym == 'F11': self.toggle_fullscreen()
        if e.keysym == 'F5': self.cycle_layout()

        if e.keysym == 'e': self.change_photo('forward') 
        if e.keysym == '2': self.change_photo('forward') 
        if e.keysym == 'q': self.change_photo('backward')
        if e.keysym == '1': self.change_photo('backward')

        if e.char == 'd': self.move_photo('right')
        if e.char == 'a': self.move_photo('left')
        if e.char == 'w': self.move_photo('up')  
        if e.char == 's': self.move_photo('down')
        if e.char == 'x': self.move_photo('reset')

        if e.char == "c": self.debug()            # debug

    def move_photo(self, direction):
        print(f'muovo {direction}')
        self.photo_frame.move_photo(direction)
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.move_photo(direction)

    def change_photo(self, direction):
        print(f'cambio {direction}')
        self.photo_frame.change_photo(direction)
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.change_photo(direction)

    def debug(self):
        print(f'debugging')

    def clone_frames(self):
        self.photo_frame_bis.zoom_level = self.photo_frame.zoom_level
        self.photo_frame_bis.photo_index = self.photo_frame.photo_index
        self.photo_frame_bis.mov_x = self.photo_frame.mov_x
        self.photo_frame_bis.mov_y = self.photo_frame.mov_y

    def cycle_layout(self):
        self.layout_num = (self.layout_num + 1) % self.layout_tot
        self.set_layout(self.layout_num)

    def setup_layout(self):
        '''create the widgets'''
        # NOTE all of them? even the hidden ones?
        self.photo_frame = PhotoFrame(self.root, self.photo_list, 'primary')
        self.photo_frame_bis = PhotoFrame(self.root, self.photo_list, 'secondary')

        # you DO need width and height here (at least width)
        # they will be fixed size
        self.metadata_frame = tk.Frame(self.root, width=250, height=100, bg='dark orange')
        self.options_frame = tk.Frame(self.root, width=250, height=100, bg='SeaGreen1')

        self.layout_tot = 5
        self.layout_is_double = (1, )

    def set_layout(self, lay_num):
        if lay_num == 0:
            self.layout_i()
        elif lay_num == 1:
            self.layout_ii()
        elif lay_num == 2:
            self.layout_im()
        elif lay_num == 3:
            self.layout_io()
        elif lay_num == 4:
            self.layout_imo()

        if lay_num in self.layout_is_double:
            self.clone_frames()

        #  self.root.event_generate('<Configure>')

        self.photo_frame.do_resize()
        if lay_num in self.layout_is_double:
            self.photo_frame_bis.do_resize()

        self.root.update()
        self.root.update_idletasks()

    def layout_i(self):
        # tell the grid in root to grow with the window
        # reset rows and columns you dont use
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        # pack the widgets
        self.photo_frame.grid(row=0, column=0, sticky='nsew')
        # remove from the grid the unused widgets
        self.photo_frame_bis.grid_forget()
        self.metadata_frame.grid_forget()
        self.options_frame.grid_forget()

    def layout_im(self):
        # tell the grid in root to grow with the window
        # reset rows and columns you dont use
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        # pack the widgets
        # remove from the grid the unused widgets
        self.photo_frame.grid(row=0, column=0, sticky='nsew')
        self.photo_frame_bis.grid_forget()
        #  self.metadata_frame.grid_forget()
        #  self.metadata_frame.grid(row=0, column=1, sticky='nsew')
        self.metadata_frame.grid(row=0, column=1, sticky='ns')
        self.options_frame.grid_forget()
        #  self.options_frame.grid(row=1, column=1, sticky='nsew')

    def layout_io(self):
        # tell the grid in root to grow with the window
        # reset rows and columns you dont use
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        # pack the widgets
        # remove from the grid the unused widgets
        self.photo_frame.grid(row=0, column=0, sticky='nsew')
        self.photo_frame_bis.grid_forget()
        self.metadata_frame.grid_forget()
        #  self.metadata_frame.grid(row=0, column=1, sticky='nsew')
        #  self.metadata_frame.grid(row=0, column=1, sticky='ns')
        #  self.options_frame.grid_forget()
        #  self.options_frame.grid(row=1, column=1, sticky='nsew')
        self.options_frame.grid(row=0, column=1, sticky='ns')

    def layout_imo(self):
        # tell the grid in root to grow with the window
        # reset rows and columns you dont use
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        # pack the widgets
        # remove from the grid the unused widgets
        self.photo_frame.grid(row=0, column=0, rowspan=2, sticky='nsew')
        self.photo_frame_bis.grid_forget()
        #  self.metadata_frame.grid_forget()
        #  self.metadata_frame.grid(row=0, column=1, sticky='nsew')
        self.metadata_frame.grid(row=0, column=1, sticky='ns')
        #  self.options_frame.grid_forget()
        #  self.options_frame.grid(row=1, column=1, sticky='nsew')
        self.options_frame.grid(row=1, column=1, sticky='ns')

    def layout_ii(self):
        # tell the grid in root to grow with the window
        # reset rows and columns you dont use
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        # pack the widgets
        self.photo_frame.grid(row=0, column=0, sticky='nsew')
        self.photo_frame_bis.grid(row=0, column=1, sticky='nsew')
        # remove from the grid the unused widgets
        self.metadata_frame.grid_forget()
        self.options_frame.grid_forget()

    def start(self):
        self.root.mainloop()

    def exit(self, e=None):
        self.root.destroy()

    def toggle_fullscreen(self, e=None):
        #  print(f'fullscreen event {e}')
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes("-fullscreen", self.fullscreen_state)

