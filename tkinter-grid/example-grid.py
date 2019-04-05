# all inspired by this https://stackoverflow.com/a/34277295
# other clear tutorials:
# http://stor.altervista.org/python/tk/tkinter.html
# https://python-forum.io/Thread-Tkinter-Getting-Tkinter-Grid-Sizing-Right-the-first-time
# more colors that you could ever use 
# http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter

import tkinter as tk

class InfoLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        # init Label, standard constructor
        self.var = tk.StringVar()
        self.var.set('Some text you should never see!')

        tk.Label.__init__(self, parent, textvariable=self.var, **kwargs)

        self.parent = parent

        # binding to the parent feels weird, bit it works
        self.parent.bind('<Configure>', self.update)

    def update(self, event):
        #  print(event)
        self.var.set(f'Width {event.width} height {event.height}')

class ResizableGrid(tk.Frame):
    def __init__(self, parent, **kwargs):
        # init Frame, standard constructor
        tk.Frame.__init__(self, parent, **kwargs)

        # tell row 1 (not 0) to expand (weight 1)
        # as it will be resized, set a minsize
        self.grid_rowconfigure(1, weight=1, minsize=60)
        self.grid_columnconfigure(0, weight=1)

        # create containers
        self.top_frame = tk.Frame(self, bg='light cyan', width=450, height=50, pady=3) # width will be ignored
        #  self.center = tk.Frame(self, bg='gray2', width=50, height=40, padx=3, pady=3)
        self.center = tk.Frame(self, bg='gray2', padx=3, pady=3)
        #  self.btm_frame = tk.Frame(self, bg='white', width=450, height=45, pady=3)
        self.btm_frame = tk.Frame(self, bg='white', height=45, pady=3)
        self.btm_frame2 = tk.Frame(self, bg='lavender', width=450, height=60, pady=3)

        # position them in the grid
        self.top_frame.grid(row=0, sticky="ew")
        self.center.grid(row=1, sticky="nsew") # the center one will grow in height too
        self.btm_frame.grid(row=3, sticky="ew")
        self.btm_frame2.grid(row=4, sticky="ew")

        # create the widgets for the top frame
        self.model_label = tk.Label(self.top_frame, text='Model Dimensions')
        self.width_label = tk.Label(self.top_frame, text='Width:')
        self.length_label = tk.Label(self.top_frame, text='Length:')
        self.entry_W = tk.Entry(self.top_frame, background="pink")
        self.entry_L = tk.Entry(self.top_frame, background="orange")

        # tell top_frame to let column 1 and 3 grow
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(3, weight=1)

        # layout the widgets in the top frame
        self.model_label.grid(row=0, columnspan=4)
        self.width_label.grid(row=1, column=0)
        self.length_label.grid(row=1, column=2)
        self.entry_W.grid(row=1, column=1, sticky='ew')
        self.entry_L.grid(row=1, column=3, sticky='ew')

        # tell center frame to let column 1 and 2 grow with different weights
        self.center.grid_rowconfigure(0, weight=1)
        self.center.grid_columnconfigure(1, weight=3)
        self.center.grid_columnconfigure(2, weight=1)

        # create widgets for the center frame
        self.ctr_left = tk.Frame(self.center, bg='blue', width=100, height=190)
        self.ctr_mid = tk.Frame(self.center, bg='yellow', width=250, height=190, padx=3, pady=3)
        self.ctr_right = tk.Frame(self.center, bg='green', width=100, height=190, padx=3, pady=3)

        self.ctr_left.grid(row=0, column=0, sticky="ns")
        self.ctr_mid.grid(row=0, column=1, sticky="nsew")
        # the *column* grows, the label doesn't
        self.ctr_right.grid(row=0, column=2, sticky="ns")


        # center label on ctr_mid
        self.ctr_mid.grid_columnconfigure(0, weight=1)
        self.ctr_mid.grid_rowconfigure(0, weight=1)

        #  self.lab1 = InfoLabel(self.ctr_mid, textvariable=var1)
        self.lab1 = InfoLabel(self.ctr_mid)
        self.lab1.grid(row=0, column=0)

class Application():
    def __init__(self):
        self.root = tk.Tk()

        self.root.bind('<Escape>', self.exit)

        self.width = 900
        self.height = 600
        self.xpos = 10
        self.ypos = 10
        #  self.root.geometry("900x600-5+5")
        # dimensiona e posiziona la finestra, - parte dal bordo destro
        self.root.geometry(f'{self.width}x{self.height}-{self.xpos}+{self.ypos}')

        # tell the grid in root to grow with the window
        # I don't know if there is any difference with the two ways
        #  self.root.columnconfigure(0, weight=1)
        #  self.root.rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # create a ResizableGrid which is a Frame
        # kwargs are sent to the Frame constructor
        #  self.gridexample = ResizableGrid(self.root, bg='cyan', padx=10) # no pad why?
        self.gridexample = ResizableGrid(self.root, bg='cyan')

        # pack the ResizableGrid and tell it to grow
        self.gridexample.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

    def start(self):
        self.root.mainloop()

    def exit(self, e=None):
        self.root.destroy()

class ApplicationDouble():
    def __init__(self):
        self.root = tk.Tk()

        self.root.bind('<Escape>', self.exit)

        self.width = 900
        self.height = 600
        self.xpos = 10
        self.ypos = 10
        #  self.root.geometry("900x600-5+5")
        # dimensiona e posiziona la finestra, - parte dal bordo destro
        self.root.geometry(f'{self.width}x{self.height}-{self.xpos}+{self.ypos}')

        # tell the grid in root to grow with the window
        # I don't know if there is any difference with the two ways
        #  self.root.columnconfigure(0, weight=1)
        #  self.root.rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # create a ResizableGrid which is a Frame
        # kwargs are sent to the Frame constructor
        #  self.gridexample = ResizableGrid(self.root, bg='cyan', padx=10) # no pad why?
        self.gridexample1 = ResizableGrid(self.root, bg='cyan')
        self.gridexample2 = ResizableGrid(self.root, bg='DarkOrange2')

        # pack the ResizableGrid and tell it to grow
        self.gridexample1.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.gridexample2.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

    def start(self):
        self.root.mainloop()

    def exit(self, e=None):
        self.root.destroy()

if __name__ == "__main__":
    #  srcdir = 'Selezione'
    #  app = Application()
    app = ApplicationDouble()
    app.start()


