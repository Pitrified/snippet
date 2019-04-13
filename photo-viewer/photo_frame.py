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
        self.top_frame = tk.Frame(self,bg='light cyan',width=450,height=50)
        self.top_frame.grid(row=0, column=0, sticky="nsew")

        #  self.image_frame = tk.Frame(self, bg='light cyan')
        self.image_label = tk.Label(self)

        # position them in the grid
        # not really, it will be manually placed
        #  self.image_label.grid(row=0, column=0, sticky="nsew")

        print('update_idletasks now')
        self.update_idletasks()
        # log scale, actual zoom: zoom_base**zoom_level
        #  self.zoom_level = 0
        self.zoom_base = sqrt(2)
        self.calc_zoom_level()

        self.mov_x = 0
        self.mov_y = 0
        # you move delta pixel regardless of zoom_level
        # when zooming the function will take care of leaving a fixed point
        self.mov_delta = 50 

        self.bind('<Configure>', self.do_resize)

        #  self.show_photo()

    def change_photo(self, direction):
        if direction == 'forward':
            self.photo_index = (self.photo_index + 1 ) % len(self.photo_list)
        elif direction == 'backward':
            self.photo_index = (self.photo_index - 1 ) % len(self.photo_list)
        else:
            print(f'unrecognized direction {direction}')
            return 0 

        self.calc_zoom_level()

        # reset the position
        self.mov_x = 0
        self.mov_y = 0

        self.show_photo()

    def calc_zoom_level(self):
        current_photo = self.photo_list[self.photo_index]
        cur_image = Image.open(current_photo)
        cur_wid, cur_hei = cur_image.size

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        ratio = min( widget_wid/cur_wid, widget_hei/cur_hei)
        self.zoom_level = log(ratio, self.zoom_base)

        #  print(f'zooming ', end='')
        #  self.print_color(f'{basename(current_photo)}')
        print(f'zooming photo {self.format_color(f"{basename(current_photo)}", "blue")}')
        print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        print(f'current width {cur_wid} height {cur_hei}')
        print(f'zoom_level is now {self.format_color(self.zoom_level, "blue")}')

        # find zoom_level so that
        # cur_wid * ( zoom_base ** zoom_level ) = widget_wid
        # and analogously for hei

    def move_photo(self, direction):
        '''slide a region as big as the widget around the *zoomed* photo'''
        current_photo = self.photo_list[self.photo_index]
        cur_image = Image.open(current_photo)
        cur_wid, cur_hei = cur_image.size

        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = cur_wid * zoom
        zoom_hei = cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        # NOTE some of these values will not be legal (a small photo in a large
        # widget will get on right a negative amount in mov_x)
        # do_resize will set mov_x to the highest possible legal value
        if direction == 'right':
            self.mov_x += self.mov_delta
            if self.mov_x + widget_wid > cur_wid:
                print('\a', end='') # bell
                self.mov_x = cur_wid - widget_wid

        elif direction == 'left':
            self.mov_x -= self.mov_delta
            if self.mov_x < 0:
                print('\a', end='')
                self.mov_x = 0

        elif direction == 'up':
            self.mov_y -= self.mov_delta
            if self.mov_y < 0:
                print('\a', end='')
                self.mov_y = 0

        elif direction == 'down':
            self.mov_y += self.mov_delta
            if self.mov_y + widget_hei > cur_hei:
                print('\a', end='')
                self.mov_y = cur_hei - widget_hei

        elif direction == 'reset':
            self.mov_x = 0
            self.mov_y = 0
        else:
            print(f'unrecognized direction {direction}')
            return 0 
        self.show_photo()

    def show_photo(self):
        #  print(f'frame {id(self)}')
        #  self.print_color(f'frame {self.frame_name}')
        #  print(f'widget x {self.winfo_x()} y {self.winfo_y()}')
        #  print(f'widget rootx {self.winfo_rootx()} rooty {self.winfo_rooty()}')
        #  print(f'widget reqwidth {self.winfo_reqwidth()} reqheight {self.winfo_reqheight()}')
        current_photo = self.photo_list[self.photo_index]
        #  self.cur_image = Image.open(current_photo)
        #  cur_wid, cur_hei = self.cur_image.size
        cur_image = Image.open(current_photo)
        cur_wid, cur_hei = cur_image.size
        print(f'current photo ', end='')
        self.print_color(f'{basename(current_photo)}')
        print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        print(f'current width {cur_wid} height {cur_hei}')

        zoom = self.zoom_base ** self.zoom_level
        #  zoom_wid = cur_wid * zoom
        #  zoom_hei = cur_hei * zoom
        zoom_wid = floor(cur_wid * zoom)
        zoom_hei = floor(cur_hei * zoom)
        print(f'zoom_level {self.zoom_level} zoom {zoom:.4f} zoom_wid {zoom_wid:.4f} zoom_hei {zoom_hei:.4f}')

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        if zoom_wid < widget_wid and zoom_hei < widget_hei:
            print(f'zoomed photo {self.format_color("smaller", "green")} than frame')
            # center it, disregard mov_x and mov_y
            x_pos = ( widget_wid - zoom_wid ) / 2
            y_pos = ( widget_hei - zoom_hei ) / 2
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            region = (0, 0, cur_wid, cur_hei)
            cur_image = cur_image.resize(resized_dim, 0, region)

        elif zoom_wid >= widget_wid and zoom_hei < widget_hei:
            print(f'zoomed photo wider than frame')
            x_pos = 0
            y_pos = ( widget_hei - zoom_hei ) / 2
            #  resized_dim = (widget_wid, cur_hei)
            #  resized_dim = (zoom_wid, zoom_hei)
            resized_dim = (widget_wid, zoom_hei)
            # region width should REDUCE with higher zoom
            #  region = (self.mov_x, 0, self.mov_x+widget_wid, cur_hei)
            #  region = (self.mov_x, 0, self.mov_x+widget_wid/zoom, cur_hei)
            region = (self.mov_x/zoom, 0, (self.mov_x+widget_wid)/zoom, cur_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei)
            cur_image = cur_image.resize(resized_dim, 0, region)

        elif zoom_wid < widget_wid and zoom_hei >= widget_hei:
            print(f'zoomed photo taller than frame')
            x_pos = ( widget_wid - zoom_wid ) / 2
            y_pos = 0
            #  resized_dim = (cur_wid, widget_hei)
            resized_dim = (zoom_wid, widget_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei/zoom)
            region = (0, self.mov_y/zoom, cur_wid, (self.mov_y+widget_hei)/zoom)
            #  region = (self.mov_x, 0, self.mov_x+widget_wid, cur_hei)
            cur_image = cur_image.resize(resized_dim, 0, region)

        elif zoom_wid >= widget_wid and zoom_hei >= widget_hei:
            print(f'zoomed photo larger than frame')
            # display it at (0,0)
            x_pos = 0
            y_pos = 0
            # resize it: pick only the region that will be shown
            resized_dim = (widget_wid, widget_hei)
            #  resized_dim = (zoom_wid, zoom_hei)
            region = (self.mov_x, self.mov_y, self.mov_x+widget_wid, self.mov_y+widget_hei)
            region = tuple(d/zoom for d in region)
            cur_image = cur_image.resize(resized_dim, 0, region)

        print(f'resized_dim {resized_dim}')
        print(f'region {region}')
        # convert the photo for tkinter
        cur_image = ImageTk.PhotoImage(cur_image)
        # keep a reference to it to avoid garbage collection
        self.image_label.image = cur_image
        # display it
        self.image_label.configure(image=cur_image)
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

    def print_color(self, string):
        if self.frame_name == 'primary':
            color = 'red'
        else:
            color = 'green'
        print(self.format_color(string, color))

    def format_color(self, string, color):
        cs = '\x1b[38;2;{};{};{}m{}\x1b[0m'
        if color == 'red':
            r, g, b = 255, 0, 0
        elif color == 'green':
            r, g, b = 0, 255, 0
        elif color == 'blue':
            r, g, b = 50, 50, 255

        return cs.format(r, g, b, string)

    def do_resize(self, e=None):
        current_photo = self.photo_list[self.photo_index]
        cur_image = Image.open(current_photo)
        cur_wid, cur_hei = cur_image.size

        self.calc_zoom_level()

        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = cur_wid * zoom
        zoom_hei = cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        if self.mov_x + widget_wid > cur_wid:
            self.mov_x = cur_wid - widget_wid

        if self.mov_x < 0:
            self.mov_x = 0

        if self.mov_y < 0:
            self.mov_y = 0

        if self.mov_y + widget_hei > cur_hei:
            self.mov_y = cur_hei - widget_hei

        self.show_photo()

    def change_photo_list(self, new_list):
        '''look for the current_photo name in the new_list
        and let photo_index point there'''
        current_photo = self.photo_list[self.photo_index]

        if current_photo in new_list:
            self.photo_index = new_list.index(current_photo)
        else:
            self.photo_index = 0

        self.photo_list = new_list.copy()

    def debug(self):
        print(f'debugging PhotoFrame')
