import tkinter as tk
from PIL import ImageTk, Image
from math import sqrt
from math import floor
from math import log
from os.path import basename

from utils import print_color
from utils import format_color_name
from utils import format_color


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
        self.top_frame = tk.Frame(self, bg="light cyan", width=450, height=50)
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

        self.bind("<Configure>", self.do_resize)

        #  self.show_photo()

        #  print(f'\nfinished init for ', end='')
        #  print_color(f'{self.frame_name}', self.frame_name)

    def load_photo(self):
        """load a photo and relatives attributes (wid, hei)"""
        self.current_photo = self.photo_list[self.photo_index]
        self.cur_image = Image.open(self.current_photo)
        self.cur_wid, self.cur_hei = self.cur_image.size

    def change_photo(self, direction):
        #  print(f'change photo {format_color(direction, "blue1")}')

        if direction == "forward":
            self.photo_index = (self.photo_index + 1) % len(self.photo_list)
        elif direction == "backward":
            self.photo_index = (self.photo_index - 1) % len(self.photo_list)
        else:
            print(f"unrecognized changing direction {direction}")
            return 0

        self.load_photo()

        #  if reset_pos:
        # reset the zoom_level and the position
        self.calc_zoom_level()
        self.mov_x = 0
        self.mov_y = 0

        print(f"current index {self.photo_index} photo ", end="")
        print_color(f"{basename(self.current_photo)}", self.frame_name)

        self.show_photo()

    def seek_photo(self, name):
        if name in self.photo_list:
            self.photo_index = self.photo_list.index(name)

            self.load_photo()

            #  if reset_pos:
            # reset the zoom_level and the position
            self.calc_zoom_level()
            self.mov_x = 0
            self.mov_y = 0

            print(f"Found at index {self.photo_index} photo ", end="")
            print_color(f"{basename(self.current_photo)}", self.frame_name)

            self.show_photo()
        else:
            print(f"Not found {name} in photo_list")

    def calc_zoom_level(self):
        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        if self.cur_wid < widget_wid and self.cur_hei < widget_hei:
            # the original photo is smaller than the widget
            self.zoom_level = 0
        else:
            ratio = min(widget_wid / self.cur_wid, widget_hei / self.cur_hei)
            self.zoom_level = log(ratio, self.zoom_base)

        #  print(f'zooming ', end='')
        #  print_color(f'{basename(current_photo)}', self.frame_name)
        #  print()
        #  print(f'do calc_zoom_level photo {format_color(f"{basename(self.current_photo)}", "blue1")}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'zoom_level is now {format_color(self.zoom_level, "blue1")}')

        # find zoom_level so that
        # cur_wid * ( zoom_base ** zoom_level ) = widget_wid
        # and analogously for hei

    def move_photo(self, direction):
        """slide a region as big as the widget around the *zoomed* photo"""
        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = self.cur_wid * zoom
        zoom_hei = self.cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        print()
        print(f'move_photo {format_color(direction, "dark turquoise")}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'zoom_level {self.zoom_level} zoom {zoom:.4f} zoom_wid {zoom_wid:.4f} zoom_hei {zoom_hei:.4f}')
        #  print(f'self.mov_x + widget_wid {self.mov_x + widget_wid} self.mov_y + widget_hei {self.mov_y + widget_hei}')

        # NOTE some of these values will not be legal (a small photo in a large
        # widget will get on right a negative amount in mov_x)
        # do_resize will set mov_x to the highest possible legal value
        # FIXME the boundaries should be on the *zoomed* photo
        if direction == "right":
            self.mov_x += self.mov_delta
            if self.mov_x + widget_wid > zoom_wid:
                self.mov_x = zoom_wid - widget_wid
                print("\a", end="")
                print(
                    f'hit {format_color(direction, "sandy brown")} border, mov_x = {self.mov_x}'
                )

        elif direction == "left":
            self.mov_x -= self.mov_delta
            if self.mov_x < 0:
                self.mov_x = 0
                print("\a", end="")
                print(
                    f'hit {format_color(direction, "sandy brown")} border, mov_x = {self.mov_x}'
                )

        elif direction == "up":
            self.mov_y -= self.mov_delta
            if self.mov_y < 0:
                self.mov_y = 0
                print("\a", end="")
                print(
                    f'hit {format_color(direction, "sandy brown")} border, mov_y = {self.mov_y}'
                )

        elif direction == "down":
            self.mov_y += self.mov_delta
            if self.mov_y + widget_hei > zoom_hei:
                self.mov_y = zoom_hei - widget_hei
                print("\a", end="")
                print(
                    f'hit {format_color(direction, "sandy brown")} border, mov_y = {self.mov_y}'
                )

        elif direction == "reset":
            self.mov_x = 0
            self.mov_y = 0

        else:
            print(f"unrecognized moving direction {direction}")
            return 0

        self.show_photo()

    def click_photo_mouse(self, x, y):
        self.old_mouse_x = x
        self.old_mouse_y = y

        #  print()
        #  print(f'click_photo_{format_color("mouse", "dark turquoise")} x {x} y {y}')

    def move_photo_mouse(self, mouse_x, mouse_y):
        delta_x = self.old_mouse_x - mouse_x
        delta_y = self.old_mouse_y - mouse_y

        self.old_mouse_x = mouse_x
        self.old_mouse_y = mouse_y

        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = self.cur_wid * zoom
        zoom_hei = self.cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        #  print()
        #  print(f'move_photo_{format_color("mouse", "dark turquoise")} dx {delta_x} dy {delta_y}')

        self.mov_x += delta_x
        self.mov_y += delta_y

        if self.mov_x + widget_wid > zoom_wid:
            self.mov_x = zoom_wid - widget_wid
            #  print('\a', end='')
            print(
                f'hit {format_color("right", "sandy brown")} border, mov_x = {self.mov_x}'
            )

        if self.mov_x < 0:
            self.mov_x = 0
            #  print('\a', end='')
            print(
                f'hit {format_color("left", "sandy brown")} border, mov_x = {self.mov_x}'
            )

        if self.mov_y < 0:
            self.mov_y = 0
            #  print('\a', end='')
            print(
                f'hit {format_color("top", "sandy brown")} border, mov_y = {self.mov_y}'
            )

        if self.mov_y + widget_hei > zoom_hei:
            self.mov_y = zoom_hei - widget_hei
            #  print('\a', end='')
            print(
                f'hit {format_color("down", "sandy brown")} border, mov_y = {self.mov_y}'
            )

        self.show_photo()

    def zoom_photo(self, direction, rel_x=-1, rel_y=-1):
        """change zoom level, recalculate mov_x mov_y so that a point stands still"""

        old_zoom = self.zoom_base ** self.zoom_level
        old_zoom_wid = self.cur_wid * old_zoom
        old_zoom_hei = self.cur_hei * old_zoom

        if direction == "in":
            self.zoom_level += 1

        elif direction == "out":
            self.zoom_level -= 1

        elif direction == "reset":
            self.calc_zoom_level()

        else:
            print(f"unrecognized zooming direction {direction}")
            return 0

        new_zoom = self.zoom_base ** self.zoom_level
        new_zoom_wid = self.cur_wid * new_zoom
        new_zoom_hei = self.cur_hei * new_zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        print()
        print(f'zoomed {format_color(direction, "dark turquoise")}')

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
            #  print(f'new_zoom photo {format_color("smaller", "green")} than frame')
            self.mov_x = 0
            self.mov_y = 0
        elif new_zoom_wid >= widget_wid and new_zoom_hei < widget_hei:
            #  print(f'new_zoom photo {format_color("wider", "green")} than frame')
            self.mov_x = (
                self.mov_x / old_zoom + rel_x / old_zoom - rel_x / new_zoom
            ) * new_zoom
            self.mov_y = 0
        elif new_zoom_wid < widget_wid and new_zoom_hei >= widget_hei:
            #  print(f'new_zoom photo {format_color("taller", "green")} than frame')
            self.mov_x = 0
            self.mov_y = (
                self.mov_y / old_zoom + rel_y / old_zoom - rel_y / new_zoom
            ) * new_zoom
        elif new_zoom_wid >= widget_wid and new_zoom_hei >= widget_hei:
            #  print(f'new_zoom photo {format_color("larger", "green")} than frame')
            self.mov_x = (
                self.mov_x / old_zoom + rel_x / old_zoom - rel_x / new_zoom
            ) * new_zoom
            self.mov_y = (
                self.mov_y / old_zoom + rel_y / old_zoom - rel_y / new_zoom
            ) * new_zoom

        #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')

        self.do_resize("zoom_photo")

        self.show_photo()

    def do_resize(self, e=None):
        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = self.cur_wid * zoom
        zoom_hei = self.cur_hei * zoom

        widget_wid = self.winfo_width()
        widget_hei = self.winfo_height()

        #  print()
        #  print(f'do_resize {format_color(f"{basename(self.current_photo)}", "blue1")} generated by {e}')
        #  print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        #  print(f'current width {self.cur_wid} height {self.cur_hei}')
        #  print(f'pre  self.mov_x {self.mov_x} self.mov_y {self.mov_y}')

        if self.mov_x + widget_wid > zoom_wid:
            #  print(f'overflowing {format_color("right", "sandy brown")}')
            self.mov_x = zoom_wid - widget_wid

        if self.mov_x < 0:
            #  print(f'overflowing {format_color("left", "sandy brown")}')
            self.mov_x = 0

        if self.mov_y < 0:
            #  print(f'overflowing {format_color("top", "sandy brown")}')
            self.mov_y = 0

        if self.mov_y + widget_hei > zoom_hei:
            #  print(f'overflowing {format_color("bottom", "sandy brown")}')
            self.mov_y = zoom_hei - widget_hei

        #  print(f'post self.mov_x {self.mov_x} self.mov_y {self.mov_y}')

        self.show_photo()

    def show_photo(self):
        #  print()
        #  print(f'current index {self.photo_index} photo ', end='')
        #  print_color(f'{basename(self.current_photo)}', self.frame_name)
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
            #  print(f'zoomed photo {format_color("smaller", "green")} than frame')
            # center it, disregard mov_x and mov_y
            x_pos = (widget_wid - zoom_wid) / 2
            y_pos = (widget_hei - zoom_hei) / 2
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            region = (0, 0, self.cur_wid, self.cur_hei)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(
                resized_dim, self.resampling_mode, region
            )

        elif zoom_wid >= widget_wid and zoom_hei < widget_hei:
            #  print(f'zoomed photo {format_color("wider", "green")} than frame')
            x_pos = 0
            y_pos = (widget_hei - zoom_hei) / 2
            #  resized_dim = (widget_wid, cur_hei)
            #  resized_dim = (zoom_wid, zoom_hei)
            resized_dim = (widget_wid, zoom_hei)
            # region width should REDUCE with higher zoom
            #  region = (self.mov_x, 0, self.mov_x+widget_wid, cur_hei)
            #  region = (self.mov_x, 0, self.mov_x+widget_wid/zoom, cur_hei)
            region = (
                self.mov_x / zoom,
                0,
                (self.mov_x + widget_wid) / zoom,
                self.cur_hei,
            )
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(
                resized_dim, self.resampling_mode, region
            )

        elif zoom_wid < widget_wid and zoom_hei >= widget_hei:
            #  print(f'zoomed photo {format_color("taller", "green")} than frame')
            x_pos = (widget_wid - zoom_wid) / 2
            y_pos = 0
            #  resized_dim = (cur_wid, widget_hei)
            resized_dim = (zoom_wid, widget_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei)
            #  region = (0, self.mov_y, cur_wid, self.mov_y+widget_hei/zoom)
            region = (
                0,
                self.mov_y / zoom,
                self.cur_wid,
                (self.mov_y + widget_hei) / zoom,
            )
            #  region = (self.mov_x, 0, self.mov_x+widget_wid, self.cur_hei)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(
                resized_dim, self.resampling_mode, region
            )

        elif zoom_wid >= widget_wid and zoom_hei >= widget_hei:
            #  print(f'zoomed photo {format_color("larger", "green")} than frame')
            # display it at (0,0)
            x_pos = 0
            y_pos = 0
            # resize it: pick only the region that will be shown
            resized_dim = (widget_wid, widget_hei)
            #  resized_dim = (zoom_wid, zoom_hei)
            region = (
                self.mov_x,
                self.mov_y,
                self.mov_x + widget_wid,
                self.mov_y + widget_hei,
            )
            region = tuple(d / zoom for d in region)
            #  print(f'resized_dim {resized_dim} region {region} x_pos {x_pos} y_pos {y_pos}')
            #  print(f'self.mov_x {self.mov_x} self.mov_y {self.mov_y}')
            cur_image_res = self.cur_image.resize(
                resized_dim, self.resampling_mode, region
            )

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
        """look for the current_photo name in the new_list
        and let photo_index point there"""

        print()

        if self.current_photo in new_list:
            self.photo_index = new_list.index(self.current_photo)
            print(
                f"Found {self.current_photo} at index {self.photo_index} in {format_color_name(self.frame_name, self.frame_name)}"
            )
        else:
            print(
                f"Not found {self.current_photo} in {format_color_name(self.frame_name, self.frame_name)}, setting photo_index to 0"
            )
            self.photo_index = 0
            self.load_photo()

        self.photo_list = new_list.copy()
        self.show_photo()

    def debug(self):
        print(f'\n{format_color("debugging PhotoFrame", "yellow")}')

