import tkinter as tk
from PIL import ImageTk, Image
from math import sqrt
from math import floor
from math import log
from os.path import basename

class PhotoFrame(tk.Frame):
    def __init__(self, parent, photo_list, frame_name, **kwargs):
        # init Frame, standard constructor
        tk.Frame.__init__(self, parent, **kwargs)

        self.photo_index = 0
        self.photo_list = photo_list.copy()

        self.frame_name = frame_name

        # setup grid for this widget
        #  self.grid_rowconfigure(0, weight=1, minsize=60)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create child widgets
        # background frame to fill the grid
        self.top_frame = tk.Frame(self,bg='light cyan',width=450,height=50)
        self.top_frame.grid(row=0, column=0, sticky="nsew")

        # image label
        self.image_label = tk.Label(self)

        self.resampling_mode = Image.NEAREST
        #  self.resampling_mode = Image.BILINEAR
        #  self.resampling_mode = Image.BICUBIC
        #  self.resampling_mode = Image.LANCZOS

        # log scale, actual zoom: zoom_base**zoom_level
        self.zoom_base = sqrt(2)
        self.zoom_level = 0
        #  self.calc_zoom_level() 
        # XXX this fails because the mainloop has not started
        # width and height are still 1

        self.mov_x = 0
        self.mov_y = 0
        # you move delta pixel regardless of zoom_level
        # when zooming the function will take care of leaving a fixed point
        self.mov_delta = 50 

        self.load_photo()

        self.bind('<Configure>', self.do_resize)

        #  self.show_photo()

        #  print(f'\nfinished init for ', end='')
        #  self.print_color(f'{self.frame_name}')

    def load_photo(self):
        '''load a photo and relatives attributes (wid, hei)'''
        self.current_photo = self.photo_list[self.photo_index]
        self.cur_image = Image.open(self.current_photo)
        self.cur_wid, self.cur_hei = self.cur_image.size

    #  def change_photo(self, direction, reset_pos=True):
    def change_photo(self, direction):
        #  print(f'change photo {self.format_color(direction, "blue1")}')

        if direction == 'forward':
            self.photo_index = (self.photo_index + 1 ) % len(self.photo_list)
        elif direction == 'backward':
            self.photo_index = (self.photo_index - 1 ) % len(self.photo_list)
        else:
            print(f'unrecognized changing direction {direction}')
            return 0 

        self.load_photo()

        #  if reset_pos:
        # reset the zoom_level and the position
        self.calc_zoom_level()
        self.mov_x = 0
        self.mov_y = 0

        self.show_photo()

    def calc_zoom_level(self):
        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        if self.cur_wid < widget_wid and self.cur_hei < widget_hei:
            # the original photo is smaller than the widget
            self.zoom_level = 0
        else:
            ratio = min( widget_wid/self.cur_wid, widget_hei/self.cur_hei)
            self.zoom_level = log(ratio, self.zoom_base)

        #  print(f'zooming ', end='')
        #  self.print_color(f'{basename(current_photo)}')
        #  print()
        #  print(f'do calc_zoom_level photo {self.format_color(f"{basename(self.current_photo)}", "blue1")}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'zoom_level is now {self.format_color(self.zoom_level, "blue1")}')

        # find zoom_level so that
        # cur_wid * ( zoom_base ** zoom_level ) = widget_wid
        # and analogously for hei

    def move_photo(self, direction):
        '''slide a region as big as the widget around the *zoomed* photo'''
        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = self.cur_wid * zoom
        zoom_hei = self.cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        print()
        print(f'move_photo {self.format_color(direction, "dark turquoise")}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'zoom_level {self.zoom_level} zoom {zoom:.4f} zoom_wid {zoom_wid:.4f} zoom_hei {zoom_hei:.4f}')
        #  print(f'self.mov_x + widget_wid {self.mov_x + widget_wid} self.mov_y + widget_hei {self.mov_y + widget_hei}')

        # NOTE some of these values will not be legal (a small photo in a large
        # widget will get on right a negative amount in mov_x)
        # do_resize will set mov_x to the highest possible legal value
        # FIXME the boundaries should be on the *zoomed* photo
        if direction == 'right':
            self.mov_x += self.mov_delta
            if self.mov_x + widget_wid > zoom_wid:
                self.mov_x = zoom_wid - widget_wid
                print('\a', end='')
                print(f'hit {self.format_color(direction, "sandy brown")} border, mov_x = {self.mov_x}')

        elif direction == 'left':
            self.mov_x -= self.mov_delta
            if self.mov_x < 0:
                self.mov_x = 0
                print('\a', end='')
                print(f'hit {self.format_color(direction, "sandy brown")} border, mov_x = {self.mov_x}')

        elif direction == 'up':
            self.mov_y -= self.mov_delta
            if self.mov_y < 0:
                self.mov_y = 0
                print('\a', end='')
                print(f'hit {self.format_color(direction, "sandy brown")} border, mov_y = {self.mov_y}')

        elif direction == 'down':
            self.mov_y += self.mov_delta
            if self.mov_y + widget_hei > zoom_hei:
                self.mov_y = zoom_hei - widget_hei
                print('\a', end='')
                print(f'hit {self.format_color(direction, "sandy brown")} border, mov_y = {self.mov_y}')

        elif direction == 'reset':
            self.mov_x = 0
            self.mov_y = 0

        else:
            print(f'unrecognized moving direction {direction}')
            return 0 

        self.show_photo()

    def zoom_photo(self, direction, rel_x=-1, rel_y=-1):
        '''change zoom level, recalculate mov_x mov_y so that a point stands still'''

        old_zoom = self.zoom_base ** self.zoom_level
        old_zoom_wid = self.cur_wid * old_zoom
        old_zoom_hei = self.cur_hei * old_zoom

        if direction == 'in':
            self.zoom_level += 1

        elif direction == 'out':
            self.zoom_level -= 1

        elif direction == 'reset':
            self.calc_zoom_level()

        else:
            print(f'unrecognized zooming direction {direction}')
            return 0 

        new_zoom = self.zoom_base ** self.zoom_level
        new_zoom_wid = self.cur_wid * new_zoom
        new_zoom_hei = self.cur_hei * new_zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        print()
        print(f'zoomed {self.format_color(direction, "dark turquoise")}')

        if rel_x == -1 or rel_y == -1:
            # find the center of the photo on the screen
            if new_zoom_wid < widget_wid and new_zoom_hei < widget_hei:
                rel_x = new_zoom_wid / 2
                rel_y = new_zoom_hei / 2
            elif new_zoom_wid >= widget_wid and new_zoom_hei < widget_hei:
                rel_x = widget_wid / 2
                rel_y = new_zoom_hei / 2
            elif new_zoom_wid < widget_wid and new_zoom_hei >= widget_hei:
                rel_x = new_zoom_wid / 2
                rel_y = widget_hei / 2
            elif new_zoom_wid >= widget_wid and new_zoom_hei >= widget_hei:
                rel_x = widget_wid / 2
                rel_y = widget_hei / 2

        if new_zoom_wid < widget_wid and new_zoom_hei < widget_hei:
            #  print(f'new_zoom photo {self.format_color("smaller", "green")} than frame')
            self.mov_x = 0
            self.mov_y = 0
        elif new_zoom_wid >= widget_wid and new_zoom_hei < widget_hei:
            #  print(f'new_zoom photo {self.format_color("wider", "green")} than frame')
            self.mov_x = ( self.mov_x/old_zoom + rel_x/old_zoom - rel_x/new_zoom) * new_zoom
            self.mov_y = 0
        elif new_zoom_wid < widget_wid and new_zoom_hei >= widget_hei:
            #  print(f'new_zoom photo {self.format_color("taller", "green")} than frame')
            self.mov_x = 0
            self.mov_y = ( self.mov_y/old_zoom + rel_y/old_zoom - rel_y/new_zoom) * new_zoom
        elif new_zoom_wid >= widget_wid and new_zoom_hei >= widget_hei:
            #  print(f'new_zoom photo {self.format_color("larger", "green")} than frame')
            self.mov_x = ( self.mov_x/old_zoom + rel_x/old_zoom - rel_x/new_zoom) * new_zoom
            self.mov_y = ( self.mov_y/old_zoom + rel_y/old_zoom - rel_y/new_zoom) * new_zoom

        #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')

        self.do_resize('zoom_photo')

        self.show_photo()

    def do_resize(self, e=None):
        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = self.cur_wid * zoom
        zoom_hei = self.cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        #  print()
        #  print(f'do_resize {self.format_color(f"{basename(self.current_photo)}", "blue1")} generated by {e}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'pre  self.mov_x {self.mov_x} self.mov_y {self.mov_y}')

        if self.mov_x + widget_wid > zoom_wid:
            #  print(f'overflowing {self.format_color("right", "sandy brown")}')
            self.mov_x = zoom_wid - widget_wid

        if self.mov_x < 0:
            #  print(f'overflowing {self.format_color("left", "sandy brown")}')
            self.mov_x = 0

        if self.mov_y < 0:
            #  print(f'overflowing {self.format_color("top", "sandy brown")}')
            self.mov_y = 0

        if self.mov_y + widget_hei > zoom_hei:
            #  print(f'overflowing {self.format_color("bottom", "sandy brown")}')
            self.mov_y = zoom_hei - widget_hei

        #  print(f'post self.mov_x {self.mov_x} self.mov_y {self.mov_y}')

        self.show_photo()

    def show_photo(self):
        print()
        print(f'current index {self.photo_index} photo ', end='')
        self.print_color(f'{basename(self.current_photo)}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'widget reqwidth {self.winfo_reqwidth()} reqheight {self.winfo_reqheight()}')

        zoom = self.zoom_base ** self.zoom_level
        #  zoom_wid = cur_wid * zoom
        #  zoom_hei = cur_hei * zoom
        zoom_wid = floor(self.cur_wid * zoom)
        zoom_hei = floor(self.cur_hei * zoom)

        #  print(f'zoom_level {self.zoom_level} zoom {zoom:.4f} zoom_wid {zoom_wid:.4f} zoom_hei {zoom_hei:.4f}')

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        if zoom_wid < widget_wid and zoom_hei < widget_hei:
            #  print(f'zoomed photo {self.format_color("smaller", "green")} than frame')
            # center it, disregard mov_x and mov_y
            x_pos = ( widget_wid - zoom_wid ) / 2
            y_pos = ( widget_hei - zoom_hei ) / 2
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            region = (0, 0, self.cur_wid, self.cur_hei)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(resized_dim, self.resampling_mode, region)

        elif zoom_wid >= widget_wid and zoom_hei < widget_hei:
            #  print(f'zoomed photo {self.format_color("wider", "green")} than frame')
            x_pos = 0
            y_pos = ( widget_hei - zoom_hei ) / 2
            #  resized_dim = (widget_wid, cur_hei)
            #  resized_dim = (zoom_wid, zoom_hei)
            resized_dim = (widget_wid, zoom_hei)
            # region width should REDUCE with higher zoom
            #  region = (self.mov_x, 0, self.mov_x+widget_wid, cur_hei)
            #  region = (self.mov_x, 0, self.mov_x+widget_wid/zoom, cur_hei)
            region = (self.mov_x/zoom, 0, (self.mov_x+widget_wid)/zoom, self.cur_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(resized_dim, self.resampling_mode, region)

        elif zoom_wid < widget_wid and zoom_hei >= widget_hei:
            #  print(f'zoomed photo {self.format_color("taller", "green")} than frame')
            x_pos = ( widget_wid - zoom_wid ) / 2
            y_pos = 0
            #  resized_dim = (cur_wid, widget_hei)
            resized_dim = (zoom_wid, widget_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei/zoom)
            region = (0, self.mov_y/zoom, self.cur_wid, (self.mov_y+widget_hei)/zoom)
            #  region = (self.mov_x, 0, self.mov_x+widget_wid, self.cur_hei)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(resized_dim, self.resampling_mode, region)

        elif zoom_wid >= widget_wid and zoom_hei >= widget_hei:
            #  print(f'zoomed photo {self.format_color("larger", "green")} than frame')
            # display it at (0,0)
            x_pos = 0
            y_pos = 0
            # resize it: pick only the region that will be shown
            resized_dim = (widget_wid, widget_hei)
            #  resized_dim = (zoom_wid, zoom_hei)
            region = (self.mov_x, self.mov_y, self.mov_x+widget_wid, self.mov_y+widget_hei)
            region = tuple(d/zoom for d in region)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(resized_dim, self.resampling_mode, region)

        #  print(f'resized_dim {resized_dim}')
        #  print(f'region {region}')
        # convert the photo for tkinter
        cur_image_res = ImageTk.PhotoImage(cur_image_res)
        # keep a reference to it to avoid garbage collection
        self.image_label.image = cur_image_res
        # display it
        self.image_label.configure(image=cur_image_res)
        self.image_label.place(x=x_pos, y=y_pos)

        # NOTE
        #  self.foto_aperte[nome_foto] = Image.open(path_name)
        #  self.pic_wid, self.pic_hei = self.foto_aperte[nome_foto].size
        #  myimg = ImageTk.PhotoImage(
        #  self.foto_aperte[nome_foto].resize((self.res_wid, self.res_hei), 0,
        #  (self.rw, self.rn, self.re, self.rs)))
        #  self.label1.configure(image=myimg)
        #  self.label1.image = myimg # devi tenere tu una referenza
        #  self.label1.place(x=self.lab_posx, y=self.lab_posy)

        # prendi le dimensioni della foto
        # moltiplicale per il livello attuale di zoom
        # 4 casi per le dimensioni *zoomate*
        # la foto e' piu' piccola:
            # centrala
        # la foto e' piu' alta della finestra:
            # centrala lateralmente
            # taglia sopra e sotto e permetti di muoverla
        # la foto e' piu' larga della finestra:
            # centrala in altezza
            # taglia destra e sinistra e permetti di muoverla
        # la foto e' piu' grande della finestra
            # tagliala
            # la posizione e' (0,0)

    def change_photo_list(self, new_list):
        '''look for the current_photo name in the new_list
        and let photo_index point there'''

        print()

        if self.current_photo in new_list:
            self.photo_index = new_list.index(self.current_photo)
            print(f'Found {self.current_photo} at index {self.photo_index} in {self.format_color_name(self.frame_name)}')
        else:
            print(f'Not found {self.current_photo} in {self.format_color_name(self.frame_name)}, setting photo_index to 0')
            self.photo_index = 0
            self.load_photo()

        self.photo_list = new_list.copy()
        self.show_photo()

    def debug(self):
        print(f'\n{self.format_color("debugging PhotoFrame", "yellow")}')

    def print_color(self, string):
        if self.frame_name == 'primary':
            color = 'red'
        else:
            color = 'green'
        print(self.format_color(string, color))

    def format_color_name(self, string):
        if self.frame_name == 'primary':
            color = 'red'
        else:
            color = 'green'
        return self.format_color(string, color)

    def format_color(self, string, color):
        cs = '\x1b[38;2;{};{};{}m{}\x1b[0m'

        # my colors
        if color == 'red1': r, g, b = 215, 0, 0
        elif color == 'green1': r, g, b = 0, 255, 0
        elif color == 'blue1': r, g, b = 50, 50, 255

        # list from https://www.rapidtables.com/web/color/RGB_Color.html
        elif color == 'Black': r, g, b = 0,0,0
        elif color == 'White': r, g, b = 255,255,255
        elif color == 'Red': r, g, b = 255,0,0
        elif color == 'Lime': r, g, b = 0,255,0
        elif color == 'Blue': r, g, b = 0,0,255
        elif color == 'Yellow': r, g, b = 255,255,0
        elif color == 'Cyan': r, g, b = 0,255,255
        elif color == 'Magenta': r, g, b = 255,0,255
        elif color == 'Silver': r, g, b = 192,192,192
        elif color == 'Gray': r, g, b = 128,128,128
        elif color == 'Maroon': r, g, b = 128,0,0
        elif color == 'Olive': r, g, b = 128,128,0
        elif color == 'Green': r, g, b = 0,128,0
        elif color == 'Purple': r, g, b = 128,0,128
        elif color == 'Teal': r, g, b = 0,128,128
        elif color == 'Navy': r, g, b = 0,0,128
        elif color == 'maroon': r, g, b = 128,0,0
        elif color == 'dark red': r, g, b = 139,0,0
        elif color == 'brown': r, g, b = 165,42,42
        elif color == 'firebrick': r, g, b = 178,34,34
        elif color == 'crimson': r, g, b = 220,20,60
        elif color == 'red': r, g, b = 255,0,0
        elif color == 'tomato': r, g, b = 255,99,71
        elif color == 'coral': r, g, b = 255,127,80
        elif color == 'indian red': r, g, b = 205,92,92
        elif color == 'light coral': r, g, b = 240,128,128
        elif color == 'dark salmon': r, g, b = 233,150,122
        elif color == 'salmon': r, g, b = 250,128,114
        elif color == 'light salmon': r, g, b = 255,160,122
        elif color == 'orange red': r, g, b = 255,69,0
        elif color == 'dark orange': r, g, b = 255,140,0
        elif color == 'orange': r, g, b = 255,165,0
        elif color == 'gold': r, g, b = 255,215,0
        elif color == 'dark golden rod': r, g, b = 184,134,11
        elif color == 'golden rod': r, g, b = 218,165,32
        elif color == 'pale golden rod': r, g, b = 238,232,170
        elif color == 'dark khaki': r, g, b = 189,183,107
        elif color == 'khaki': r, g, b = 240,230,140
        elif color == 'olive': r, g, b = 128,128,0
        elif color == 'yellow': r, g, b = 255,255,0
        elif color == 'yellow green': r, g, b = 154,205,50
        elif color == 'dark olive green': r, g, b = 85,107,47
        elif color == 'olive drab': r, g, b = 107,142,35
        elif color == 'lawn green': r, g, b = 124,252,0
        elif color == 'chart reuse': r, g, b = 127,255,0
        elif color == 'green yellow': r, g, b = 173,255,47
        elif color == 'dark green': r, g, b = 0,100,0
        elif color == 'green': r, g, b = 0,128,0
        elif color == 'forest green': r, g, b = 34,139,34
        elif color == 'lime': r, g, b = 0,255,0
        elif color == 'lime green': r, g, b = 50,205,50
        elif color == 'light green': r, g, b = 144,238,144
        elif color == 'pale green': r, g, b = 152,251,152
        elif color == 'dark sea green': r, g, b = 143,188,143
        elif color == 'medium spring green': r, g, b = 0,250,154
        elif color == 'spring green': r, g, b = 0,255,127
        elif color == 'sea green': r, g, b = 46,139,87
        elif color == 'medium aqua marine': r, g, b = 102,205,170
        elif color == 'medium sea green': r, g, b = 60,179,113
        elif color == 'light sea green': r, g, b = 32,178,170
        elif color == 'dark slate gray': r, g, b = 47,79,79
        elif color == 'teal': r, g, b = 0,128,128
        elif color == 'dark cyan': r, g, b = 0,139,139
        elif color == 'aqua': r, g, b = 0,255,255
        elif color == 'cyan': r, g, b = 0,255,255
        elif color == 'light cyan': r, g, b = 224,255,255
        elif color == 'dark turquoise': r, g, b = 0,206,209
        elif color == 'turquoise': r, g, b = 64,224,208
        elif color == 'medium turquoise': r, g, b = 72,209,204
        elif color == 'pale turquoise': r, g, b = 175,238,238
        elif color == 'aqua marine': r, g, b = 127,255,212
        elif color == 'powder blue': r, g, b = 176,224,230
        elif color == 'cadet blue': r, g, b = 95,158,160
        elif color == 'steel blue': r, g, b = 70,130,180
        elif color == 'corn flower blue': r, g, b = 100,149,237
        elif color == 'deep sky blue': r, g, b = 0,191,255
        elif color == 'dodger blue': r, g, b = 30,144,255
        elif color == 'light blue': r, g, b = 173,216,230
        elif color == 'sky blue': r, g, b = 135,206,235
        elif color == 'light sky blue': r, g, b = 135,206,250
        elif color == 'midnight blue': r, g, b = 25,25,112
        elif color == 'navy': r, g, b = 0,0,128
        elif color == 'dark blue': r, g, b = 0,0,139
        elif color == 'medium blue': r, g, b = 0,0,205
        elif color == 'blue': r, g, b = 0,0,255
        elif color == 'royal blue': r, g, b = 65,105,225
        elif color == 'blue violet': r, g, b = 138,43,226
        elif color == 'indigo': r, g, b = 75,0,130
        elif color == 'dark slate blue': r, g, b = 72,61,139
        elif color == 'slate blue': r, g, b = 106,90,205
        elif color == 'medium slate blue': r, g, b = 123,104,238
        elif color == 'medium purple': r, g, b = 147,112,219
        elif color == 'dark magenta': r, g, b = 139,0,139
        elif color == 'dark violet': r, g, b = 148,0,211
        elif color == 'dark orchid': r, g, b = 153,50,204
        elif color == 'medium orchid': r, g, b = 186,85,211
        elif color == 'purple': r, g, b = 128,0,128
        elif color == 'thistle': r, g, b = 216,191,216
        elif color == 'plum': r, g, b = 221,160,221
        elif color == 'violet': r, g, b = 238,130,238
        elif color == 'magenta': r, g, b = 255,0,255
        elif color == 'orchid': r, g, b = 218,112,214
        elif color == 'medium violet red': r, g, b = 199,21,133
        elif color == 'pale violet red': r, g, b = 219,112,147
        elif color == 'deep pink': r, g, b = 255,20,147
        elif color == 'hot pink': r, g, b = 255,105,180
        elif color == 'light pink': r, g, b = 255,182,193
        elif color == 'pink': r, g, b = 255,192,203
        elif color == 'antique white': r, g, b = 250,235,215
        elif color == 'beige': r, g, b = 245,245,220
        elif color == 'bisque': r, g, b = 255,228,196
        elif color == 'blanched almond': r, g, b = 255,235,205
        elif color == 'wheat': r, g, b = 245,222,179
        elif color == 'corn silk': r, g, b = 255,248,220
        elif color == 'lemon chiffon': r, g, b = 255,250,205
        elif color == 'light golden rod yellow': r, g, b = 250,250,210
        elif color == 'light yellow': r, g, b = 255,255,224
        elif color == 'saddle brown': r, g, b = 139,69,19
        elif color == 'sienna': r, g, b = 160,82,45
        elif color == 'chocolate': r, g, b = 210,105,30
        elif color == 'peru': r, g, b = 205,133,63
        elif color == 'sandy brown': r, g, b = 244,164,96
        elif color == 'burly wood': r, g, b = 222,184,135
        elif color == 'tan': r, g, b = 210,180,140
        elif color == 'rosy brown': r, g, b = 188,143,143
        elif color == 'moccasin': r, g, b = 255,228,181
        elif color == 'navajo white': r, g, b = 255,222,173
        elif color == 'peach puff': r, g, b = 255,218,185
        elif color == 'misty rose': r, g, b = 255,228,225
        elif color == 'lavender blush': r, g, b = 255,240,245
        elif color == 'linen': r, g, b = 250,240,230
        elif color == 'old lace': r, g, b = 253,245,230
        elif color == 'papaya whip': r, g, b = 255,239,213
        elif color == 'sea shell': r, g, b = 255,245,238
        elif color == 'mint cream': r, g, b = 245,255,250
        elif color == 'slate gray': r, g, b = 112,128,144
        elif color == 'light slate gray': r, g, b = 119,136,153
        elif color == 'light steel blue': r, g, b = 176,196,222
        elif color == 'lavender': r, g, b = 230,230,250
        elif color == 'floral white': r, g, b = 255,250,240
        elif color == 'alice blue': r, g, b = 240,248,255
        elif color == 'ghost white': r, g, b = 248,248,255
        elif color == 'honeydew': r, g, b = 240,255,240
        elif color == 'ivory': r, g, b = 255,255,240
        elif color == 'azure': r, g, b = 240,255,255
        elif color == 'snow': r, g, b = 255,250,250
        elif color == 'black': r, g, b = 0,0,0
        elif color == 'dim gray': r, g, b = 105,105,105
        elif color == 'gray': r, g, b = 128,128,128
        elif color == 'dark gray': r, g, b = 169,169,169
        elif color == 'silver': r, g, b = 192,192,192
        elif color == 'light gray': r, g, b = 211,211,211
        elif color == 'gainsboro': r, g, b = 220,220,220
        elif color == 'white smoke': r, g, b = 245,245,245
        elif color == 'white': r, g, b = 255,255,255
        else: r, g, b = 255,255,255

        return cs.format(r, g, b, string)
