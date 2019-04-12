import tkinter as tk
from PIL import ImageTk, Image
from math import sqrt
from os.path import basename

class PhotoFrame(tk.Frame):
    def __init__(self, parent, photo_list, **kwargs):
        # init Frame, standard constructor
        tk.Frame.__init__(self, parent, **kwargs)

        self.photo_index = 0
        self.photo_list = photo_list.copy()

        # setup grid for this widget
        #  self.grid_rowconfigure(0, weight=1, minsize=60)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create child widgets
        # self.top_frame = tk.Frame(self,bg='light cyan',width=450,height=50)
        #  self.image_frame = tk.Frame(self, bg='light cyan')
        self.image_label = tk.Label(self)

        # position them in the grid
        # not really, it will be manually placed
        #  self.image_label.grid(row=0, column=0, sticky="nsew")

        # log scale, actual zoom: zoom_base**zoom_level
        self.zoom_level = 0
        self.zoom_base = sqrt(2)

        self.mov_x = 0
        self.mov_y = 0
        # you move delta pixel regardless of zoom_level
        # when zooming the function will take care of leaving a fixed point
        self.mov_delta = 50 

        self.bind('<Configure>', self.do_resize)

        self.show_photo()

    def show_photo(self):
        print(f'frame {id(self)}')
        print(f'widget width {self.winfo_width()} height {self.winfo_height()}')
        print(f'widget x {self.winfo_x()} y {self.winfo_y()}')
        print(f'widget rootx {self.winfo_rootx()} rooty {self.winfo_rooty()}')
        current_photo = self.photo_list[self.photo_index]
        #  self.cur_image = Image.open(current_photo)
        #  cur_wid, cur_hei = self.cur_image.size
        cur_image = Image.open(current_photo)
        cur_wid, cur_hei = cur_image.size
        print(f'Current {basename(current_photo)} width {cur_wid} height {cur_hei}')

        zoom = self.zoom_base ** self.zoom_level
        zoom_wid = cur_wid * zoom
        zoom_hei = cur_hei * zoom
        print(f'zoom_level {self.zoom_level} zoom {zoom:.4f} zoom_wid {zoom_wid:.4f} zoom_hei {zoom_hei:.4f}')

        cur_image = ImageTk.PhotoImage(cur_image)
        self.image_label.image = cur_image
        self.image_label.configure(image=cur_image)
        self.image_label.place(x=-1, y=-1)
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

    def do_resize(self, e=None):
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
