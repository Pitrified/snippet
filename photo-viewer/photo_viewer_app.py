import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from os import listdir
from os import makedirs
from os.path import isfile
from os.path import isdir
from os.path import join
from os.path import splitext
from os.path import basename # Returns the final component of a pathname
#  import re

from photo_frame import PhotoFrame

class PhotoViewerApp():
    def __init__(self, base_dir):
        self.setup_window()
        self.setup_dirs(base_dir)
        self.setup_layout()

        self.setup_options()

        self.setup_bind()

        self.layout_num = 0
        self.set_layout(self.layout_num)

        # misc variables
        self.selection_list = []
        self.fullscreen_state = False

    def setup_dirs(self, base_dir):
        # where the main is, start here the fancy tk dir picker every time
        self.base_dir = base_dir    

        # list of dir to check for photos
        self.all_dirs = [self.base_dir]
        # list of toggled dirs
        self.active_dirs = [self.base_dir]

        #  self.is_photo_reg = re.compile('.jpe?g|.png', re.IGNORECASE)
        self.is_photo_ext = set( ('.jpg', '.jpeg', '.png') )

        #  self.photo_index = None
        self.populate_photo_list()

    def populate_photo_list(self):
        '''go through the directories and add the photos that are
        of supported formats'''
        # the index is moved when the new list is sent to the frame
        # if the photo_index is defined, search through the new list
        # and change its value to point at the same pic'''

        self.photo_list = []
        for directory in self.active_dirs:
            #  print(f'inside {directory}')
            for photo in listdir(directory):
                photo = join(directory, photo)
                #  print(f'checking {photo}')
                if self.is_photo(photo):
                    self.photo_list.append(photo)
        #  print(f'Photo list {self.photo_list}')

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

        # linux
        #  self.root.bind_all('<4>', self._on_mousewheel,  add='+') # scroll UP
        #  self.root.bind_all('<5>', self._on_mousewheel,  add='+')
        # windows/macos
        #  self.root.bind_all("<MouseWheel>", self._on_mousewheel,  add='+') # 120 up

        # this works but you have to check which widget fired
        #  self.root.bind('<4>', self.zoom_photo_mouse)
        #  self.root.bind('<5>', self.zoom_photo_mouse)
        #  self.root.bind('<MouseWheel>', self.zoom_photo_mouse)

        # for misterious reasons this deosn't work
        #  self.photo_frame.bind('<4>', self.zoom_photo_mouse)
        #  self.photo_frame.bind('<5>', self.zoom_photo_mouse)
        #  self.photo_frame.bind('<MouseWheel>', self.zoom_photo_mouse)
        #  self.photo_frame_bis.bind('<4>', self.zoom_photo_mouse)
        #  self.photo_frame_bis.bind('<5>', self.zoom_photo_mouse)
        #  self.photo_frame_bis.bind('<MouseWheel>', self.zoom_photo_mouse)
        #  self.photo_frame.bind('<Enter>', self.photo_enter)
        #  self.photo_frame.bind('<Leave>', self.photo_enter)

        self.photo_frame.image_label.bind('<4>', self.zoom_photo_mouse)
        self.photo_frame.image_label.bind('<5>', self.zoom_photo_mouse)
        self.photo_frame.image_label.bind('<MouseWheel>', self.zoom_photo_mouse)
        self.photo_frame_bis.image_label.bind('<4>', self.zoom_photo_mouse)
        self.photo_frame_bis.image_label.bind('<5>', self.zoom_photo_mouse)
        self.photo_frame_bis.image_label.bind('<MouseWheel>', self.zoom_photo_mouse)

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

        if e.char == 'r': self.zoom_photo('in')
        if e.char == 'f': self.zoom_photo('out')
        if e.char == 'v': self.zoom_photo('reset')

        if e.char == "c": self.debug()            # debug

    def move_photo(self, direction):
        #  print(f'muovo {direction}')
        self.photo_frame.move_photo(direction)
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.move_photo(direction)

    def change_photo(self, direction):
        print(f'cambio {direction}')
        self.photo_frame.change_photo(direction)
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.change_photo(direction)

    def zoom_photo(self, direction):
        print(f'zooming {direction}')
        self.photo_frame.zoom_photo(direction)
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.zoom_photo(direction)

    def zoom_photo_mouse(self, e):
        #  print('\nMOUSE')
        #  print(e)
        #  print(type(e))
        #  print(e.widget)
        #  print(type(e.widget))
        #  print(e.widget.master)
        #  print(type(e.widget.master))
        #  print(e.widget.winfo_parent())
        #  print(type(e.widget.winfo_parent()))
        #  if isinstance(e.widget.master, PhotoFrame): #  print(e)

        if e.num == 4 or e.delta == 120 or e.delta == 1:
            self.photo_frame.zoom_photo('in', e.x, e.y)
            if self.layout_num in self.layout_is_double:
                self.photo_frame_bis.zoom_photo('in', e.x, e.y)
        elif e.num == 5 or e.delta == -120 or e.delta == -1:
            self.photo_frame.zoom_photo('out', e.x, e.y)
            if self.layout_num in self.layout_is_double:
                self.photo_frame_bis.zoom_photo('out', e.x, e.y)

    def photo_enter(self, e):
        print('\nENTERING')
        print(e)
        print(e.widget)

    def debug(self):
        #  print(f'debugging')
        self.photo_frame.debug()

    def clone_frames(self):
        self.photo_frame_bis.zoom_level = self.photo_frame.zoom_level
        self.photo_frame_bis.photo_index = self.photo_frame.photo_index
        self.photo_frame_bis.mov_x = self.photo_frame.mov_x
        self.photo_frame_bis.mov_y = self.photo_frame.mov_y

        self.photo_frame_bis.load_photo()
        self.photo_frame_bis.show_photo()

    def setup_options(self):
        # don't shrink when packing
        self.options_frame.pack_propagate(False)

        # set output folder
        self.btn_set_output_folder = ttk.Button(self.options_frame, text='Set output folder', command=self.set_output_folder)
        self.output_folder_var = tk.StringVar(self.btn_set_output_folder, value='Not set')
        self.text_output_folder = tk.Label(self.options_frame,
                textvariable=self.output_folder_var,
                background=self.options_frame.cget('background'),
                )

        # add input folders
        self.btn_add_folder = ttk.Button(self.options_frame, text='Add directory to list', command=self.add_folder)
        self.checkbtn_dir = {}
        self.checkbtn_state = {}

        # pack static options
        self.btn_set_output_folder.pack()
        self.text_output_folder.pack()
        self.btn_add_folder.pack()

        self.draw_options()

    def add_folder(self, new_dir=''):
        #  new_dir = tkFileDialog.askdirectory()
        if new_dir == '':
            new_dir = tk.filedialog.askdirectory()
        print()
        print(f'{PhotoFrame.format_color(None, "New", "spring green")} folder to add to the list: {new_dir}')

        # pressing ESC in the dialog returns a tuple
        # this also closes the program
        #  if isinstance(new_dir, tuple) or not isdir(new_dir):
        if isinstance(new_dir, tuple) or not isdir(new_dir):
            print(f'Not a folder {new_dir}')
            return -1

        if not new_dir in self.all_dirs:
            self.all_dirs.append(new_dir)
            #  self.populate_photo_list()

            # send changes to frames, both of them

            #  self.photo_frame.change_photo_list(self.photo_list)
            #  self.photo_frame_bis.change_photo_list(self.photo_list)

        self.draw_options()
        self.toggle_folder()

    def draw_options(self):
        # remove all widgets from options_frame
        # this doesn't destroy them
        for folder in self.checkbtn_dir:
            self.checkbtn_dir[folder].pack_forget()

        # repack them in order
        for folder in sorted(self.all_dirs):
            folder_name = basename(folder)
            # create the Checkbutton
            if not folder in self.checkbtn_dir:
                self.checkbtn_state[folder] = tk.IntVar(value=1)
                self.checkbtn_dir[folder] = tk.Checkbutton(self.options_frame,
                    text=folder_name,
                    command=self.toggle_folder,
                    background=self.options_frame.cget('background'),
                    variable=self.checkbtn_state[folder],
                    )
            # pack it
            #  print(f'Packing {folder}')
            self.checkbtn_dir[folder].pack()

        # destroy unused Checkbutton if you want
        #  for folder in self.checkbtn_dir:
            #  if not folder in self.all_dirs:
                #  self.checkbtn_dir[folder].destroy

    def toggle_folder(self):
        #  print(f'Toggling something')
        # untoggling every folder is a bad idea
        self.active_dirs = []
        for folder in self.checkbtn_dir:
            #  print(f'Folder {folder} has value {self.checkbtn_state[folder].get()}')
            if self.checkbtn_state[folder].get() == 1:
                self.active_dirs.append(folder)
        #  print(f'Active dirs {self.active_dirs}')
        self.populate_photo_list()

        self.photo_frame.change_photo_list(self.photo_list)
        self.photo_frame_bis.change_photo_list(self.photo_list)

    def set_output_folder(self, out_dir=''):
        if out_dir == '':
            out_dir = tk.filedialog.askdirectory()

        if isinstance(out_dir, tuple):
            print(f'Selection cancelled')
            return -1

        print()
        print(f'{PhotoFrame.format_color(None, "Output", "spring green")} folder: {out_dir}')

        # create the folder if it doesn't exist
        if not isdir(out_dir):
            print(f'Not a folder {out_dir}, creating it')
            makedirs(out_dir)

        self.output_folder_var.set(basename(out_dir))

    def cycle_layout(self):
        self.layout_num = (self.layout_num + 1) % self.layout_tot
        self.set_layout(self.layout_num)

    def setup_layout(self):
        '''create the widgets'''
        #  print('update_idletasks now')
        #  self.root.update_idletasks()
        #  self.root.update()
        #  self.update_idletasks()

        # NOTE all of them? even the hidden ones?
        self.photo_frame = PhotoFrame(self.root, self.photo_list, 'primary')
        self.photo_frame_bis = PhotoFrame(self.root, self.photo_list, 'secondary')
        #  self.photo_frame = PhotoFrame(self.root, frame_name='primary')
        #  self.photo_frame_bis = PhotoFrame(self.root, frame_name='secondary')

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

        #  self.photo_frame.do_resize()
        #  if lay_num in self.layout_is_double:
            #  self.photo_frame_bis.do_resize()

        #  self.root.update()
        #  self.root.update_idletasks()

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
        self.root.update()
        #  self.root.after(0, self.finish_setup())
        self.finish_setup()
        print('\nSTARTING MAINLOOP\n')
        self.root.mainloop()

    def finish_setup(self):
        print('\nfihishing setup\n')
        self.photo_frame.calc_zoom_level()
        self.photo_frame.show_photo()
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.calc_zoom_level()
            self.photo_frame_bis.show_photo()

    def exit(self, e=None):
        self.root.destroy()

    def toggle_fullscreen(self, e=None):
        #  print(f'fullscreen event {e}')
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes("-fullscreen", self.fullscreen_state)

