from os import listdir
from os.path import abspath
from os.path import dirname
from os.path import join

#  import ray

from photo_viewer_app import PhotoViewerApp


def main():
    base_dir_name = "img"
    path_main = dirname(abspath(__file__))
    base_dir = join(path_main, base_dir_name)

    #  ray.init()

    app = PhotoViewerApp(base_dir)
    app.start()


if __name__ == "__main__":
    main()
