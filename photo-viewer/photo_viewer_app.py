import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from PIL import ImageTk, Image
import exifread

from os import listdir
from os import makedirs
from os.path import isfile
from os.path import isdir
from os.path import join
from os.path import splitext
from os.path import basename
from shutil import copy2
from math import ceil
from math import floor
from queue import Queue

import ray

from photo_frame import PhotoFrame

class LabelPixel(tk.Frame):
    '''label with width set in pixel

    http://code.activestate.com/recipes/578887-text-widget-width-and-height-in-pixels-tkinter/
    https://stackoverflow.com/questions/14887610/specify-the-dimensions-of-a-tkinter-text-box-in-pixels
    '''
    def __init__(self, parent, width=0, height=0, **kwargs):
        self.width = width
        self.height = height

        tk.Frame.__init__(self, parent, width=self.width, height=self.height)

        self.label_widget = tk.Label(self, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label_widget.grid(row=0, column=0, sticky='nsew')

    def pack(self, *args, **kwargs):
        tk.Frame.pack(self, *args, **kwargs)
        self.pack_propagate(False)

    def grid(self, *args, **kwargs):
        tk.Frame.grid(self, *args, **kwargs)
        self.grid_propagate(False)

class PhotoInfo:
    def __init__(self, photo, thumb_size=50):
        self.photo = photo
        #  self.thumb_size = (thumb_size, thumb_size)
        self.thumb_size = thumb_size

        #  self.define_useful_tags()
        #  self.get_metadata()

        self.load_thumbnail()

    def define_useful_tags(self):
        '''Populate set of useful tags'''
        self.useful_tags = set([
                'JPEGThumbnail',
                'TIFFThumbnail',
                'Filename',
                #  'EXIF MakerNote',
                # 'Image Tag 0x000B',
                # 'Image ImageDescription',
                'Image Make',
                'Image Model',
                'Image Orientation',
                # 'Image XResolution',
                # 'Image YResolution',
                # 'Image ResolutionUnit',
                'Image Software',
                'Image DateTime',
                # 'Image YCbCrPositioning',
                # 'Image ExifOffset',
                # 'Image PrintIM',
                # 'Image Padding',
                'GPS GPSLatitudeRef',
                'GPS GPSLatitude',
                'GPS GPSLongitudeRef',
                'GPS GPSLongitude',
                # 'GPS GPSAltitudeRef',
                # 'GPS GPSTimeStamp',
                # 'GPS GPSSatellites',
                # 'GPS GPSImgDirectionRef',
                # 'GPS GPSMapDatum',
                # 'GPS GPSDate',
                # 'Image GPSInfo',
                # 'Thumbnail Compression',
                # 'Thumbnail XResolution',
                # 'Thumbnail YResolution',
                # 'Thumbnail ResolutionUnit',
                # 'Thumbnail JPEGInterchangeFormat',
                # 'Thumbnail JPEGInterchangeFormatLength',
                'EXIF ExposureTime',
                'EXIF FNumber',
                'EXIF ExposureProgram',
                'EXIF ISOSpeedRatings',
                # 'EXIF ExifVersion',
                'EXIF DateTimeOriginal',
                'EXIF DateTimeDigitized',
                # 'EXIF ComponentsConfiguration',
                # 'EXIF CompressedBitsPerPixel',
                # 'EXIF BrightnessValue',
                'EXIF ExposureBiasValue',
                # 'EXIF MaxApertureValue',
                # 'EXIF MeteringMode',
                # 'EXIF LightSource',
                'EXIF Flash',
                'EXIF FocalLength',
                # 'EXIF UserComment',
                # 'EXIF FlashPixVersion',
                # 'EXIF ColorSpace',
                'EXIF ExifImageWidth',
                'EXIF ExifImageLength',
                # 'Interoperability InteroperabilityVersion',
                # 'EXIF InteroperabilityOffset',
                # 'EXIF FileSource',
                # 'EXIF SceneType',
                # 'EXIF CustomRendered',
                'EXIF ExposureMode',
                'EXIF WhiteBalance',
                'EXIF DigitalZoomRatio',
                'EXIF FocalLengthIn35mmFilm',
                ])

    def get_metadata(self):
        '''Load metadata for Photo, according to useful list'''
        with open(self.photo, 'rb') as f:
            tags = exifread.process_file(f)

        #  print(f'type tags {type(tags)}')
        #  print(f'for {self.photo} len tags {len(tags.keys())}')

        #  for tag in tags.keys():
            #  if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                #  print(f'Key: {tag}, value: {tags[tag]}')

    def load_thumbnail(self):
        '''resize the pic'''
        #  img = Image.open(self.photo)
        self.thumb = Image.open(self.photo)
        self.thumb.thumbnail((self.thumb_size, self.thumb_size) , Image.BICUBIC)
        #  self.thumb.thumbnail(self.thumb_size, Image.LANCZOS)

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
        self.thumb_label = tk.Label(self,
                width=self.photo_info.thumb_size,
                bg='powder blue',
                )
        #  self.photo_text = tk.Label(self,
        self.photo_text = LabelPixel(self,
                text=basename(self.photo_info.photo),
                bg='wheat2',
                activebackground='wheat1',
                justify=tk.LEFT,
                width=self.thumb_btn_width-self.photo_info.thumb_size,
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
        self.photo_text.grid(row=0, column=1, sticky='nsew')

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
        # remember last toggled folder
        self.last_input_folder = self.base_dir

        #  self.is_photo_reg = re.compile('.jpe?g|.png', re.IGNORECASE)
        self.is_photo_ext = set( ('.jpg', '.jpeg', '.JPG', '.png', ) )

        #  self.photo_index = None
        self.populate_photo_list()

        # update info
        self.photo_info = {}
        self.populate_info()
        #  self.populate_info_ray()

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

        # sort the list in place
        self.photo_list.sort()
        #  print(f'Photo list {self.photo_list}')

    def populate_info(self):
        new_pics = 0
        for pic in self.photo_list:
            if not pic in self.photo_info:
                new_pics += 1

        if new_pics == 0:
            return 1

        bar_width = 80

        # 100/80 = 1,... -> 2   avanzo di 50 volte ogni 2
        # 10/80 = 0,... -> 1    avanzo di 10 volte ogni 1
        step = ceil(new_pics / bar_width)

        print('Loading thumbnails:   0%', end='', flush=True)
        pic_count = 0
        for pic in self.photo_list:
            if pic in self.photo_info:
                continue

            self.photo_info[pic] = PhotoInfo(pic, thumb_size=self.thumb_size)

            pic_count += 1
            #  if pic_count % step == 0: print('.', end='', flush=True)
            progress = floor(pic_count / new_pics * 100)
            #  print(progress)
            print(f'\b\b\b\b{progress: 3d}%', end='', flush=True)
        print('\b\b\b\bDone')

    #  def populate_info_ray(self):
        #  # www.toptal.com/python/beginners-guide-to-concurrency-and-parallelism-in-python
        #  # https://towardsdatascience.com/modern-parallel-and-distributed-python-a-quick-tutorial-on-ray-99f8d70369b8

        #  new_pics_pair_ray = []
        #  for pic in self.photo_list:
            #  if pic in self.photo_info:
                #  continue

            #  #  self.photo_info[pic] = self.new_photo_info.remote(pic)
            #  new_pics_pair_ray.append(self.new_photo_info.remote(pic))

        #  new_pics_pair = ray.get(new_pics_pair_ray)

        #  for which_pic, info in new_pics_pair:
            #  self.photo_info[which_pic] = info

    #  def new_photo_info(pic):
        #  @ray.remote
        #  return (pic, PhotoInfo(pic))

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

        #  self.root.wm_iconbitmap('LogoPV.png')
        #  self.root.wm_iconbitmap('LogoPV.ico')
        #  self.root.wm_iconwindow('LogoPV.ico')
        #  self.root.iconphoto(True, tk.PhotoImage(file='Logo.png') )
        #  self.root.iconphoto(True, tk.PhotoImage(file='Logo.gif') )
        #  icon_img = tk.PhotoImage(file='./LogoPV64.gif')
        icon_img = tk.PhotoImage(file='./LogoPV64_2-2.gif')
        self.root.iconphoto(True, icon_img)

        self.thumb_size = 50
        self.sidebar_width = 250
        #  self.sidebar_width = 400

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

        self.photo_frame.image_label.bind('<Button-1>', self.click_photo_mouse)
        self.photo_frame_bis.image_label.bind('<Button-1>', self.click_photo_mouse)
        self.photo_frame.image_label.bind('<B1-Motion>', self.move_photo_mouse)
        self.photo_frame_bis.image_label.bind('<B1-Motion>', self.move_photo_mouse)

        self.photo_list_canvas.bind('<4>', self.on_photo_list_scroll)
        self.photo_list_canvas.bind('<5>', self.on_photo_list_scroll)
        self.photo_list_canvas.bind('<MouseWheel>', self.on_photo_list_scroll)
        #  self.photo_list_frame.bind('<4>', self.on_photo_list_scroll, add='+')
        #  self.photo_list_frame.bind('<5>', self.on_photo_list_scroll, add='+')
        #  self.photo_list_frame.bind('<MouseWheel>', self.on_photo_list_scroll, add='+')
        self.photo_list_frame.bind('<4>', self.on_photo_list_scroll)
        self.photo_list_frame.bind('<5>', self.on_photo_list_scroll)
        self.photo_list_frame.bind('<MouseWheel>', self.on_photo_list_scroll)

    def keyup(self, e):
        #  print(f'key released {e}')
        if e.keysym == 'Escape': self.exit()
        if e.keysym == 'F11': self.toggle_fullscreen()
        if e.keysym == 'F5': self.cycle_layout()
        if e.keysym == 'F8': self.save_selection()

        if e.keysym == 'e': self.change_photo('forward') 
        if e.keysym == '3': self.change_photo('forward', 'secondary') 
        if e.keysym == 'KP_Down': self.change_photo('forward')      # numpad 2
        if e.keysym == 'q': self.change_photo('backward')
        if e.keysym == '1': self.change_photo('backward', 'secondary')
        if e.keysym == 'KP_End': self.change_photo('backward')      # numpad 1
        if e.keysym == '2': self.change_photo('sync')

        if e.keysym == 'd': self.move_photo('right')
        if e.keysym == 'a': self.move_photo('left')
        if e.keysym == 'w': self.move_photo('up')  
        if e.keysym == 's': self.move_photo('down')
        if e.keysym == 'x': self.move_photo('reset')

        if e.keysym == 'r': self.zoom_photo('in')
        if e.keysym == 'f': self.zoom_photo('out')
        if e.keysym == 'v': self.zoom_photo('reset')

        if e.keysym == 'k': self.add_to_selection('primary')
        if e.keysym == 'l': self.add_to_selection('secondary')

        #  if e.char == "c": self.debug()            # debug
        if e.keysym == "c": self.debug()            # debug

    def move_photo(self, direction):
        #  print(f'muovo {direction}')
        self.photo_frame.move_photo(direction)
        if self.layout_num in self.layout_is_double:
            self.photo_frame_bis.move_photo(direction)

    def click_photo_mouse(self, e):
        #  print(f'Clicked: {e}')
        self.photo_frame.click_photo_mouse(e.x, e.y)

    def move_photo_mouse(self, e):
        #  print(f'Moved: {e}')
        self.photo_frame.move_photo_mouse(e.x, e.y)

        if self.layout_num in self.layout_is_double:
            self.clone_frames(reset_index=False)

    def change_photo(self, direction, photo_frame_which='primary'):
        #  print(f'cambio {direction} in {photo_frame_which}')

        if direction == 'sync':
            self.clone_frames(reset_index=True)
            return 1

        if photo_frame_which == 'primary':
            #  if self.layout_num in self.layout_is_double:
                # in a double layout, don't reset the zoom
                #  self.photo_frame.change_photo(direction, reset_pos=False)
            #  else:
            self.photo_frame.change_photo(direction)

        elif photo_frame_which == 'secondary' and self.layout_num in self.layout_is_double:
            self.photo_frame_bis.change_photo(direction)

        # keep zoom and position in sync
        self.clone_frames(reset_index=False)
        #  self.photo_frame_bis.zoom_level = self.photo_frame.zoom_level
        #  self.photo_frame_bis.mov_x = self.photo_frame.mov_x
        #  self.photo_frame_bis.mov_y = self.photo_frame.mov_y
        #  self.photo_frame_bis.load_photo()
        #  self.photo_frame_bis.show_photo()

    def zoom_photo(self, direction):
        #  print(f'zooming {direction}')
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
        else:
            print(f'Errors when zooming {e}')

    def photo_enter(self, e):
        print('\nENTERING')
        print(e)
        print(e.widget)

    def clone_frames(self, reset_index=True):
        self.photo_frame_bis.zoom_level = self.photo_frame.zoom_level
        self.photo_frame_bis.mov_x = self.photo_frame.mov_x
        self.photo_frame_bis.mov_y = self.photo_frame.mov_y
        if reset_index:
            self.photo_frame_bis.photo_index = self.photo_frame.photo_index

        self.photo_frame_bis.load_photo()
        self.photo_frame_bis.show_photo()

    def setup_options(self):
        # don't shrink when packing, this is shaky af
        #  self.options_frame.pack_propagate(False)
        #  self.options_frame.grid_propagate(False)

        # setup grid for options_frame
        self.options_frame.grid_rowconfigure(0, weight=0)
        self.options_frame.grid_rowconfigure(1, weight=0)
        self.options_frame.grid_rowconfigure(2, weight=1)
        self.options_frame.grid_rowconfigure(3, weight=1)
        #  self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(0, weight=0)

        # CREATE children frames
        # the height parameter is happily ignored, you might set grid_propagate in each frame
        self.output_frame = tk.Frame(self.options_frame,
                width=self.sidebar_width,
                height=120,
                bg='turquoise')
        self.input_frame = tk.Frame(self.options_frame,
                width=self.sidebar_width,
                height=200,
                bg='dark green')
        self.selection_frame = tk.Frame(self.options_frame,
                width=self.sidebar_width,
                bg='SkyBlue1')
        self.photo_list_frame = tk.Frame(self.options_frame,
                width=self.sidebar_width,
                bg='SkyBlue3')

        # GRID childrens
        self.output_frame.grid(row=0, column=0, sticky='ew')
        self.input_frame.grid(row=1, column=0, sticky='ew')
        self.selection_frame.grid(row=2, column=0, sticky='nsew')
        self.photo_list_frame.grid(row=3, column=0, sticky='nsew')

        # tell children to GROW width
        # and most importantly center their children
        # https://stackoverflow.com/a/33047033
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # don't grow/center lists, widgets will be created with 250 width
        #  self.selection_frame.grid_columnconfigure(0, weight=1)
        #  self.photo_list_frame.grid_columnconfigure(0, weight=1)

        ### SETUP OUTPUT FOLDERS ###

        # set output folder, packed in output_frame
        self.btn_set_output_folder = tk.Button(self.output_frame,
                text='Set output folder',
                command=self.set_output_folder)
        self.output_folder_var = tk.StringVar(self.btn_set_output_folder,
                value='Not set')
        self.text_output_folder = tk.Label(self.output_frame,
                textvariable=self.output_folder_var,
                background=self.options_frame.cget('background'),
                )
        self.output_folder = 'Not set'

        # pack static options about output folder
        #  self.btn_set_output_folder.pack()
        #  self.text_output_folder.pack()
        #  self.btn_set_output_folder.grid(row=0, column=0, sticky='ew')
        self.btn_set_output_folder.grid(row=0, column=0)
        self.text_output_folder.grid(row=1, column=0, sticky='ew')

        ### SETUP INPUT FOLDERS ###

        # add input folders
        self.btn_add_folder = tk.Button(self.input_frame,
                text='Add directory to list',
                command=self.add_folder)
        self.checkbtn_input_dirs = {}
        self.checkbtn_input_state = {}

        # pack input folders
        #  self.btn_add_folder.pack()
        #  self.btn_add_folder.grid(row=0, column=0, sticky='ew')
        self.btn_add_folder.grid(row=0, column=0)
        self.draw_input_folders()


        ##############################
        ### SETUP PHOTO_LIST_FRAME ###
        ##############################

        # add photo_list_frame header
        self.photo_list_frame_header = tk.Label(self.photo_list_frame,
                text='Photo list:',
                bg='wheat3',
                #  width=self.sidebar_width, # XXX ERRORS
                )
        # create scrollbar for canvas
        self.photo_list_scrollbar = tk.Scrollbar(self.photo_list_frame)
        # create the canvas and bind it to Scrollbar
        self.photo_list_canvas = tk.Canvas(self.photo_list_frame,
                bg='cornflower blue',
                yscrollcommand=self.photo_list_scrollbar.set,
                width=self.sidebar_width-13,
                highlightthickness=0,
                )
        # bind Scrollbar to Canvas
        self.photo_list_scrollbar.config(command=self.photo_list_canvas.yview)
        # create the Frame to put inside the Canvas
        # thanks to the wizard BO https://stackoverflow.com/a/3092341
        self.photo_list_holder = tk.Frame(self.photo_list_canvas,
                bg='red',
                #  width=self.sidebar_width,
                #  width=self.sidebar_width-30,
                width=self.sidebar_width-13,
                )

        # pack photo_list_frame
        #  self.photo_list_frame_header.pack(fill='x')

        # grid configure the photo_list_frame

        self.photo_list_frame.rowconfigure(0, weight=0)
        self.photo_list_frame.rowconfigure(1, weight=1)
        #  self.photo_list_frame.rowconfigure(1, weight=0)

        self.photo_list_frame.columnconfigure(0, weight=1)
        #  self.photo_list_frame.columnconfigure(0, weight=0)
        self.photo_list_frame.columnconfigure(1, weight=0)

        # grid photo list pieces
        self.photo_list_frame_header.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.photo_list_canvas.grid(row=1, column=0, sticky='nsew')
        self.photo_list_scrollbar.grid(row=1, column=1, sticky='ns')

        # place the Frame on the Canvas
        self.photo_list_canvas.create_window(
                (0,0),
                window=self.photo_list_holder,
                anchor='nw',
                tags='self.photo_list_holder',
                width=self.sidebar_width-13,
                )

        # bind resizing of canvas scrollregion
        self.photo_list_holder.bind('<Configure>', self.on_photo_list_holder_configure)

        self.thumbbtn_photo_list = {}
        self.draw_photo_list_frame()

    def on_photo_list_holder_configure(self, e):
        self.photo_list_canvas.configure(scrollregion=self.photo_list_canvas.bbox('all'))

    def on_photo_list_scroll(self, e):
        if e.num == 4 or e.delta == 120 or e.delta == 1:
            number = -1
        elif e.num == 5 or e.delta == -120 or e.delta == -1:
            number = 1
        else:
            print(f'Errors when scrolling photo_list {e}')

        #  print(f'Scrolling list {number} units, event {e} from {e.widget}')
        self.photo_list_canvas.yview_scroll(number, 'units')

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

        self.draw_input_folders()
        self.toggle_input_folders()

    def draw_input_folders(self):
        # remove all widgets from options_frame
        # this doesn't destroy them
        for folder in self.checkbtn_input_dirs:
            #  self.checkbtn_input_dirs[folder].pack_forget()
            self.checkbtn_input_dirs[folder].grid_forget()

        # repack them in order
        # first row (0) is the button
        ri = 1
        for folder in sorted(self.all_dirs):
            folder_name = basename(folder)

            # create the Checkbutton
            if not folder in self.checkbtn_input_dirs:
                self.checkbtn_input_state[folder] = tk.IntVar(value=1)
                self.checkbtn_input_dirs[folder] = tk.Checkbutton(self.input_frame,
                        text=folder_name,
                        command=self.toggle_input_folders,
                        background=self.options_frame.cget('background'),
                        variable=self.checkbtn_input_state[folder],
                        )

            # pack it
            #  print(f'Packing {folder}')
            #  self.checkbtn_input_dirs[folder].pack(fill='x')
            self.checkbtn_input_dirs[folder].grid(row=ri, column=0, sticky='ew')
            ri += 1

        # destroy unused Checkbutton if you want
        #  for folder in self.checkbtn_input_dirs:
            #  if not folder in self.all_dirs:
                #  self.checkbtn_input_dirs[folder].destroy

    def draw_photo_list_frame(self):
        '''pack all acvite ThumbButton'''
        for pic in self.thumbbtn_photo_list:
            #  self.thumbbtn_photo_list[pic].pack_forget()
            self.thumbbtn_photo_list[pic].grid_forget()

        # they start at the first row
        ri = 0
        for pic in self.photo_list:
            if not pic in self.thumbbtn_photo_list:
                self.thumbbtn_photo_list[pic] = ThumbButton(
                        #  self.photo_list_frame,
                        #  self.photo_list_canvas,
                        self.photo_list_holder,
                        self.photo_info[pic],
                        bg='powder blue',
                        #  thumb_btn_width=self.sidebar_width,
                        thumb_btn_width=self.sidebar_width-13,
                        )

                self.thumbbtn_photo_list[pic].photo_text.bind('<Enter>',
                        self.photo_list_highlight)
                self.thumbbtn_photo_list[pic].photo_text.bind('<Leave>',
                        self.photo_list_highlight)

                self.thumbbtn_photo_list[pic].bind('<4>',
                        self.on_photo_list_scroll)
                self.thumbbtn_photo_list[pic].bind('<5>',
                        self.on_photo_list_scroll)
                self.thumbbtn_photo_list[pic].bind('<MouseWheel>',
                        self.on_photo_list_scroll)

                self.thumbbtn_photo_list[pic].thumb_label.bind('<4>',
                        self.on_photo_list_scroll)
                self.thumbbtn_photo_list[pic].thumb_label.bind('<5>',
                        self.on_photo_list_scroll)
                self.thumbbtn_photo_list[pic].thumb_label.bind('<MouseWheel>',
                        self.on_photo_list_scroll)

                #  self.thumbbtn_photo_list[pic].photo_text.bind('<4>',
                        #  self.on_photo_list_scroll)
                #  self.thumbbtn_photo_list[pic].photo_text.bind('<5>',
                        #  self.on_photo_list_scroll)
                #  self.thumbbtn_photo_list[pic].photo_text.bind('<MouseWheel>',
                        #  self.on_photo_list_scroll)

                #  self.thumbbtn_photo_list[pic].photo_text.bind('<Double-Button-1>',
                        #  self.on_photo_list_doubleclick)
                self.thumbbtn_photo_list[pic].photo_text.label_widget.bind('<4>',
                        self.on_photo_list_scroll)
                self.thumbbtn_photo_list[pic].photo_text.label_widget.bind('<5>',
                        self.on_photo_list_scroll)
                self.thumbbtn_photo_list[pic].photo_text.label_widget.bind('<MouseWheel>',
                        self.on_photo_list_scroll)

                self.thumbbtn_photo_list[pic].photo_text.label_widget.bind('<Double-Button-1>',
                        self.on_photo_list_doubleclick)

            #  self.thumbbtn_photo_list[pic].pack(fill='x')
            self.thumbbtn_photo_list[pic].grid(row=ri, column=0, sticky='ew')
            ri += 1

    def on_photo_list_doubleclick(self, e):
        #  print(f'Doubleclick on {e.widget} generated by {e}')
        #  print(f'Parent {e.widget.master}')
        #  print(f'PhotoInfo.photo {e.widget.master.photo_info.photo}')
        #  self.photo_frame.seek_photo(e.widget.master.photo_info.photo)
        self.photo_frame.seek_photo(e.widget.master.master.photo_info.photo)

    def photo_list_highlight(self, e):
        #  print(f'Event type {e.type}')
        #  print(f'Event widget {e.widget}')
        if e.type == '7': # 'Enter'
            #  e.widget.config(state=tk.ACTIVE)
            e.widget.label_widget.config(state=tk.ACTIVE)
        elif e.type == '8': # 'Leave'
            #  e.widget.config(state=tk.NORMAL)
            e.widget.label_widget.config(state=tk.NORMAL)
        else:
            print(f'Unrecognized event {e}')

    def toggle_input_folders(self):
        #  print(f'Toggling something')
        # untoggling every folder is a bad idea
        self.active_dirs = []

        for folder in self.checkbtn_input_dirs:
            #  print(f'Folder {folder} has value {self.checkbtn_input_state[folder].get()}')
            if self.checkbtn_input_state[folder].get() == 1:
                self.active_dirs.append(folder)
                self.last_input_folder = folder

        # if no folder is toggled, reactivate the last toggled one
        if len(self.active_dirs) == 0:
            self.active_dirs = [self.last_input_folder]
            self.checkbtn_input_state[self.last_input_folder].set(1)
            print(f'Retoggling {self.last_input_folder}')

        #  print(f'Active dirs {self.active_dirs}')
        self.populate_photo_list()

        self.populate_info()
        #  self.populate_info_ray()
        self.draw_photo_list_frame()

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
        self.output_folder = out_dir

    def add_to_selection(self, photo_frame_which):
        print()
        # if the layout only shows the primary frame, add the pic from that
        if photo_frame_which == 'secondary' and not self.layout_num in self.layout_is_double:
            print(f'Adding from primary')
            photo_frame_which = 'primary'
        
        if photo_frame_which == 'primary':
            pic_name = self.photo_frame.photo_list[self.photo_frame.photo_index]
        elif photo_frame_which == 'secondary':
            pic_name = self.photo_frame_bis.photo_list[self.photo_frame_bis.photo_index]
        else:
            print(f'Unrecognized frame {photo_frame_which}')
            return -1

        if pic_name in self.selection_list:
            self.selection_list.remove(pic_name)
            print(f'{PhotoFrame.format_color(None, "De-selected", "tomato")} {basename(pic_name)}, selection_list is now {len(self.selection_list)} long')
        else:
            self.selection_list.append(pic_name)
            print(f'{PhotoFrame.format_color(None, "Selected", "lawn green")} {basename(pic_name)}, selection_list is now {len(self.selection_list)} long')

    def save_selection(self):
        #  out_dir = self.output_folder_var.get()
        out_dir = self.output_folder
        print()

        if out_dir == 'Not set':
            print(f'{PhotoFrame.format_color(None, "Set", "indian red")} the output folder before saving the selection_list')
            return -1

        if len(self.selection_list) == 0:
            print(f'{PhotoFrame.format_color(None, "Add", "indian red")} pictures to the selection_list before saving it')
            return -1

        out_dir_content = set(listdir(out_dir))

        #  print(f'Saving {len(self.selection_list)} pics in {out_dir}')
        print(f'{PhotoFrame.format_color(None, "Saving", "spring green")} {len(self.selection_list)} pics in folder: {out_dir}')
        for pic in self.selection_list:
            if basename(pic) in out_dir_content:
                print(f'{basename(pic)} is already in out_dir, ignoring it')
            else:
                copy2(pic, out_dir)

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
        self.metadata_frame = tk.Frame(self.root,
                width=self.sidebar_width,
                height=100,
                bg='dark orange')
        self.options_frame = tk.Frame(self.root,
                width=self.sidebar_width,
                height=100,
                bg='SeaGreen1')

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
        self.options_frame.grid(row=0, column=1, sticky='nsew')
        #  self.options_frame.grid(row=0, column=1, sticky='ns')

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
        self.options_frame.grid(row=1, column=1, sticky='nsew')
        #  self.options_frame.grid(row=1, column=1, sticky='ns')

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
        #  print('\nSTARTING MAINLOOP\n')
        self.root.mainloop()

    def finish_setup(self):
        #  print('\nfinishing setup\n')
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

    def print_widget_info(self, wid, level=0):
        colorz = [
        'dark olive green',
        'olive drab',
        'lawn green',
        #  'chart reuse',
        #  'dark green',
        'green',
        #  'forest green',
        'lime',
        'green yellow',
        #  'lime green',
        'sea green',
        'light green',
        'pale green',
        'dark sea green',
        'medium spring green',
        'spring green',
        ]
        #  print(f'{PhotoFrame.format_color(None, colorz[level], colorz[level])} ', end='')
        print(f'{PhotoFrame.format_color(None, wid, colorz[level])}', end='')
        print(f' w {wid.winfo_width()} h {wid.winfo_height()} rw {PhotoFrame.format_color(None, wid.winfo_reqwidth(), "green")} rh {wid.winfo_reqheight()} x {wid.winfo_x()} y {wid.winfo_y()}')
        #  print(f'{wid} {wid.winfo_class()}')

    def print_all_widget_info_BFS(self, wid_queue):
        #  self.print_widget_info(wid_queue)
        while not wid_queue.empty():
            wid = wid_queue.get()
            self.print_widget_info(wid)
            for child in wid.winfo_children():
                wid_queue.put(child)

    def print_all_widget_info_DFS(self, wid, level):
        self.print_widget_info(wid, level)
        for child in wid.winfo_children():
            self.print_all_widget_info_DFS(child, level+1)

    def debug(self):
        #  print(f'debugging')
        self.photo_frame.debug()

        #  wid_queue = Queue()
        #  wid_queue.put(self.root)
        #  self.print_all_widget_info_BFS(wid_queue)

        self.print_all_widget_info_DFS(self.root, 0)
